"""
Vector store service using ChromaDB.
Manages document and clause embeddings for RAG pipeline.
Per-workspace isolation for data separation.
"""
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from pathlib import Path
import hashlib

from src.services.embedding_service import EmbeddingService
from src.core.config import settings
from src.core.cache import cache_service


class VectorStore:
    """
    Vector store service using ChromaDB.
    
    Architecture:
    - Per-workspace collections for document chunks
    - Embeddings stored with metadata (workspace_id, document_id, page, section, chunk_id)
    - Supports semantic search with metadata filtering
    """
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize ChromaDB client.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_dir = Path(persist_directory or settings.chroma_persist_directory)
        self.persist_dir.mkdir(exist_ok=True, parents=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.embedding_service = EmbeddingService()
    
    def get_collection_name(self, workspace_id: str) -> str:
        """Get collection name for workspace"""
        return f"workspace_{workspace_id}"
    
    def get_or_create_collection(self, workspace_id: str):
        """Get or create collection for workspace"""
        collection_name = self.get_collection_name(workspace_id)
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            # Collection doesn't exist, create it
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"workspace_id": str(workspace_id)}
            )
        return collection
    
    def _clean_metadata(self, metadata: Dict) -> Dict:
        """
        Clean metadata to ensure ChromaDB compatibility.
        Removes None values and ensures all values are proper types.
        
        Args:
            metadata: Raw metadata dict
            
        Returns:
            Cleaned metadata dict with no None values
        """
        cleaned = {}
        for key, value in metadata.items():
            # Skip None values (ChromaDB doesn't allow them)
            if value is None:
                continue
            
            # Ensure proper types
            if isinstance(value, (str, int, float, bool)):
                cleaned[key] = value
            elif isinstance(value, (list, dict)):
                # Convert complex types to JSON string
                import json
                cleaned[key] = json.dumps(value)
            else:
                # Convert everything else to string
                cleaned[key] = str(value)
        
        return cleaned
    
    def index_document_chunks(
        self,
        workspace_id: str,
        document_id: str,
        document_name: str,
        chunks: List[Dict]
    ) -> int:
        """
        Index document chunks in vector store.
        
        Args:
            workspace_id: Workspace UUID
            document_id: Document UUID
            document_name: Document name
            chunks: List of chunks with text, page, section metadata
        
        Returns:
            Number of chunks indexed
        """
        if not chunks:
            return 0
        
        collection = self.get_or_create_collection(workspace_id)
        
        texts = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_text = chunk.get("text", "")
            if not chunk_text or not chunk_text.strip():
                continue
            
            texts.append(chunk_text)
            chunk_id = chunk.get("chunk_id", f"chunk_{document_id}_{i}")
            ids.append(chunk_id)
            
            # Store coordinates if available
            coordinates = chunk.get("coordinates")
            coordinates_str = None
            if coordinates:
                # Store as JSON string (ChromaDB metadata must be strings/numbers)
                import json
                coordinates_str = json.dumps(coordinates)
            
            # Build metadata dict, filtering out None values (ChromaDB doesn't allow None)
            metadata = {
                "workspace_id": str(workspace_id),
                "document_id": str(document_id),
                "document_name": str(document_name) if document_name else "",
                "page_number": int(chunk.get("page_number", 0)),
                "section_name": str(chunk.get("section_name", "")),
                "chunk_type": str(chunk.get("chunk_type", "chunk")),
                "type": "chunk",  # For filtering chunks vs clauses
            }
            
            # Only add coordinates if they exist (ChromaDB doesn't allow None)
            if coordinates_str:
                metadata["coordinates"] = str(coordinates_str)
            
            # Clean metadata to ensure no None values and proper types
            cleaned_metadata = self._clean_metadata(metadata)
            metadatas.append(cleaned_metadata)
        
        if not texts:
            return 0
        
        # Generate embeddings
        embeddings = self.embedding_service.get_embeddings_batch(texts)
        
        # Filter out None embeddings
        valid_data = [
            (text, metadata, embedding, id_val)
            for text, metadata, embedding, id_val in zip(texts, metadatas, embeddings, ids)
            if embedding is not None
        ]
        
        if not valid_data:
            return 0
        
        # Add to collection
        collection.add(
            embeddings=[item[2] for item in valid_data],
            documents=[item[0] for item in valid_data],
            metadatas=[item[1] for item in valid_data],
            ids=[item[3] for item in valid_data]
        )
        
        return len(valid_data)
    
    def search(
        self,
        workspace_id: str,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None,
        include_clauses: bool = True,
        include_chunks: bool = True
    ) -> List[Dict]:
        """
        Search for relevant documents/chunks/clauses.
        
        Args:
            workspace_id: Workspace UUID
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {"document_id": "..."})
            include_clauses: Whether to include clause results
            include_chunks: Whether to include chunk results
        
        Returns:
            List of search results with document text, metadata, and score
        """
        # Build cache key
        filter_str = str(sorted(filter_metadata.items())) if filter_metadata else ""
        cache_key_parts = [
            "vector_search",
            workspace_id,
            hashlib.sha256(query.encode()).hexdigest()[:16],
            str(n_results),
            str(include_clauses),
            str(include_chunks),
            hashlib.sha256(filter_str.encode()).hexdigest()[:8]
        ]
        cache_key = ":".join(cache_key_parts)
        
        # Try cache first
        cached = cache_service.get(cache_key)
        if cached is not None:
            return cached
        
        collection = self.get_or_create_collection(workspace_id)
        
        # Get query embedding (this will use embedding cache)
        query_embedding = self.embedding_service.get_embedding(query)
        if not query_embedding:
            return []
        
        # Build where clause for filtering
        where = {}
        if filter_metadata:
            where.update(filter_metadata)
        
        # Filter by type if needed
        if not include_clauses and include_chunks:
            where["type"] = "chunk"
        elif not include_chunks and include_clauses:
            where["type"] = "clause"
        # If both are True, don't filter by type
        
        # Query collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where if where else None,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results["documents"] and len(results["documents"]) > 0:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 1.0
                
                # Convert distance to similarity score
                # ChromaDB uses cosine distance: 0 = identical, 2 = opposite
                # For cosine similarity: similarity = 1 - distance (but can be negative)
                # Normalize to ensure we handle negative values correctly
                similarity_score = 1.0 - distance
                
                # Store both raw score and normalized score
                formatted_results.append({
                    "text": doc,
                    "metadata": metadata,
                    "score": similarity_score,  # Can be negative for cosine distance
                    "distance": distance,  # Keep original distance for reference
                    "page_number": metadata.get("page_number", 0),
                    "section_name": metadata.get("section_name", ""),
                    "document_id": metadata.get("document_id", ""),
                    "document_name": metadata.get("document_name", "")
                })
        
        # Cache results
        cache_service.set(cache_key, formatted_results, ttl=settings.cache_vector_search_ttl)
        
        return formatted_results
    
    def delete_document(self, workspace_id: str, document_id: str) -> bool:
        """
        Delete all chunks/clauses for a document.
        
        Args:
            workspace_id: Workspace UUID
            document_id: Document UUID
        
        Returns:
            True if successful
        """
        collection = self.get_or_create_collection(workspace_id)
        collection.delete(where={"document_id": document_id})
        return True
    
    def delete_workspace(self, workspace_id: str) -> bool:
        """
        Delete entire workspace collection.
        
        Args:
            workspace_id: Workspace UUID
        
        Returns:
            True if successful
        """
        collection_name = self.get_collection_name(workspace_id)
        try:
            self.client.delete_collection(name=collection_name)
            return True
        except Exception:
            return False


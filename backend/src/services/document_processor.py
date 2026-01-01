"""
Document processing service using PyMuPDF and LLM for intelligent structuring.

This service:
1. Extracts text and coordinates from PDF/DOCX using PyMuPDF
2. Uses LLM (via instructor) to intelligently structure the document:
   - Section detection with page numbers
   - Semantic chunking (complete clauses/thoughts)
   - Metadata extraction
3. Returns structured data ready for clause extraction and RAG
"""
import fitz  # PyMuPDF
from docx import Document as DocxDocument
from pathlib import Path
from typing import List, Dict, Optional
import re
from openai import OpenAI
from instructor import patch
from pydantic import BaseModel, Field

from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class DocumentSection(BaseModel):
    """Document section identified by LLM"""
    section_name: str = Field(description="Name of the section (e.g., 'TERMINATION', 'LIABILITY')")
    page_number: int = Field(description="Page number where section starts")
    start_char: int = Field(description="Character position in full text where section starts")
    end_char: int = Field(description="Character position in full text where section ends")
    content: str = Field(description="Full text content of the section")


class DocumentChunk(BaseModel):
    """Semantic chunk of document text"""
    chunk_id: str = Field(description="Unique identifier for the chunk")
    text: str = Field(description="Complete text of the chunk (should be a complete semantic unit)")
    page_number: int = Field(description="Page number where chunk appears")
    section_name: str = Field(description="Section name this chunk belongs to")
    chunk_type: str = Field(
        default="clause",
        description="Type of chunk: 'clause', 'definition', 'header', 'table', etc."
    )
    context_before: str = Field(
        default="",
        description="Preceding text for context (helps with understanding)"
    )
    context_after: str = Field(
        default="",
        description="Following text for context (helps with understanding)"
    )
    coordinates: Optional[Dict] = Field(
        default=None,
        description="Bounding box coordinates for text highlighting: {x0, y0, x1, y1}"
    )


class DocumentStructure(BaseModel):
    """Complete document structure as analyzed by LLM"""
    sections: List[DocumentSection] = Field(description="All major sections identified in the document")
    chunks: List[DocumentChunk] = Field(
        description="Semantic chunks - each should be a complete thought/clause, not arbitrary splits"
    )
    metadata: Dict = Field(
        default_factory=dict,
        description="Document metadata (document type, parties, dates, etc.)"
    )
    contract_type_hints: List[str] = Field(
        default_factory=list,
        description="Hints about contract type (e.g., 'vendor_procurement', 'saas_technology')"
    )


class DocumentProcessor:
    """
    Document processing service using PyMuPDF + LLM for intelligent structuring.
    
    Process flow:
    1. PyMuPDF extracts raw text + coordinates (accurate, preserves layout)
    2. LLM analyzes and structures the document intelligently
    3. Returns structured data ready for clause extraction and RAG
    """
    
    def __init__(self):
        """Initialize document processor"""
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY in environment.")
        
        self.client = patch(OpenAI(api_key=settings.openai_api_key))
        self.detected_contract_type: Optional[str] = None
    
    def process_pdf(self, file_path: str) -> Dict:
        """
        Process PDF document.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dict with:
                - page_count: Number of pages
                - full_text: Complete extracted text
                - pages: List of page data with text and coordinates
                - sections: List of sections with page numbers
                - chunks: List of semantic chunks
                - metadata: Document metadata
                - contract_type_hints: Contract type hints
        """
        doc = fitz.open(file_path)
        
        # Extract text and coordinates from each page
        pages_data = []
        full_text_parts = []
        page_text_map = {}  # Map page number to text for context
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # Get text blocks with coordinates for highlighting
            blocks = page.get_text("dict")
            text_blocks = []
            for block in blocks.get("blocks", []):
                if "lines" in block:  # Text block
                    block_text = " ".join(
                        " ".join(span.get("text", "") for span in line.get("spans", []))
                        for line in block.get("lines", [])
                    )
                    if block_text.strip():
                        bbox = block.get("bbox", [0, 0, 0, 0])
                        text_blocks.append({
                            "text": block_text,
                            "bbox": bbox,
                            "page": page_num + 1
                        })
            
            pages_data.append({
                "page_number": page_num + 1,
                "text": text,
                "blocks": text_blocks
            })
            
            full_text_parts.append(text)
            page_text_map[page_num + 1] = text
        
        full_text = "\n\n".join(full_text_parts)
        page_count = len(doc)
        doc.close()
        
        # Use LLM to structure the document intelligently
        structure = self._structure_with_llm(full_text, page_text_map)
        
        # Post-processing validation: Ensure all pages are covered
        pages_with_chunks = set(chunk.page_number for chunk in structure.chunks)
        all_pages = set(page_text_map.keys())
        missing_pages = all_pages - pages_with_chunks
        
        # If pages are missing, add fallback chunks for those pages
        if missing_pages:
            logger.warning(
                f"LLM did not process pages {sorted(missing_pages)}. Adding fallback chunks.",
                extra={"missing_pages": sorted(missing_pages)}
            )
            for page_num in sorted(missing_pages):
                page_text = page_text_map[page_num]
                if page_text.strip():
                    fallback_chunks = self._create_fallback_chunks_for_page(
                        page_num, page_text, structure.chunks
                    )
                    structure.chunks.extend(fallback_chunks)
        
        # Extract coordinates for chunks
        structure.chunks = self._extract_chunk_coordinates(file_path, structure.chunks, pages_data)
        
        # Update detected contract type
        if structure.contract_type_hints:
            self.detected_contract_type = structure.contract_type_hints[0]
        
        return {
            "page_count": page_count,
            "full_text": full_text,
            "pages": pages_data,
            "sections": [section.model_dump() for section in structure.sections],
            "chunks": [chunk.model_dump() for chunk in structure.chunks],
            "metadata": structure.metadata,
            "contract_type_hints": structure.contract_type_hints
        }
    
    def process_docx(self, file_path: str) -> Dict:
        """
        Process DOCX document.
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Same structure as process_pdf
        """
        doc = DocxDocument(file_path)
        
        # Extract text from DOCX
        pages_data = []
        full_text_parts = []
        page_text_map = {}
        
        # DOCX doesn't have explicit pages, so we'll simulate pages
        # by grouping paragraphs (rough approximation)
        paragraphs = doc.paragraphs
        current_page = 1
        current_page_text = []
        chars_per_page = 2000  # Approximate characters per page
        
        for para in paragraphs:
            text = para.text.strip()
            if text:
                current_page_text.append(text)
                full_text_parts.append(text)
                
                # If we've accumulated enough text, consider it a new page
                if sum(len(p) for p in current_page_text) >= chars_per_page:
                    page_text = "\n".join(current_page_text)
                    pages_data.append({
                        "page_number": current_page,
                        "text": page_text,
                        "blocks": [{"text": page_text, "bbox": None, "page": current_page}]
                    })
                    page_text_map[current_page] = page_text
                    current_page += 1
                    current_page_text = []
        
        # Add remaining text as last page
        if current_page_text:
            page_text = "\n".join(current_page_text)
            pages_data.append({
                "page_number": current_page,
                "text": page_text,
                "blocks": [{"text": page_text, "bbox": None, "page": current_page}]
            })
            page_text_map[current_page] = page_text
        
        full_text = "\n\n".join(full_text_parts)
        page_count = len(pages_data) if pages_data else 1
        
        # Use LLM to structure the document
        structure = self._structure_with_llm(full_text, page_text_map)
        
        # Post-processing validation: Ensure all pages are covered (for DOCX too)
        pages_with_chunks = set(chunk.page_number for chunk in structure.chunks)
        all_pages = set(page_text_map.keys())
        missing_pages = all_pages - pages_with_chunks
        
        # If pages are missing, add fallback chunks for those pages
        if missing_pages:
            logger.warning(
                f"LLM did not process pages {sorted(missing_pages)}. Adding fallback chunks.",
                extra={"missing_pages": sorted(missing_pages)}
            )
            for page_num in sorted(missing_pages):
                page_text = page_text_map[page_num]
                if page_text.strip():
                    fallback_chunks = self._create_fallback_chunks_for_page(
                        page_num, page_text, structure.chunks
                    )
                    structure.chunks.extend(fallback_chunks)
        
        # Update detected contract type
        if structure.contract_type_hints:
            self.detected_contract_type = structure.contract_type_hints[0]
        
        return {
            "page_count": page_count,
            "full_text": full_text,
            "pages": pages_data,
            "sections": [section.model_dump() for section in structure.sections],
            "chunks": [chunk.model_dump() for chunk in structure.chunks],
            "metadata": structure.metadata,
            "contract_type_hints": structure.contract_type_hints
        }
    
    def _structure_with_llm(self, full_text: str, page_text_map: Dict[int, str]) -> DocumentStructure:
        """
        Use LLM to intelligently structure the document.
        
        Args:
            full_text: Complete document text
            page_text_map: Map of page numbers to page text
            
        Returns:
            DocumentStructure with sections, chunks, and metadata
        """
        # Truncate if too long (LLM context limits)
        max_chars = 200000  # ~50K tokens, safe for GPT-4o-mini
        if len(full_text) > max_chars:
            # Rebuild full_text and page_text_map with truncation
            accumulated = 0
            new_page_map = {}
            new_full_text_parts = []
            
            for page_num in sorted(page_text_map.keys()):
                page_text = page_text_map[page_num]
                if accumulated + len(page_text) <= max_chars:
                    new_page_map[page_num] = page_text
                    new_full_text_parts.append(page_text)
                    accumulated += len(page_text) + 2  # +2 for "\n\n"
                else:
                    remaining = max_chars - accumulated
                    if remaining > 0:
                        truncated_text = page_text[:remaining]
                        new_page_map[page_num] = truncated_text
                        new_full_text_parts.append(truncated_text)
                    break
            
            full_text = "\n\n".join(new_full_text_parts)
            page_text_map = new_page_map
        
        # Build context for LLM about page boundaries
        page_boundaries = []
        char_pos = 0
        for page_num in sorted(page_text_map.keys()):
            page_text = page_text_map[page_num]
            page_boundaries.append({
                "page": page_num,
                "start": char_pos,
                "end": char_pos + len(page_text)
            })
            char_pos += len(page_text) + 2  # +2 for "\n\n"
        
        system_prompt = """You are a document analysis expert. Analyze this contract document and extract:

1. **Sections**: Identify all major sections (e.g., TERMINATION, LIABILITY, PAYMENT TERMS, etc.) with their page numbers and character positions in the text.

2. **Semantic Chunks**: Break the text into semantic chunks. Each chunk should be a COMPLETE semantic unit:
   - A complete clause (not split mid-sentence)
   - A complete definition
   - A complete paragraph with full meaning
   - Do NOT create arbitrary fixed-size chunks
   - Preserve context - each chunk should make sense on its own
   - **CRITICAL**: You MUST create chunks for ALL pages, even if content appears similar or duplicate
   - **CRITICAL**: Do NOT skip any pages - every page must have at least one chunk

3. **Metadata**: Extract document metadata:
   - Document type (e.g., "SaaS Agreement", "Vendor Contract")
   - Parties involved (if mentioned)
   - Key dates
   - Any other relevant metadata

4. **Contract Type Hints**: Identify what type of contract this appears to be:
   - vendor_procurement
   - service_agreement
   - saas_technology
   - government_contract
   - employment
   - generic

Be precise with page numbers and character positions. Each chunk should reference the correct page number based on where that text appears in the document. Ensure you process every single page of the document."""

        # Get total page count for validation
        total_pages = len(page_text_map)
        page_numbers = sorted(page_text_map.keys())
        
        user_prompt = f"""Analyze this contract document:

{full_text}

Page boundaries (character positions):
{page_boundaries}

**IMPORTANT**: This document has {total_pages} pages (pages {min(page_numbers)} to {max(page_numbers)}). 
You MUST create chunks for ALL {total_pages} pages. Do not skip any pages, even if they contain similar content.

Extract sections, create semantic chunks, and provide metadata."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_model=DocumentStructure,
                temperature=0.1,  # Low temperature for consistency
            )
            
            structure = response.model_dump()
            structure_obj = DocumentStructure(**structure)
            
            # Post-processing validation: Ensure all pages are covered
            pages_with_chunks = set(chunk.page_number for chunk in structure_obj.chunks)
            all_pages = set(page_text_map.keys())
            missing_pages = all_pages - pages_with_chunks
            
            # If pages are missing, add fallback chunks for those pages
            if missing_pages:
                logger.warning(
                    f"LLM did not process pages {sorted(missing_pages)}. Adding fallback chunks.",
                    extra={"missing_pages": sorted(missing_pages)}
                )
                for page_num in sorted(missing_pages):
                    page_text = page_text_map[page_num]
                    if page_text.strip():
                        # Create fallback chunks for missing pages
                        fallback_chunks = self._create_fallback_chunks_for_page(
                            page_num, page_text, structure_obj.chunks
                        )
                        structure_obj.chunks.extend(fallback_chunks)
            
            return structure_obj
            
        except Exception as e:
            # Fallback: Create basic structure if LLM fails
            # Split into pages as chunks
            chunks = []
            for page_num, page_text in page_text_map.items():
                # Simple sentence-based chunking as fallback
                sentences = re.split(r'(?<=[.!?])\s+', page_text)
                current_chunk = ""
                chunk_num = 0
                
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) < 1000:  # Max chunk size
                        current_chunk += sentence + " "
                    else:
                        if current_chunk.strip():
                            chunks.append(DocumentChunk(
                                chunk_id=f"chunk_{page_num}_{chunk_num}",
                                text=current_chunk.strip(),
                                page_number=page_num,
                                section_name="Unknown",
                                chunk_type="clause",
                                context_before="",
                                context_after=""
                            ))
                            chunk_num += 1
                        current_chunk = sentence + " "
                
                # Add remaining chunk
                if current_chunk.strip():
                    chunks.append(DocumentChunk(
                        chunk_id=f"chunk_{page_num}_{chunk_num}",
                        text=current_chunk.strip(),
                        page_number=page_num,
                        section_name="Unknown",
                        chunk_type="clause",
                        context_before="",
                        context_after=""
                    ))
            
            return DocumentStructure(
                sections=[],
                chunks=chunks,
                metadata={"error": str(e)},
                contract_type_hints=[]
            )
    
    def _create_fallback_chunks_for_page(
        self, 
        page_num: int, 
        page_text: str, 
        existing_chunks: List[DocumentChunk]
    ) -> List[DocumentChunk]:
        """
        Create fallback chunks for a page that was missed by LLM.
        Uses intelligent chunking: detects clause markers, then sentence-based splitting.
        
        Args:
            page_num: Page number
            page_text: Text content of the page
            existing_chunks: Existing chunks to infer section context from
        
        Returns:
            List of DocumentChunk objects
        """
        chunks = []
        
        # Try to infer section name from nearby pages
        section_name = "Unknown"
        for chunk in existing_chunks:
            if abs(chunk.page_number - page_num) <= 1:
                section_name = chunk.section_name
                break
        
        # First, try to split by clause markers (A., B., C., etc. or numbered lists)
        # Pattern: Letter/number followed by period and space (e.g., "B. ", "1. ", "A. ")
        # Look for patterns like "B. ", "C. ", "1. " at start of line or after whitespace
        clause_marker_pattern = r'(\n\s*|^)([A-Z]\.\s+|\d+\.\s+)'
        
        # Find all clause markers and their positions
        matches = list(re.finditer(clause_marker_pattern, page_text))
        
        # If we found clause markers, split by them
        if len(matches) >= 2:  # Need at least 2 markers to split
            clause_parts = []
            last_pos = 0
            
            # First part (before first marker)
            if matches[0].start() > 0:
                first_text = page_text[:matches[0].start()].strip()
                if first_text:
                    clause_parts.append(("", first_text))
            
            # Process each clause
            for i, match in enumerate(matches):
                marker = match.group(2).strip()  # The actual marker (B., C., etc.)
                start_pos = match.end()
                # End position is start of next marker, or end of text
                end_pos = matches[i+1].start() if i+1 < len(matches) else len(page_text)
                clause_text = page_text[start_pos:end_pos].strip()
                
                if clause_text:
                    clause_parts.append((marker, clause_text))
            
            # If no markers found, clause_parts will be empty, fall through to sentence-based
            if not clause_parts:
                matches = []
            
            # Create chunks from clause parts
            if clause_parts:
                for chunk_num, (marker, clause_text) in enumerate(clause_parts):
                    # Further split if clause is too long (by sentences)
                    if len(clause_text) > 1500:
                        sentences = re.split(r'(?<=[.!?])\s+', clause_text)
                        current_subchunk = ""
                        subchunk_num = 0
                        
                        for sentence in sentences:
                            sentence = sentence.strip()
                            if not sentence:
                                continue
                            
                            if len(current_subchunk) + len(sentence) > 1500:
                                if current_subchunk.strip():
                                    chunks.append(DocumentChunk(
                                        chunk_id=f"chunk_{page_num}_{chunk_num}_{subchunk_num}",
                                        text=current_subchunk.strip(),
                                        page_number=page_num,
                                        section_name=section_name,
                                        chunk_type="clause",
                                        context_before="",
                                        context_after=""
                                    ))
                                    subchunk_num += 1
                                current_subchunk = sentence + " "
                            else:
                                current_subchunk += sentence + " "
                        
                        if current_subchunk.strip():
                            chunks.append(DocumentChunk(
                                chunk_id=f"chunk_{page_num}_{chunk_num}_{subchunk_num}",
                                text=current_subchunk.strip(),
                                page_number=page_num,
                                section_name=section_name,
                                chunk_type="clause",
                                context_before="",
                                context_after=""
                            ))
                    else:
                        # Clause is reasonable size, use as-is
                        chunks.append(DocumentChunk(
                            chunk_id=f"chunk_{page_num}_{chunk_num}",
                            text=clause_text,
                            page_number=page_num,
                            section_name=section_name,
                            chunk_type="clause",
                            context_before="",
                            context_after=""
                        ))
                return chunks
        else:
            # No clause markers found, use sentence-based chunking
            sentences = re.split(r'(?<=[.!?])\s+', page_text)
            current_chunk = ""
            chunk_num = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # If adding this sentence would exceed reasonable chunk size, finalize current chunk
                if len(current_chunk) + len(sentence) > 1500:  # Max chunk size
                    if current_chunk.strip():
                        chunks.append(DocumentChunk(
                            chunk_id=f"chunk_{page_num}_{chunk_num}",
                            text=current_chunk.strip(),
                            page_number=page_num,
                            section_name=section_name,
                            chunk_type="clause",
                            context_before="",
                            context_after=""
                        ))
                        chunk_num += 1
                    current_chunk = sentence + " "
                else:
                    current_chunk += sentence + " "
            
            # Add remaining chunk
            if current_chunk.strip():
                chunks.append(DocumentChunk(
                    chunk_id=f"chunk_{page_num}_{chunk_num}",
                    text=current_chunk.strip(),
                    page_number=page_num,
                    section_name=section_name,
                    chunk_type="clause",
                    context_before="",
                    context_after=""
                ))
        
        return chunks
    
    def _extract_chunk_coordinates(
        self, 
        file_path: str, 
        chunks: List[DocumentChunk],
        pages_data: List[Dict]
    ) -> List[DocumentChunk]:
        """
        Extract coordinates for chunks from PDF.
        
        Args:
            file_path: Path to PDF file
            chunks: List of DocumentChunk objects
            pages_data: List of page data with blocks and coordinates
            
        Returns:
            List of DocumentChunk objects with coordinates populated
        """
        try:
            doc = fitz.open(file_path)
            updated_chunks = []
            
            for chunk in chunks:
                if chunk.coordinates is not None:
                    # Already has coordinates
                    updated_chunks.append(chunk)
                    continue
                
                # Try to find coordinates for this chunk
                page_num = chunk.page_number
                if page_num > len(doc):
                    updated_chunks.append(chunk)
                    continue
                
                page = doc[page_num - 1]
                # Search for the chunk text (first 100 chars for efficiency)
                search_text = chunk.text[:100].strip()
                if not search_text:
                    updated_chunks.append(chunk)
                    continue
                
                # Find text instances
                text_instances = page.search_for(search_text)
                
                if text_instances:
                    # Use first match's coordinates
                    bbox = text_instances[0]
                    chunk.coordinates = {
                        "x0": float(bbox.x0),
                        "y0": float(bbox.y0),
                        "x1": float(bbox.x1),
                        "y1": float(bbox.y1),
                        "page": page_num
                    }
                
                updated_chunks.append(chunk)
            
            doc.close()
            return updated_chunks
            
        except Exception as e:
            logger.error(f"Error extracting coordinates: {e}", exc_info=True)
            return chunks
    
    def get_page_coordinates(self, file_path: str, page_number: int, text_snippet: str) -> Optional[Dict]:
        """
        Get coordinates for text snippet on a specific page (for PDF highlighting).
        
        Args:
            file_path: Path to PDF file
            page_number: Page number (1-indexed)
            text_snippet: Text to find coordinates for
            
        Returns:
            Dict with bbox coordinates or None if not found
        """
        try:
            doc = fitz.open(file_path)
            if page_number > len(doc):
                doc.close()
                return None
            
            page = doc[page_number - 1]
            text_instances = page.search_for(text_snippet[:100])  # Search for first 100 chars
            
            if text_instances:
                # Return first match's coordinates
                bbox = text_instances[0]
                doc.close()
                return {
                    "x0": bbox.x0,
                    "y0": bbox.y0,
                    "x1": bbox.x1,
                    "y1": bbox.y1,
                    "page": page_number
                }
            
            doc.close()
            return None
            
        except Exception:
            return None


"""
RAG Pipeline using LangGraph for Q&A with citations.

This service implements:
1. Retrieve node: Vector search for relevant chunks
2. Generate node: LLM answer generation with citations
3. Conversation state management
"""
from typing import List, Dict, Optional, TypedDict, Annotated
from operator import add
from openai import OpenAI
from instructor import patch
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field, field_validator
import operator
import re

from src.core.config import settings
from src.core.logging_config import get_logger
from src.services.vector_store import VectorStore

logger = get_logger(__name__)


class Citation(BaseModel):
    """Citation for a source chunk"""
    document_id: str = Field(description="Document ID")
    document_name: str = Field(description="Document name")
    page_number: int = Field(description="Page number")
    section_name: str = Field(description="Section name")
    text_excerpt: str = Field(description="Excerpt from the source")
    similarity_score: float = Field(description="Similarity score (0-1)")
    chunk_id: Optional[str] = Field(default=None, description="Chunk ID")
    coordinates: Optional[Dict] = Field(
        default=None,
        description="Bounding box coordinates for highlighting: {x0, y0, x1, y1, page}"
    )


class StructuredAnswer(BaseModel):
    """Structured answer with validated citations - ensures high accuracy"""
    answer: str = Field(
        description="Complete answer to the question based on provided sources"
    )
    cited_sources: List[int] = Field(
        description="List of source numbers (1-based) that were used to generate this answer. "
        "ONLY include source numbers that exist in the provided sources (1 to number of sources). "
        "Do NOT include invalid source numbers. Each number must be >= 1."
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        default=0.0,
        description="Confidence score (0.0-1.0) for the answer accuracy"
    )
    answer_notes: Optional[str] = Field(
        default=None,
        description="Any notes about the answer (e.g., limitations, assumptions)"
    )

    @field_validator('cited_sources')
    @classmethod
    def validate_cited_sources(cls, v: List[int]) -> List[int]:
        """Validate that all source numbers are >= 1"""
        if not v:
            return v
        invalid = [s for s in v if s < 1]
        if invalid:
            raise ValueError(f"Source numbers must be >= 1, got: {invalid}")
        return v


class Message(BaseModel):
    """Conversation message"""
    role: str = Field(description="Message role: 'user' or 'assistant'")
    content: str = Field(description="Message content")
    citations: Optional[List[Citation]] = Field(
        default=None, description="Citations for assistant messages")


class ContractIQState(TypedDict):
    """State schema for RAG pipeline"""
    question: str
    workspace_id: str
    document_ids: Optional[List[str]]  # Optional: filter to specific documents
    conversation_history: Annotated[List[Dict],
                                    operator.add]  # Accumulated messages
    retrieved_chunks: List[Dict]  # Chunks from vector search
    answer: str
    citations: List[Citation]
    error: Optional[str]


class RAGPipeline:
    """
    RAG Pipeline using LangGraph.

    Flow:
    1. Retrieve: Vector search for relevant chunks
    2. Generate: LLM generates answer with citations
    3. Return: Answer with citations
    """

    def __init__(self):
        """Initialize RAG pipeline"""
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")

        self.client = patch(OpenAI(api_key=settings.openai_api_key))
        self.vector_store = VectorStore()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(ContractIQState)

        # Add nodes
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("generate", self._generate_node)

        # Define edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()

    def _retrieve_node(self, state: ContractIQState) -> ContractIQState:
        """
        Retrieve relevant chunks from vector store.

        Args:
            state: Current state with question

        Returns:
            Updated state with retrieved_chunks
        """
        question = state["question"].strip()
        workspace_id = state["workspace_id"]
        document_ids = state.get("document_ids")

        # Fast pre-classification: Check if question is a simple greeting or off-topic
        # This avoids unnecessary retrieval and improves response time
        question_lower = question.lower().strip()
        simple_greetings = ["hi", "hello", "hey", "greetings",
                            "good morning", "good afternoon", "good evening"]

        # Check for simple greetings (exact match or very short)
        if question_lower in simple_greetings or (len(question_lower) <= 3 and question_lower in ["hi", "hey"]):
            # Return empty chunks - generate node will handle greeting response
            return {
                **state,
                "retrieved_chunks": [],
                "error": None
            }

        # Build filter metadata
        filter_metadata = {}
        if document_ids:
            # If specific documents requested, filter by document_id
            # Note: ChromaDB where clause supports OR, but we'll search all and filter
            pass  # We'll filter after retrieval for simplicity

        # Search vector store for actual questions
        n_results = 10  # Get top 10 chunks
        results = self.vector_store.search(
            workspace_id=workspace_id,
            query=question,
            n_results=n_results,
            filter_metadata=filter_metadata if filter_metadata else None,
            include_clauses=True,
            include_chunks=True
        )

        # Filter by document_ids if specified
        if document_ids:
            results = [
                r for r in results
                if r.get("document_id") in document_ids
            ]

        # Filter by minimum similarity threshold (remove very low relevance chunks)
        # Keep chunks with similarity > -0.3, or top 5 if all are below threshold
        MIN_SIMILARITY_THRESHOLD = -0.3
        filtered_results = [r for r in results if r.get(
            "score", -1.0) > MIN_SIMILARITY_THRESHOLD]

        # If filtering removed all results, use top 5 by score
        if not filtered_results:
            filtered_results = sorted(results, key=lambda x: x.get(
                "score", -1.0), reverse=True)[:5]
        else:
            # Sort by score and take top 5
            filtered_results = sorted(filtered_results, key=lambda x: x.get(
                "score", -1.0), reverse=True)[:5]

        results = filtered_results

        return {
            **state,
            "retrieved_chunks": results,
            "error": None
        }

    def _generate_node(self, state: ContractIQState) -> ContractIQState:
        """
        Generate answer using LLM with retrieved chunks.

        Args:
            state: Current state with retrieved_chunks

        Returns:
            Updated state with answer and citations
        """
        question = state["question"]
        retrieved_chunks = state.get("retrieved_chunks", [])
        conversation_history = state.get("conversation_history", [])

        # If no chunks retrieved, use LLM to intelligently determine response type
        if not retrieved_chunks:
            try:
                # Use LLM to classify the question type
                classification_response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "Classify the user's message into one category:\n- 'greeting' - casual greetings (hi, hello, hey, etc.)\n- 'needs_context' - questions about contracts that need document context\n- 'off_topic' - questions not related to contracts\n\nRespond with ONLY the category name."
                        },
                        {
                            "role": "user",
                            "content": question
                        }
                    ],
                    max_tokens=10,
                    temperature=0
                )

                classification = classification_response.choices[0].message.content.strip(
                ).lower()

                if "greeting" in classification:
                    return {
                        **state,
                        "answer": "Hello! I'm here to help you understand your contracts. You can ask me questions like:\n\n• What are the termination terms?\n• What is the liability cap?\n• What are the payment terms?\n• Explain the confidentiality clause\n\nWhat would you like to know about your contracts?",
                        "citations": [],
                        "error": None
                    }
                elif "off_topic" in classification:
                    return {
                        **state,
                        "answer": "I'm specialized in helping with contract analysis. Please ask me questions about your uploaded contracts, such as terms, clauses, liability, payment terms, etc.",
                        "citations": [],
                        "error": None
                    }
                else:
                    # Needs context but no chunks found
                    return {
                        **state,
                        "answer": "I couldn't find any relevant information to answer your question. Please try rephrasing your question or make sure you have documents uploaded in your workspace.",
                        "citations": [],
                        "error": "No relevant chunks found"
                    }
            except Exception as e:
                # Fallback if classification fails
                return {
                    **state,
                    "answer": "I couldn't find any relevant information to answer your question. Please try rephrasing your question or make sure you have documents uploaded in your workspace.",
                    "citations": [],
                    "error": "No relevant chunks found"
                }

        # Build context from retrieved chunks
        context_parts = []
        citations_data = []

        for i, chunk in enumerate(retrieved_chunks, 1):
            text = chunk.get("text", "")
            metadata = chunk.get("metadata", {})
            score = chunk.get("score", 0.0)

            context_parts.append(
                f"[Source {i}]\n"
                f"Document: {metadata.get('document_name', 'Unknown')}\n"
                f"Page: {metadata.get('page_number', '?')}\n"
                f"Section: {metadata.get('section_name', 'Unknown')}\n"
                f"Content: {text}\n"
            )

            # Parse coordinates from metadata if available
            coordinates = None
            coordinates_str = metadata.get("coordinates")
            if coordinates_str:
                try:
                    import json
                    coordinates = json.loads(coordinates_str)
                except Exception:
                    pass

            citations_data.append(Citation(
                document_id=metadata.get("document_id", ""),
                document_name=metadata.get("document_name", "Unknown"),
                page_number=metadata.get("page_number", 0),
                section_name=metadata.get("section_name", "Unknown"),
                text_excerpt=text[:500],  # First 500 chars
                similarity_score=score,
                chunk_id=metadata.get("chunk_id"),
                coordinates=coordinates
            ))

        context = "\n\n".join(context_parts)

        # Build conversation history for context
        history_text = ""
        if conversation_history:
            history_parts = []
            # Last 4 messages for context
            for msg in conversation_history[-4:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_parts.append(f"{role.capitalize()}: {content}")
            history_text = "\n".join(history_parts)

        # Build prompt for structured output
        num_sources = len(citations_data)
        system_prompt = f"""You are an experienced contract attorney providing legal analysis. Answer questions about contracts using ONLY the provided source material.

CRITICAL: You have been provided with EXACTLY {num_sources} sources, numbered 1 to {num_sources}.

STYLE AND TONE:
- Answer like a lawyer: professional, precise, and direct
- Be concise: go straight to the point, avoid unnecessary verbosity
- Be practical: focus on what matters for contract analysis
- Use clear, professional language without being overly formal
- Structure your answer logically (use bullet points or numbered lists when helpful)
- Preserve proper paragraph breaks and spacing in your response
- Format markdown properly: use **bold** for emphasis, preserve line breaks between paragraphs

INSTRUCTIONS:
1. Answer the question based ONLY on the provided sources
2. In the cited_sources field, list ONLY the source numbers (1-based) that you actually used
3. IMPORTANT: cited_sources can ONLY contain numbers from 1 to {num_sources}
4. Do NOT include any number greater than {num_sources} in cited_sources
5. Do NOT include any number less than 1 in cited_sources
6. Be precise and accurate - cite specific clauses, page numbers, and sections
7. Include specific details from sources (exact terms, numbers, dates, conditions)
8. If the answer requires multiple points, use bullet points or numbered lists
9. If information is not in the sources, state that clearly

VALIDATION RULES:
- cited_sources must ONLY contain integers between 1 and {num_sources} (inclusive)
- If you see "Source 5" but only {num_sources} sources exist, DO NOT include 5
- Each number in cited_sources must be >= 1 and <= {num_sources}
- Set confidence based on how certain you are (0.0-1.0)

EXAMPLES OF GOOD ANSWERS:
- "The contract allows termination with 30 days written notice (Page 5, Section 8.1). No penalties apply for termination."
- "Payment terms: Net 30 days. Late payments incur 1.5% monthly interest (Page 3, Section 4.2)."
- "Liability is capped at the contract value. Exclusions apply for indirect damages (Page 7, Section 12.3)."

Be direct, useful, and actionable. Focus on what the user needs to know."""

        # Build user prompt
        history_section = ""
        if history_text:
            history_section = f"Previous conversation:\n{history_text}\n\n"

        num_sources = len(citations_data)
        user_prompt = f"""Question: {question}

{history_section}Available Sources (numbered 1 to {num_sources}):
{context}

CRITICAL REMINDER: You have EXACTLY {num_sources} sources available (numbered 1 to {num_sources}).

Answer the question using the sources above. In your response:
- Provide a complete, accurate answer
- List ONLY the source numbers you actually used in cited_sources
- cited_sources must ONLY contain numbers from 1 to {num_sources} (no higher, no lower)
- Do NOT include any number outside the range 1-{num_sources}
- Set confidence score based on answer certainty"""

        try:
            # Generate structured answer using instructor
            structured_answer: StructuredAnswer = self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=StructuredAnswer,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for accuracy
            )

            # Validate cited sources - ensure they're within valid range
            # This is critical: instructor may not always enforce constraints perfectly
            valid_source_nums = set(range(1, len(citations_data) + 1))
            cited_sources = structured_answer.cited_sources

            # Filter to only valid sources - robust validation
            # Remove any source numbers that don't exist
            valid_cited_sources = [
                s for s in cited_sources if s in valid_source_nums]

            # Log if invalid sources were filtered out (for debugging)
            invalid_sources = [
                s for s in cited_sources if s not in valid_source_nums]
            if invalid_sources:
                logger.warning(
                    f"Filtered out invalid source numbers: {invalid_sources} (valid range: 1-{len(citations_data)})",
                    extra={
                        "invalid_sources": invalid_sources,
                        "valid_range": f"1-{len(citations_data)}",
                        "num_citations": len(citations_data)
                    }
                )

            # If no valid citations, use top 3 by similarity score
            if not valid_cited_sources:
                sorted_citations = sorted(
                    citations_data,
                    key=lambda c: c.similarity_score if isinstance(
                        c, Citation) else c.get("similarity_score", -1.0),
                    reverse=True
                )
                valid_cited_sources = [
                    i + 1 for i in range(min(3, len(sorted_citations)))]

            # Get citations for valid sources
            used_citations = []
            for source_num in sorted(set(valid_cited_sources)):
                idx = source_num - 1  # Convert to 0-based
                if 0 <= idx < len(citations_data):
                    citation = citations_data[idx]
                    # Filter by similarity if needed
                    score = citation.similarity_score if isinstance(
                        citation, Citation) else citation.get("similarity_score", -1.0)
                    if score > -0.3:  # MIN_CITATION_SIMILARITY
                        used_citations.append(citation)

            # If filtering removed all, keep top 3
            if not used_citations:
                sorted_citations = sorted(
                    citations_data,
                    key=lambda c: c.similarity_score if isinstance(
                        c, Citation) else c.get("similarity_score", -1.0),
                    reverse=True
                )
                used_citations = sorted_citations[:3]

            # Format answer - clean up any invalid source references
            answer = structured_answer.answer

            # Remove invalid source references from answer text
            # Find all source references (both [Source N] and Source N formats)
            import re
            # Match both [Source N] and Source N (without brackets)
            source_refs_bracketed = re.findall(
                r'\[Source\s+(\d+)\]', answer, re.IGNORECASE)
            source_refs_unbracketed = re.findall(
                r'\bSource\s+(\d+)\b', answer, re.IGNORECASE)
            all_source_refs = set(
                source_refs_bracketed + source_refs_unbracketed)
            valid_refs_set = set(str(s) for s in valid_cited_sources)

            # Remove invalid references from answer
            cleaned_answer = answer
            for ref in all_source_refs:
                if ref not in valid_refs_set:
                    # Remove both [Source N] and Source N formats
                    pattern_bracketed = rf'\[Source\s+{ref}\]'
                    pattern_unbracketed = rf'\bSource\s+{ref}\b'
                    cleaned_answer = re.sub(
                        pattern_bracketed, '', cleaned_answer, flags=re.IGNORECASE)
                    cleaned_answer = re.sub(
                        pattern_unbracketed, '', cleaned_answer, flags=re.IGNORECASE)

            # Clean up formatting - preserve paragraph breaks and proper spacing
            # Only collapse multiple spaces, preserve newlines
            # Collapse spaces/tabs
            cleaned_answer = re.sub(r'[ \t]+', ' ', cleaned_answer)
            # Fix spacing before citations
            cleaned_answer = re.sub(
                r'[ \t]*\[Source', ' [Source', cleaned_answer)
            # Clean up standalone "Source N" (not in brackets)
            cleaned_answer = re.sub(
                r'\s+Source\s+(\d+)', r' [Source \1]', cleaned_answer)
            # Preserve paragraph breaks (double newlines)
            cleaned_answer = re.sub(r'\n\s*\n', '\n\n', cleaned_answer)
            cleaned_answer = cleaned_answer.strip()

            answer = cleaned_answer if cleaned_answer else structured_answer.answer

            # DO NOT add redundant "Sources:" paragraph - citations are already inline
            # The frontend will display citations separately

            # Convert citations to dict format
            citations_dict = []
            for c in used_citations:
                if isinstance(c, Citation):
                    citations_dict.append(c.dict())
                elif isinstance(c, dict):
                    citations_dict.append(c)
                else:
                    citations_dict.append({
                        "document_id": getattr(c, "document_id", ""),
                        "document_name": getattr(c, "document_name", ""),
                        "page_number": getattr(c, "page_number", 0),
                        "section_name": getattr(c, "section_name", ""),
                        "text_excerpt": getattr(c, "text_excerpt", ""),
                        "similarity_score": getattr(c, "similarity_score", 0.0),
                        "chunk_id": getattr(c, "chunk_id", None)
                    })

            return {
                **state,
                "answer": answer,
                "citations": citations_dict,
                "error": None
            }

        except Exception as e:
            return {
                **state,
                "answer": f"Error generating answer: {str(e)}",
                "citations": [],
                "error": str(e)
            }

    def ask(
        self,
        question: str,
        workspace_id: str,
        document_ids: Optional[List[str]] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Ask a question and get an answer with citations.

        Args:
            question: User's question
            workspace_id: Workspace UUID
            document_ids: Optional list of document IDs to search
            conversation_history: Optional conversation history

        Returns:
            Dict with answer, citations, and metadata
        """
        # Prepare conversation history (already in dict format)
        history = conversation_history or []

        # Initial state
        initial_state: ContractIQState = {
            "question": question,
            "workspace_id": workspace_id,
            "document_ids": document_ids,
            "conversation_history": history,
            "retrieved_chunks": [],
            "answer": "",
            "citations": [],
            "error": None
        }

        # Run graph
        result = self.graph.invoke(initial_state)

        return {
            "answer": result["answer"],
            "citations": result["citations"],
            "retrieved_chunks_count": len(result.get("retrieved_chunks", [])),
            "error": result.get("error")
        }

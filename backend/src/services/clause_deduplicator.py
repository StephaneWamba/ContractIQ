"""
LLM-based clause deduplication service.

Uses LLM to intelligently identify true duplicates vs similar but distinct clauses,
avoiding heuristic text matching that might miss semantic duplicates or incorrectly
merge distinct clauses.
"""
from typing import List, Dict, Set
from openai import OpenAI
from instructor import patch
from pydantic import BaseModel, Field

from src.core.config import settings
from src.core.logging_config import get_logger
from src.services.clause_extractor import ExtractedClause

logger = get_logger(__name__)


class ClausePair(BaseModel):
    """Pair of clauses for comparison"""
    clause1_text: str = Field(description="Text of first clause")
    clause1_type: str = Field(description="Type of first clause")
    clause1_page: int = Field(description="Page number of first clause")
    clause2_text: str = Field(description="Text of second clause")
    clause2_type: str = Field(description="Type of second clause")
    clause2_page: int = Field(description="Page number of second clause")


class DuplicateDecision(BaseModel):
    """LLM decision on whether clauses are duplicates"""
    is_duplicate: bool = Field(description="True if clauses are duplicates")
    reasoning: str = Field(description="Explanation of why they are/aren't duplicates")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in decision (0-1)")


class ClauseDeduplicator:
    """
    LLM-based clause deduplication.
    
    Uses LLM to intelligently identify duplicates by understanding semantic meaning
    rather than relying on text similarity heuristics.
    """
    
    def __init__(self):
        """Initialize deduplicator"""
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = patch(OpenAI(api_key=settings.openai_api_key))
    
    def deduplicate_clauses(
        self,
        clauses: List[ExtractedClause]
    ) -> List[ExtractedClause]:
        """
        Remove duplicate clauses using LLM-based comparison.
        
        Args:
            clauses: List of extracted clauses
            
        Returns:
            Deduplicated list of clauses (keeping best version of each duplicate)
        """
        if len(clauses) <= 1:
            return clauses
        
        # Group clauses by type and page for efficient comparison
        # Only compare clauses of same type on same or adjacent pages
        clause_groups = self._group_clauses_for_comparison(clauses)
        
        # Track which clauses to keep
        keep_indices: Set[int] = set(range(len(clauses)))
        
        # Compare clauses within each group
        for group_indices in clause_groups:
            if len(group_indices) <= 1:
                continue
            
            # Compare all pairs in group
            for i in range(len(group_indices)):
                if group_indices[i] not in keep_indices:
                    continue
                
                for j in range(i + 1, len(group_indices)):
                    if group_indices[j] not in keep_indices:
                        continue
                    
                    idx1, idx2 = group_indices[i], group_indices[j]
                    clause1, clause2 = clauses[idx1], clauses[idx2]
                    
                    # Use LLM to determine if duplicate
                    is_duplicate = self._are_clauses_duplicate(clause1, clause2)
                    
                    if is_duplicate:
                        # Keep the one with higher confidence or more complete text
                        if self._is_clause_better(clause1, clause2):
                            keep_indices.discard(idx2)
                        else:
                            keep_indices.discard(idx1)
                            break  # clause1 removed, move to next
        
        return [clauses[i] for i in sorted(keep_indices)]
    
    def _group_clauses_for_comparison(
        self,
        clauses: List[ExtractedClause]
    ) -> List[List[int]]:
        """
        Group clauses for efficient comparison.
        Only compare clauses of same type on same or adjacent pages.
        """
        groups: Dict[tuple, List[int]] = {}
        
        for idx, clause in enumerate(clauses):
            # Group by (type, page_range)
            # Compare clauses on same page or adjacent pages (±1)
            key = (clause.clause_type.value, clause.page_number)
            
            if key not in groups:
                groups[key] = []
            groups[key].append(idx)
            
            # Also add to adjacent page groups
            if clause.page_number > 0:
                key_prev = (clause.clause_type.value, clause.page_number - 1)
                if key_prev not in groups:
                    groups[key_prev] = []
                groups[key_prev].append(idx)
            
            key_next = (clause.clause_type.value, clause.page_number + 1)
            if key_next not in groups:
                groups[key_next] = []
            groups[key_next].append(idx)
        
        return list(groups.values())
    
    def _are_clauses_duplicate(
        self,
        clause1: ExtractedClause,
        clause2: ExtractedClause
    ) -> bool:
        """
        Use LLM to determine if two clauses are duplicates.
        
        Returns True if clauses represent the same legal provision (duplicate extraction).
        """
        # Quick checks first
        if clause1.clause_type != clause2.clause_type:
            return False
        
        if abs(clause1.page_number - clause2.page_number) > 2:
            return False  # Too far apart to be same clause
        
        # Use LLM for semantic comparison
        try:
            pair = ClausePair(
                clause1_text=clause1.extracted_text,
                clause1_type=clause1.clause_type.value,
                clause1_page=clause1.page_number,
                clause2_text=clause2.extracted_text,
                clause2_type=clause2.clause_type.value,
                clause2_page=clause2.page_number
            )
            
            decision: DuplicateDecision = self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=DuplicateDecision,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert contract analyst. Determine if two extracted clauses are duplicates (same legal provision extracted twice) or distinct clauses.

A duplicate means:
- Same legal provision extracted from overlapping document sections
- Same meaning and intent, even if wording differs slightly
- Same clause type and same page/adjacent pages

NOT duplicates if:
- Different legal provisions (even if similar wording)
- Different clause types
- Related but distinct clauses (e.g., termination for cause vs termination for convenience)

Be precise: false positives (merging distinct clauses) are worse than false negatives (keeping duplicates)."""
                    },
                    {
                        "role": "user",
                        "content": f"""Are these two clauses duplicates (same provision extracted twice)?

Clause 1 (Type: {pair.clause1_type}, Page: {pair.clause1_page}):
{pair.clause1_text}

Clause 2 (Type: {pair.clause2_type}, Page: {pair.clause2_page}):
{pair.clause2_text}

Respond with is_duplicate=true only if they represent the SAME legal provision."""
                    }
                ],
                temperature=0.1
            )
            
            # Only trust high-confidence decisions
            return decision.is_duplicate and decision.confidence >= 0.8
            
        except Exception as e:
            logger.error(f"Error in LLM deduplication: {e}", exc_info=True)
            # Fallback: simple text similarity (but only for very similar text)
            text1 = clause1.extracted_text.strip().lower()
            text2 = clause2.extracted_text.strip().lower()
            
            # Only consider duplicates if >90% text overlap
            if len(text1) > 0 and len(text2) > 0:
                # Simple overlap check
                shorter = min(len(text1), len(text2))
                longer = max(len(text1), len(text2))
                if shorter / longer > 0.9 and text1[:100] == text2[:100]:
                    return True
            
            return False
    
    def _is_clause_better(
        self,
        clause1: ExtractedClause,
        clause2: ExtractedClause
    ) -> bool:
        """Determine which clause is better (keep this one)"""
        # Prefer higher confidence
        conf1 = clause1.confidence_score or 0.0
        conf2 = clause2.confidence_score or 0.0
        
        if abs(conf1 - conf2) > 0.05:
            return conf1 > conf2
        
        # If confidence similar, prefer longer text (more complete)
        if abs(len(clause1.extracted_text) - len(clause2.extracted_text)) > 20:
            return len(clause1.extracted_text) > len(clause2.extracted_text)
        
        # If still similar, prefer the one with risk reasoning
        has_reasoning1 = bool(clause1.risk_reasoning and clause1.risk_reasoning.strip())
        has_reasoning2 = bool(clause2.risk_reasoning and clause2.risk_reasoning.strip())
        
        if has_reasoning1 != has_reasoning2:
            return has_reasoning1
        
        # Default: keep first
        return True


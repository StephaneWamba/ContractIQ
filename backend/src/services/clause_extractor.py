"""
High-accuracy clause extraction service using LLM.

This service:
1. Analyzes document chunks to identify extractable clauses
2. Extracts clause text, type, and metadata with high accuracy
3. Performs risk analysis on each clause
4. Returns structured clause data ready for storage
"""
from typing import List, Dict, Optional
from enum import Enum
from openai import OpenAI
from instructor import patch
from pydantic import BaseModel, Field

from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class ClauseType(str, Enum):
    """Comprehensive clause type taxonomy"""
    TERMINATION = "Termination"
    PAYMENT = "Payment"
    LIABILITY = "Liability"
    INDEMNIFICATION = "Indemnification"
    INTELLECTUAL_PROPERTY = "Intellectual Property"
    CONFIDENTIALITY = "Confidentiality"
    DISPUTE_RESOLUTION = "Dispute Resolution"
    FORCE_MAJEURE = "Force Majeure"
    COMPLIANCE = "Compliance"
    INSURANCE = "Insurance"
    WARRANTIES = "Warranties"
    LIMITATION_OF_DAMAGES = "Limitation of Damages"
    DATA_PRIVACY = "Data Privacy"
    NON_COMPETE = "Non-Compete"
    ASSIGNMENT = "Assignment"
    GOVERNING_LAW = "Governing Law"
    NOTICES = "Notices"
    AMENDMENT = "Amendment"
    SEVERABILITY = "Severability"
    ENTIRE_AGREEMENT = "Entire Agreement"
    WAIVER = "Waiver"
    DEFINITIONS = "Definitions"
    INDEPENDENT_CONTRACTOR = "Independent Contractor"
    OTHER = "Other"


class RiskFlag(str, Enum):
    """Risk flag types"""
    UNFAVORABLE_TERMINATION = "unfavorable_termination"
    HIGH_LIABILITY = "high_liability"
    UNFAIR_PAYMENT_TERMS = "unfair_payment_terms"
    WEAK_INDEMNIFICATION = "weak_indemnification"
    IP_RISK = "ip_risk"
    COMPLIANCE_RISK = "compliance_risk"
    DATA_PRIVACY_RISK = "data_privacy_risk"
    EXCESSIVE_PENALTIES = "excessive_penalties"
    ONE_SIDED_TERMS = "one_sided_terms"
    UNCLEAR_LANGUAGE = "unclear_language"
    MISSING_PROTECTIONS = "missing_protections"


class ExtractedClause(BaseModel):
    """Single extracted clause with metadata"""
    clause_type: ClauseType = Field(description="Type of clause")
    extracted_text: str = Field(description="Complete text of the clause")
    page_number: int = Field(description="Page number where clause appears")
    section_name: str = Field(
        default="Unknown",
        description="Section name this clause belongs to"
    )
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0) for extraction accuracy"
    )
    risk_score: float = Field(
        ge=0.0,
        le=100.0,
        default=0.0,
        description="Risk score (0-100) indicating potential risk level"
    )
    risk_flags: List[str] = Field(
        default_factory=list,
        description="List of specific risk flags identified (e.g., 'unfavorable_termination', 'high_liability')"
    )
    risk_reasoning: str = Field(
        default="",
        description="Explanation of why this clause is risky (if applicable)"
    )
    clause_subtype: Optional[str] = Field(
        default=None,
        description="Subtype for more specific classification (e.g., 'Early Termination', 'Breach Termination')"
    )


class ClauseExtractionResult(BaseModel):
    """Result of clause extraction from a chunk or set of chunks"""
    clauses: List[ExtractedClause] = Field(
        description="List of extracted clauses"
    )
    processing_notes: str = Field(
        default="",
        description="Notes about the extraction process"
    )


class ClauseExtractor:
    """
    High-accuracy clause extraction service using LLM.

    Uses structured output (instructor) to ensure consistent, validated results.
    """

    def __init__(self):
        """Initialize clause extractor"""
        if not settings.openai_api_key:
            raise ValueError(
                "OpenAI API key not configured. Set OPENAI_API_KEY in environment.")

        self.client = patch(OpenAI(api_key=settings.openai_api_key))

    def extract_clauses_from_chunks(
        self,
        chunks: List[Dict],
        document_context: Optional[Dict] = None
    ) -> List[ExtractedClause]:
        """
        Extract clauses from document chunks.

        Args:
            chunks: List of chunk dictionaries with 'text', 'page_number', 'section_name'
            document_context: Optional document metadata for context

        Returns:
            List of extracted clauses with risk analysis
        """
        all_clauses = []

        # Process chunks in batches to avoid token limits
        batch_size = 5
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_clauses = self._extract_from_batch(batch, document_context)
            all_clauses.extend(batch_clauses)

        return all_clauses

    def _validate_and_correct_clause_types(
        self,
        clauses: List[ExtractedClause]
    ) -> List[ExtractedClause]:
        """
        Validate and correct invalid clause types.
        Replaces any invalid clause_type with 'Other'.
        """
        valid_types = {ct.value for ct in ClauseType}
        corrected_clauses = []

        for clause in clauses:
            if clause.clause_type.value not in valid_types:
                logger.warning(
                    f"Invalid clause_type '{clause.clause_type.value}' detected. "
                    f"Correcting to 'Other'. Clause text: {clause.extracted_text[:100]}..."
                )
                # Create a new clause with corrected type
                corrected_clause = ExtractedClause(
                    clause_type=ClauseType.OTHER,
                    extracted_text=clause.extracted_text,
                    page_number=clause.page_number,
                    section_name=clause.section_name,
                    confidence_score=clause.confidence_score,
                    risk_score=clause.risk_score,
                    risk_flags=clause.risk_flags,
                    risk_reasoning=clause.risk_reasoning,
                    clause_subtype=clause.clause_subtype
                )
                corrected_clauses.append(corrected_clause)
            else:
                corrected_clauses.append(clause)

        return corrected_clauses

    def _extract_from_batch(
        self,
        chunks: List[Dict],
        document_context: Optional[Dict] = None,
        max_retries: int = 2
    ) -> List[ExtractedClause]:
        """Extract clauses from a batch of chunks with retry logic"""

        # Prepare chunk text for LLM
        chunk_texts = []
        for chunk in chunks:
            chunk_info = f"[Page {chunk.get('page_number', '?')}, Section: {chunk.get('section_name', 'Unknown')}]\n"
            chunk_info += chunk.get('text', '')
            chunk_texts.append(chunk_info)

        combined_text = "\n\n---\n\n".join(chunk_texts)

        # Truncate if too long (keep last 150k chars to preserve context)
        max_chars = 150000
        if len(combined_text) > max_chars:
            combined_text = combined_text[-max_chars:]

        # Build system prompt with few-shot examples
        system_prompt = self._build_extraction_prompt(document_context)

        # Extract clauses using structured output with retry logic
        for attempt in range(max_retries + 1):
            try:
                result: ClauseExtractionResult = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    response_model=ClauseExtractionResult,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Extract all clauses from the following document chunks:\n\n{combined_text}"}
                    ],
                    temperature=0.0,  # Zero temperature for maximum consistency
                )

                # Validate and correct clause types before returning
                validated_clauses = self._validate_and_correct_clause_types(
                    result.clauses)

                if validated_clauses != result.clauses:
                    logger.info(
                        f"Corrected {len(result.clauses) - len(validated_clauses)} invalid clause types "
                        f"in batch extraction"
                    )

                return validated_clauses

            except Exception as e:
                error_msg = str(e)

                # Check if it's a validation error for clause_type
                if "clause_type" in error_msg.lower() and "enum" in error_msg.lower():
                    logger.warning(
                        f"Validation error on attempt {attempt + 1}/{max_retries + 1}: {error_msg[:200]}"
                    )

                    if attempt < max_retries:
                        # Add correction instruction to prompt for retry
                        correction_note = (
                            "\n\nCRITICAL REMINDER: You MUST use ONLY the clause types listed above. "
                            "If a clause doesn't match any specific type, you MUST use 'Other'. "
                            "Never invent new clause type names. Any clause that doesn't fit the listed "
                            "categories MUST be classified as 'Other'."
                        )
                        system_prompt = self._build_extraction_prompt(
                            document_context) + correction_note
                        continue
                    else:
                        # Last attempt failed, try to extract without strict validation
                        logger.error(
                            f"All retry attempts failed. Attempting fallback extraction without strict validation."
                        )
                        return self._fallback_extraction(combined_text, system_prompt)
                else:
                    # Non-validation error, log and return empty
                    logger.error(
                        f"Error extracting clauses: {e}", exc_info=True)
                    return []

        return []

    def _fallback_extraction(
        self,
        combined_text: str,
        system_prompt: str
    ) -> List[ExtractedClause]:
        """
        Fallback extraction method that handles invalid types gracefully.
        Uses a more permissive model that allows string clause_type, then corrects.
        """
        try:
            # Use a temporary model that accepts string clause_type
            class PermissiveExtractedClause(BaseModel):
                """Temporary permissive clause model"""
                clause_type: str = Field(description="Type of clause")
                extracted_text: str = Field(
                    description="Complete text of the clause")
                page_number: int = Field(
                    description="Page number where clause appears")
                section_name: str = Field(
                    default="Unknown", description="Section name")
                confidence_score: float = Field(
                    ge=0.0, le=1.0, description="Confidence score")
                risk_score: float = Field(
                    ge=0.0, le=100.0, default=0.0, description="Risk score")
                risk_flags: List[str] = Field(
                    default_factory=list, description="Risk flags")
                risk_reasoning: str = Field(
                    default="", description="Risk reasoning")
                clause_subtype: Optional[str] = Field(
                    default=None, description="Subtype")

            class PermissiveResult(BaseModel):
                clauses: List[PermissiveExtractedClause]

            result: PermissiveResult = self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=PermissiveResult,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract all clauses from the following document chunks:\n\n{combined_text}"}
                ],
                temperature=0.0,
            )

            # Convert to proper ExtractedClause objects, correcting invalid types
            corrected_clauses = []
            valid_types = {ct.value for ct in ClauseType}

            for clause in result.clauses:
                clause_type_value = clause.clause_type
                if clause_type_value not in valid_types:
                    logger.warning(
                        f"Fallback: Invalid clause_type '{clause_type_value}' corrected to 'Other'"
                    )
                    clause_type_value = ClauseType.OTHER.value

                corrected_clauses.append(ExtractedClause(
                    clause_type=ClauseType(clause_type_value),
                    extracted_text=clause.extracted_text,
                    page_number=clause.page_number,
                    section_name=clause.section_name,
                    confidence_score=clause.confidence_score,
                    risk_score=clause.risk_score,
                    risk_flags=clause.risk_flags,
                    risk_reasoning=clause.risk_reasoning,
                    clause_subtype=clause.clause_subtype
                ))

            return corrected_clauses

        except Exception as e:
            logger.error(
                f"Fallback extraction also failed: {e}", exc_info=True)
            return []

    def _build_extraction_prompt(self, document_context: Optional[Dict] = None) -> str:
        """Build the system prompt for clause extraction with few-shot examples"""

        prompt = """You are an expert contract analyst specializing in clause extraction and risk assessment.

Your task is to:
1. Identify and extract all extractable clauses from contract text
2. Classify each clause by type using ONLY the clause types listed below
3. Assess risk factors and assign risk scores
4. Provide confidence scores for extraction accuracy

CRITICAL RULE - CLAUSE TYPE CLASSIFICATION:
You MUST use ONLY the clause types from the list below. There are NO exceptions to this rule.

If a clause doesn't fit any of the specific categories listed below, you MUST classify it as "Other".
Examples of clauses that should be "Other":
- Documentation requirements
- Delivery schedules
- Training requirements
- Maintenance obligations
- Quality standards
- Any clause that doesn't clearly match a specific category below

NEVER invent new clause type names. NEVER use names like "Documentation", "Delivery", "Training", etc.
If you are unsure which category a clause belongs to, use "Other".

The valid clause types are EXACTLY these (case-sensitive):

CLAUSE TYPES TO EXTRACT:
- Termination: Early termination, breach termination, convenience termination
- Payment: Payment terms, schedules, penalties, late fees
- Liability: Liability limitations, caps, exclusions
- Indemnification: Indemnification clauses, hold harmless provisions
- Intellectual Property: IP ownership, licensing, rights
- Confidentiality: NDA terms, confidentiality obligations
- Dispute Resolution: Arbitration, jurisdiction, mediation
- Force Majeure: Force majeure provisions
- Compliance: Regulatory compliance, certifications
- Insurance: Insurance requirements, coverage
- Warranties: Warranties, representations
- Limitation of Damages: Damage caps, exclusions
- Data Privacy: Data protection, privacy obligations
- Non-Compete: Non-compete, non-solicitation
- Assignment: Assignment rights, restrictions
- Governing Law: Choice of law, venue
- Notices: Notice requirements
- Amendment: Amendment procedures
- Severability: Severability clauses
- Entire Agreement: Entire agreement clauses
- Independent Contractor: Contractor status, relationship definitions, authority limitations
- Waiver: Waiver clauses, rights waivers
- Definitions: Term definitions, glossary

RISK ASSESSMENT:
For each clause, you MUST provide:
- Risk Score (0-100): 0 = no risk/standard, 100 = extreme risk
  * 0-24: Low risk (standard, acceptable terms)
  * 25-49: Medium risk (some concerns, review recommended)
  * 50-74: High risk (significant concerns, negotiation recommended)
  * 75-100: Critical risk (major issues, requires immediate attention)
- Risk Flags: Identify specific risk factors (use exact flag names from list below)
- Risk Reasoning: ALWAYS provide detailed explanation:
  * For low-risk clauses: Explain why it's acceptable/standard (e.g., "Standard 30-day notice period is reasonable and industry-standard")
  * For medium-risk clauses: Explain specific concerns (e.g., "5% monthly penalty rate is high but may be negotiable")
  * For high-risk clauses: Explain major risks and implications (e.g., "Unlimited liability exposes contractor to catastrophic financial risk")
  * For critical-risk clauses: Explain severe risks and urgent actions needed (e.g., "One-sided termination clause allows immediate termination without cause or compensation")
  
CRITICAL: Risk Reasoning is MANDATORY for ALL clauses. Never leave it empty.

RISK FLAGS (use exact string values):
- "unfavorable_termination": One-sided termination rights
- "high_liability": Unlimited or very high liability caps
- "unfair_payment_terms": Penalties, late fees, unfavorable payment terms
- "weak_indemnification": Limited indemnification protection
- "ip_risk": Unfavorable IP ownership or licensing
- "compliance_risk": Missing required compliance clauses
- "data_privacy_risk": Weak data protection provisions
- "excessive_penalties": Excessive penalties or liquidated damages
- "one_sided_terms": Terms that heavily favor one party
- "unclear_language": Ambiguous or unclear language
- "missing_protections": Missing standard protections

IMPORTANT: When returning risk_flags, use the exact string values listed above (e.g., "high_liability", not "High Liability").

EXTRACTION GUIDELINES:
1. Extract complete clauses - don't truncate mid-sentence
2. Only extract clauses that are clearly identifiable
3. Set confidence_score based on how certain you are (0.0-1.0)
4. If a chunk contains multiple clauses, extract each separately
5. If no extractable clauses found, return empty list
6. Preserve exact text from the document
7. Include page numbers accurately
8. ONLY use clause types from the "CLAUSE TYPES TO EXTRACT" list above - never create new clause types

EXAMPLES:

Example 1 - Low Risk Termination Clause:
Text: "Either party may terminate this Agreement at any time with thirty (30) days written notice."
Extraction:
- clause_type: Termination
- clause_subtype: Convenience Termination
- risk_score: 20 (low risk - standard notice period)
- risk_flags: [] (no flags)
- risk_reasoning: "Standard 30-day notice period is reasonable and provides adequate time for transition. This is an industry-standard termination clause that balances both parties' interests."
- confidence_score: 0.95

Example 2 - Critical Risk Liability Clause:
Text: "Contractor shall be liable for all damages, losses, and expenses of any kind, without limitation, arising from or related to this Agreement."
Extraction:
- clause_type: Liability
- risk_score: 85 (critical risk - unlimited liability)
- risk_flags: [high_liability, one_sided_terms]
- risk_reasoning: "Unlimited liability clause exposes contractor to catastrophic financial risk with no cap on potential damages. This could result in liability exceeding contract value by orders of magnitude. Standard practice is to cap liability at contract value or a reasonable multiple. This clause heavily favors the other party and should be negotiated to include liability caps and exclusions for indirect/consequential damages."
- confidence_score: 0.98

Example 3 - Medium Risk Payment Clause:
Text: "Payment shall be due within 30 days of invoice. Late payments shall incur a penalty of 5% per month."
Extraction:
- clause_type: Payment
- clause_subtype: Payment Terms with Penalties
- risk_score: 40 (medium risk - penalty rate is high)
- risk_flags: [unfair_payment_terms]
- risk_reasoning: "5% monthly penalty rate translates to 60% annually, which is significantly higher than typical late payment penalties (usually 1-2% per month). While 30-day payment terms are standard, the penalty rate is excessive and may not be enforceable in some jurisdictions. Consider negotiating a lower penalty rate (1-2% per month) or requesting a grace period before penalties apply."
- confidence_score: 0.92

Example 4 - Low Risk Independent Contractor Clause:
Text: "Vendor is an independent contractor and not an employee or agent of Watson or Watson Clients. Vendor has no authority to act for or on behalf of Watson or Watson Clients."
Extraction:
- clause_type: Independent Contractor
- risk_score: 10 (low risk - standard relationship definition)
- risk_flags: []
- risk_reasoning: "This clause clearly establishes the vendor as an independent contractor rather than an employee, which provides important legal protection for both parties. It prevents misunderstandings about employment status and reduces potential liability for employment-related claims. The limitation on authority is standard and reasonable."
- confidence_score: 0.95

Example 5 - Using "Other" for Unmapped Clause Types:
Text: "The Contractor shall provide three (3) sets of documentation in printed form or CD-ROM format for the Commissioning of Equipment."
Extraction:
- clause_type: Other
- clause_subtype: Documentation Requirements
- risk_score: 15 (low risk - standard deliverable requirement)
- risk_flags: []
- risk_reasoning: "This clause specifies documentation delivery requirements, which is a standard contractual obligation. While it doesn't fit into a specific category like Payment or Intellectual Property, it represents a reasonable deliverable requirement that ensures the client receives necessary materials for equipment operation."
- confidence_score: 0.90

NOTE: In Example 5, even though the clause mentions "documentation", we use "Other" because "Documentation" is NOT in the valid clause type list. The clause_subtype field can be used to provide more specific classification while keeping clause_type as "Other".

FINAL REMINDER: If you encounter ANY clause that doesn't match the exact categories listed above, you MUST use "Other" as the clause_type. Never create new clause type names.

Now extract clauses from the provided text, following these guidelines precisely."""

        if document_context:
            prompt += f"\n\nDOCUMENT CONTEXT:\n{document_context}"

        return prompt

    def extract_clauses_from_document(
        self,
        document_id: str,
        chunks: List[Dict]
    ) -> List[ExtractedClause]:
        """
        Extract clauses from a processed document.

        This is the main entry point for clause extraction.
        """
        document_context = {
            "document_id": document_id,
            "total_chunks": len(chunks)
        }

        return self.extract_clauses_from_chunks(chunks, document_context)

"""
LLM-Enhanced Extraction Service using Instructor for Structured Outputs

Provides context-aware extraction and validation for financial document fields,
especially for complex cases where regex-based extraction fails.
"""
from typing import Optional
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI

from src.core.config import settings


class TaxExtraction(BaseModel):
    """Structured tax information extraction"""
    tax_rate: Optional[float] = Field(
        None,
        description="Tax rate as percentage (e.g., 8.0 for 8%, not 0.08). Extract from patterns like 'Tax (8%):' or '8% Tax'"
    )
    tax_amount: Optional[float] = Field(
        None,
        description="Tax amount in currency (e.g., 160.00). This should be the tax value, NOT the total amount."
    )
    confidence: float = Field(
        default=0.0,
        description="Confidence score 0.0-1.0 for the extraction"
    )
    reasoning: str = Field(
        default="",
        description="Brief explanation of how values were extracted"
    )


class TotalsExtraction(BaseModel):
    """Structured totals section extraction"""
    subtotal: Optional[float] = Field(
        None,
        description="Subtotal amount before tax"
    )
    tax_rate: Optional[float] = Field(
        None,
        description="Tax rate as percentage (e.g., 8.0 for 8%)"
    )
    tax_amount: Optional[float] = Field(
        None,
        description="Tax amount (NOT the total)"
    )
    total_amount: Optional[float] = Field(
        None,
        description="Final total amount including tax"
    )
    confidence: float = Field(
        default=0.0,
        description="Overall confidence score 0.0-1.0"
    )
    extraction_notes: str = Field(
        default="",
        description="Notes about extraction process and any ambiguities"
    )


class ValidationResult(BaseModel):
    """Result of validating extracted vs calculated values"""
    is_extraction_error: bool = Field(
        description="True if the discrepancy is due to extraction error, False if it's a real document discrepancy"
    )
    confidence: float = Field(
        description="Confidence in the validation decision (0.0-1.0)"
    )
    reasoning: str = Field(
        description="Explanation of why this is an extraction error or real discrepancy"
    )
    recommended_value: Optional[float] = Field(
        None,
        description="Recommended value to use (calculated if extraction error, extracted if real discrepancy)"
    )


class LLMExtractor:
    """LLM-powered extraction service using Instructor for structured outputs"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            self.client = None
            self.enabled = False
        else:
            self.client = instructor.patch(OpenAI(api_key=settings.OPENAI_API_KEY))
            self.enabled = settings.USE_LLM_FOR_EXTRACTION
    
    def extract_tax_rate(self, text_content: str) -> Optional[TaxExtraction]:
        """
        Extract tax rate from text using LLM with structured output.
        
        Args:
            text_content: Text containing tax information (e.g., "Tax (8%): $160.00")
            
        Returns:
            TaxExtraction with tax_rate and tax_amount, or None if LLM not available
        """
        if not self.enabled or not self.client:
            return None
        
        try:
            prompt = f"""Extract tax information from this financial document text.

Text: {text_content}

Instructions:
1. Look for tax rate percentage in patterns like:
   - "Tax (8%):"
   - "8% Tax"
   - "Tax Rate: 8%"
   - "VAT 20%"
   
2. Extract tax rate as a percentage number (e.g., 8.0 for 8%, NOT 0.08)

3. If you see a tax amount, extract it (e.g., "$160.00" → 160.0)
   - Make sure it's the TAX amount, not the TOTAL amount
   - If you see "Tax (8%): $160.00 Total: $2,160.00", the tax amount is 160.00, NOT 2160.00

4. Be careful to distinguish:
   - Tax amount (what we want)
   - Total amount (what we DON'T want)
   - Subtotal (what we DON'T want)

Return structured data with confidence score."""

            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                response_model=TaxExtraction,
                messages=[
                    {"role": "system", "content": "You are a financial document extraction expert. Extract tax information accurately and distinguish between tax amounts and total amounts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,  # Deterministic extraction
            )
            
            return response
            
        except Exception as e:
            # Fallback to regex if LLM fails
            return None
    
    def extract_totals_section(self, paragraphs: list[str]) -> Optional[TotalsExtraction]:
        """
        Extract totals section (subtotal, tax, total) from multiple paragraphs.
        
        Args:
            paragraphs: List of paragraph texts that may contain totals information
            
        Returns:
            TotalsExtraction with all totals fields, or None if LLM not available
        """
        if not self.enabled or not self.client:
            return None
        
        try:
            # Combine relevant paragraphs
            relevant_text = "\n".join([
                para for para in paragraphs 
                if any(keyword in para.lower() for keyword in ["subtotal", "tax", "total", "vat"])
            ])
            
            if not relevant_text:
                return None
            
            prompt = f"""Extract financial totals from this purchase order document.

Text sections:
{relevant_text}

Instructions:
1. Extract subtotal (amount before tax)
2. Extract tax rate as percentage (e.g., 8.0 for 8%)
3. Extract tax amount (the tax value itself, NOT the total)
4. Extract total amount (final amount including tax)

Be very careful to distinguish:
- Subtotal: Base amount before tax
- Tax Rate: Percentage (e.g., 8% = 8.0)
- Tax Amount: The tax value (e.g., if subtotal is 2000 and tax is 8%, tax amount is 160)
- Total Amount: Subtotal + Tax Amount

If text is ambiguous or combined (e.g., "Subtotal: $2,000.00 Tax (8%): $160.00 Total: $2,160.00"),
correctly identify each value based on its label.

Return structured data with confidence scores."""

            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                response_model=TotalsExtraction,
                messages=[
                    {"role": "system", "content": "You are a financial document extraction expert. Accurately extract subtotal, tax rate, tax amount, and total amount, distinguishing between them carefully."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
            )
            
            return response
            
        except Exception as e:
            return None
    
    def validate_tax_discrepancy(
        self,
        extracted_tax_amount: float,
        calculated_tax_amount: float,
        subtotal: float,
        tax_rate: float,
        document_context: str
    ) -> Optional[ValidationResult]:
        """
        Validate if a discrepancy between extracted and calculated tax is an extraction error
        or a real document discrepancy.
        
        Args:
            extracted_tax_amount: Tax amount extracted from document
            calculated_tax_amount: Tax amount calculated from subtotal × tax_rate
            subtotal: Subtotal amount
            tax_rate: Tax rate percentage
            document_context: Relevant document text for context
            
        Returns:
            ValidationResult indicating if it's an extraction error, or None if LLM not available
        """
        if not self.enabled or not self.client:
            return None
        
        try:
            difference = abs(extracted_tax_amount - calculated_tax_amount)
            difference_percent = (difference / subtotal * 100) if subtotal > 0 else 0
            
            prompt = f"""You are validating financial data extraction accuracy.

Context:
- Subtotal: {subtotal}
- Tax Rate: {tax_rate}%
- Calculated Tax Amount: {calculated_tax_amount} (subtotal × tax_rate/100)
- Extracted Tax Amount: {extracted_tax_amount}
- Difference: {difference} ({difference_percent:.2f}% of subtotal)

Document Context:
{document_context}

Question: Is the difference between extracted and calculated tax amounts:
1. An EXTRACTION ERROR (we picked the wrong number from document)?
   - Example: Extracted the "Total" amount instead of "Tax" amount
   - Example: Picked a number from wrong line
   
2. A REAL DOCUMENT DISCREPANCY (document has calculation error)?
   - Example: Document shows wrong tax calculation
   - Example: Document has typo
   
3. ACCEPTABLE ROUNDING (small difference due to rounding)?
   - Example: Difference < 1% of subtotal

Consider:
- If extracted amount equals the "Total" line value → extraction error
- If extracted amount is very close to calculated (±1%) → rounding
- If extracted amount is very different → likely extraction error (picked wrong number)

Return structured validation result."""

            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                response_model=ValidationResult,
                messages=[
                    {"role": "system", "content": "You are a financial data validation expert. Distinguish between extraction errors and real document discrepancies."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
            )
            
            return response
            
        except Exception as e:
            return None



from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.extracted_data import ExtractedData
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


router = APIRouter()


class LineItemResponse(BaseModel):
    item_number: Optional[str]
    description: Optional[str]
    quantity: Optional[float]
    unit_price: Optional[float]
    line_total: Optional[float]


class ExtractedDataResponse(BaseModel):
    id: str
    document_id: str
    po_number: Optional[str]
    invoice_number: Optional[str]
    delivery_note_number: Optional[str]
    vendor_name: Optional[str]
    vendor_address: Optional[str]
    date: Optional[datetime]
    total_amount: Optional[float]
    currency_code: Optional[str]
    subtotal: Optional[float]
    tax_amount: Optional[float]
    tax_rate: Optional[float]
    due_date: Optional[datetime]
    line_items: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    extraction_model: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/document/{document_id}", response_model=ExtractedDataResponse)
async def get_extracted_data(document_id: str, db: Session = Depends(get_db)):
    """Get extracted data for a document"""
    extracted_data = db.query(ExtractedData).filter(ExtractedData.document_id == document_id).first()
    if not extracted_data:
        raise HTTPException(status_code=404, detail="Extracted data not found for this document")
    return extracted_data


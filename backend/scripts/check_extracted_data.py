"""
Check what data was actually extracted from documents in the database.
This helps us understand if Azure is extracting correctly.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.document import Document
from src.models.extracted_data import ExtractedData
from src.core.config import settings
import json

def check_extracted_data():
    """Check extracted data from all processed documents"""
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Get all processed documents
        documents = db.query(Document).filter(
            Document.status == "PROCESSED"
        ).all()
        
        print(f"\n{'='*60}")
        print(f"Found {len(documents)} processed documents")
        print(f"{'='*60}\n")
        
        for doc in documents:
            print(f"\nDocument: {doc.file_name} ({doc.document_type})")
            print(f"  ID: {doc.id}")
            print(f"  Status: {doc.status}")
            
            # Get extracted data
            extracted = db.query(ExtractedData).filter(
                ExtractedData.document_id == doc.id
            ).first()
            
            if extracted:
                print(f"\n  Extracted Data:")
                print(f"    Invoice Number: {extracted.invoice_number}")
                print(f"    PO Number: {extracted.po_number}")
                print(f"    Vendor Name: {extracted.vendor_name}")
                print(f"    Total Amount: {extracted.total_amount}")
                print(f"    Date: {extracted.date}")
                
                print(f"\n  Line Items ({len(extracted.line_items) if extracted.line_items else 0}):")
                if extracted.line_items:
                    for idx, item in enumerate(extracted.line_items[:3]):  # Show first 3
                        print(f"    Item {idx + 1}:")
                        print(f"      Item Number: {item.get('item_number')}")
                        print(f"      Description: {item.get('description')}")
                        print(f"      Quantity: {item.get('quantity')}")
                        print(f"      Unit Price: {item.get('unit_price')}")
                        print(f"      Line Total: {item.get('line_total')}")
                else:
                    print("      No line items extracted")
                
                print(f"\n  Confidence Scores:")
                if extracted.confidence_scores:
                    for field, score in extracted.confidence_scores.items():
                        print(f"    {field}: {score:.2f}")
            else:
                print("  No extracted data found")
            
            print("\n" + "-"*60)
        
    finally:
        db.close()

if __name__ == "__main__":
    check_extracted_data()



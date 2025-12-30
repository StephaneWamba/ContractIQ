"""
Debug script to see what Azure Form Recognizer actually extracts from our PDFs.
This helps us understand what fields are being extracted and fix any issues.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.form_recognizer import form_recognizer_service
from src.core.config import settings

def debug_invoice_extraction(pdf_path: str):
    """Debug what Azure extracts from an invoice PDF"""
    print(f"\n{'='*60}")
    print(f"Debugging Azure Extraction: {pdf_path}")
    print(f"{'='*60}\n")
    
    try:
        with open(pdf_path, 'rb') as f:
            file_content = f.read()
        
        # Use Azure's prebuilt-invoice model directly
        from azure.ai.formrecognizer import DocumentAnalysisClient
        from azure.core.credentials import AzureKeyCredential
        
        client = DocumentAnalysisClient(
            endpoint=settings.AZURE_FORM_RECOGNIZER_ENDPOINT,
            credential=AzureKeyCredential(settings.AZURE_FORM_RECOGNIZER_KEY)
        )
        
        poller = client.begin_analyze_document(
            model_id="prebuilt-invoice",
            document=file_content,
        )
        result = poller.result()
        
        print("=== DOCUMENT FIELDS ===")
        if result.documents:
            doc = result.documents[0]
            print(f"\nAvailable fields in document.fields:")
            for field_name, field_value in doc.fields.items():
                print(f"  - {field_name}: {field_value}")
                if hasattr(field_value, 'value'):
                    print(f"    Value: {field_value.value}")
                if hasattr(field_value, 'confidence'):
                    print(f"    Confidence: {field_value.confidence}")
        
        print("\n=== LINE ITEMS (Items field) ===")
        if result.documents:
            doc = result.documents[0]
            if "Items" in doc.fields:
                items = doc.fields["Items"].value
                print(f"Number of items: {len(items) if items else 0}")
                if items:
                    for idx, item in enumerate(items):
                        print(f"\n  Item {idx + 1}:")
                        item_value = item.value if hasattr(item, "value") else item
                        if isinstance(item_value, dict):
                            for key, value in item_value.items():
                                print(f"    {key}: {value}")
                        elif hasattr(item_value, "__dict__"):
                            for key, value in item_value.__dict__.items():
                                if not key.startswith("_"):
                                    print(f"    {key}: {value}")
                        else:
                            print(f"    Raw: {item_value}")
            else:
                print("  No 'Items' field found in document")
        
        print("\n=== ALL AVAILABLE FIELDS ===")
        if result.documents:
            doc = result.documents[0]
            print(f"Field names: {list(doc.fields.keys())}")
        
        # Also test our extraction function
        print("\n=== OUR EXTRACTION FUNCTION OUTPUT ===")
        extracted = form_recognizer_service.analyze_invoice(file_content)
        print(f"Invoice Number: {extracted.get('invoice_number')}")
        print(f"PO Number: {extracted.get('po_number')}")
        print(f"Vendor Name: {extracted.get('vendor_name')}")
        print(f"Total Amount: {extracted.get('total_amount')}")
        print(f"Line Items Count: {len(extracted.get('line_items', []))}")
        if extracted.get('line_items'):
            print("\nLine Items:")
            for idx, item in enumerate(extracted['line_items'][:3]):  # Show first 3
                print(f"  Item {idx + 1}: {item}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Default to first invoice in assets
        assets_dir = Path(__file__).parent.parent.parent / "assets"
        pdf_path = assets_dir / "test-invoice.pdf"
    
    if not Path(pdf_path).exists():
        print(f"PDF not found: {pdf_path}")
        print("\nUsage: python debug_azure_extraction.py <path_to_invoice.pdf>")
        sys.exit(1)
    
    debug_invoice_extraction(str(pdf_path))

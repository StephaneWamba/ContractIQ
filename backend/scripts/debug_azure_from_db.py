"""
Debug Azure extraction using documents already uploaded to the database.
"""
from src.core.config import settings
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from src.services.form_recognizer import form_recognizer_service
from src.services.storage import storage_service
from src.models.document import Document, DocumentType
from src.core.database import SessionLocal, engine
from sqlalchemy.orm import Session
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def debug_azure_response(file_content: bytes, model_id: str, doc_type: str, file_name: str):
    """Debug what Azure returns for a document."""
    print(f"\n{'='*80}")
    print(f"DEBUGGING: {doc_type.upper()} - Using model: {model_id}")
    print(f"File: {file_name}")
    print(f"{'='*80}\n")

    # Initialize client
    client = DocumentAnalysisClient(
        endpoint=settings.AZURE_FORM_RECOGNIZER_ENDPOINT,
        credential=AzureKeyCredential(settings.AZURE_FORM_RECOGNIZER_KEY),
    )

    # Analyze
    print("[*] Sending to Azure Form Recognizer...")
    poller = client.begin_analyze_document(
        model_id=model_id,
        document=file_content,
    )
    result = poller.result()

    print(f"[OK] Analysis complete\n")

    # Inspect result structure
    print("RESULT STRUCTURE:")
    print(f"  Type: {type(result)}")
    print(
        f"  Attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")
    print()

    # Check for key-value pairs
    print("KEY-VALUE PAIRS:")
    if hasattr(result, 'key_value_pairs'):
        kv_pairs = result.key_value_pairs
        print(f"  Found key_value_pairs: {type(kv_pairs)}")

        # Try to iterate
        try:
            if hasattr(kv_pairs, 'items'):
                print(f"  Has 'items' method")
                count = 0
                for key, value in kv_pairs.items():
                    if count < 10:  # Show first 10
                        val_str = str(value)
                        if hasattr(value, 'value'):
                            val_str = f"{val_str} (value: {value.value})"
                        if hasattr(value, 'content'):
                            val_str = f"{val_str} (content: {value.content})"
                        print(f"    '{key}' -> {val_str}")
                    count += 1
                print(f"  Total pairs: {count}")
            elif isinstance(kv_pairs, dict):
                print(f"  Is a dict with {len(kv_pairs)} items")
                for i, (key, value) in enumerate(list(kv_pairs.items())[:10]):
                    print(f"    '{key}' -> {value}")
            elif hasattr(kv_pairs, '__iter__'):
                print(f"  Is iterable")
                for i, item in enumerate(list(kv_pairs)[:10]):
                    print(f"    Item {i}: {item}")
        except Exception as e:
            print(f"  Error iterating: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("  No 'key_value_pairs' attribute found")

    print()

    # Check for tables
    print("TABLES:")
    if hasattr(result, 'tables'):
        tables = result.tables
        print(f"  Found {len(tables)} table(s)")
        for i, table in enumerate(tables):
            print(f"\n  Table {i+1}:")
            print(f"    Row count: {table.row_count}")
            print(f"    Column count: {table.column_count}")
            print(f"    Cells: {len(table.cells)}")

            # Show first few rows
            for row_idx in range(min(5, table.row_count)):
                row_cells = [
                    cell for cell in table.cells if cell.row_index == row_idx]
                if row_cells:
                    row_content = [cell.content for cell in sorted(
                        row_cells, key=lambda x: x.column_index)]
                    print(f"    Row {row_idx}: {row_content}")
    else:
        print("  No 'tables' attribute found")

    print()

    # Check for paragraphs
    print("PARAGRAPHS (first 10):")
    if hasattr(result, 'paragraphs'):
        paragraphs = result.paragraphs
        print(f"  Found {len(paragraphs)} paragraph(s)")
        for i, para in enumerate(paragraphs[:10]):
            print(f"    Para {i+1}: {para.content[:100]}")
    else:
        print("  No 'paragraphs' attribute found")

    print()

    # Search for specific values in paragraphs
    if hasattr(result, 'paragraphs'):
        print("SEARCHING FOR KEY VALUES IN PARAGRAPHS:")
        search_terms = ['PO-2024-001', 'PO Number',
                        'CONTOSO', 'Office Chairs', 'Desk Lamps']
        for term in search_terms:
            for para in result.paragraphs:
                if term.lower() in para.content.lower():
                    print(f"  Found '{term}': '{para.content[:150]}'")
                    break

    print(f"\n{'='*80}\n")


def main():
    """Debug extraction using documents from database."""
    db: Session = SessionLocal()

    try:
        # Get PO and Delivery Note documents
        po_doc = db.query(Document).filter(Document.document_type ==
                                           DocumentType.PURCHASE_ORDER).order_by(Document.created_at.desc()).first()
        dn_doc = db.query(Document).filter(Document.document_type ==
                                           DocumentType.DELIVERY_NOTE).order_by(Document.created_at.desc()).first()

        if po_doc:
            print(
                f"[*] Found PO document: {po_doc.file_name} (ID: {po_doc.id[:8]}...)")
            file_content = storage_service.get_file(po_doc.file_path)
            debug_azure_response(
                file_content, "prebuilt-layout", "Purchase Order", po_doc.file_name)

            # Also try prebuilt-purchaseOrder
            print("\n[*] Trying prebuilt-purchaseOrder model...")
            try:
                debug_azure_response(
                    file_content, "prebuilt-purchaseOrder", "Purchase Order", po_doc.file_name)
            except Exception as e:
                print(f"[ERROR] prebuilt-purchaseOrder failed: {e}")
        else:
            print("[ERROR] No PO document found in database")

        if dn_doc:
            print(
                f"[*] Found Delivery Note document: {dn_doc.file_name} (ID: {dn_doc.id[:8]}...)")
            file_content = storage_service.get_file(dn_doc.file_path)
            debug_azure_response(
                file_content, "prebuilt-layout", "Delivery Note", dn_doc.file_name)
        else:
            print("[ERROR] No Delivery Note document found in database")

    finally:
        db.close()


if __name__ == "__main__":
    main()


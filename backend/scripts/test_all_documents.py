"""
Test script to upload and process all document types (Invoice, PO, Delivery Note).
"""
import requests
import sys
from pathlib import Path

API_URL = "http://localhost:8100"

def test_document_upload(workspace_id: str, file_path: Path, doc_type: str):
    """Upload and process a document."""
    print(f"\n[*] Testing {doc_type}...")
    print(f"    File: {file_path.name}")
    
    if not file_path.exists():
        print(f"    [ERROR] File not found: {file_path}")
        return None
    
    # Upload document
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f, 'application/pdf')}
        params = {
            'document_type': doc_type,
            'workspace_id': workspace_id
        }
        response = requests.post(
            f"{API_URL}/api/documents/upload",
            files=files,
            params=params
        )
    
    if response.status_code != 200:
        print(f"    [ERROR] Upload failed: {response.status_code}")
        print(f"    {response.text}")
        return None
    
    doc_data = response.json()
    doc_id = doc_data['id']
    print(f"    [OK] Uploaded: {doc_id}")
    print(f"    Status: {doc_data['status']}")
    
    # Wait for processing
    import time
    max_wait = 30
    waited = 0
    while waited < max_wait:
        time.sleep(2)
        response = requests.get(f"{API_URL}/api/documents/{doc_id}")
        if response.status_code == 200:
            doc_data = response.json()
            if doc_data['status'] == 'PROCESSED':
                print(f"    [OK] Processing complete!")
                break
            elif doc_data['status'] == 'FAILED':
                print(f"    [ERROR] Processing failed!")
                return None
        waited += 2
    
    # Get extracted data
    response = requests.get(f"{API_URL}/api/extracted-data/document/{doc_id}")
    if response.status_code == 200:
        extracted = response.json()
        print(f"    Extracted Data:")
        if doc_type == 'invoice':
            print(f"      Invoice #: {extracted.get('invoice_number', 'N/A')}")
            print(f"      PO #: {extracted.get('po_number', 'N/A')}")
            print(f"      Vendor: {extracted.get('vendor_name', 'N/A')}")
            print(f"      Total: ${extracted.get('total_amount', 0):.2f}" if extracted.get('total_amount') else "      Total: N/A")
        elif doc_type == 'purchase_order':
            print(f"      PO #: {extracted.get('po_number', 'N/A')}")
            print(f"      Vendor: {extracted.get('vendor_name', 'N/A')}")
            print(f"      Total: ${extracted.get('total_amount', 0):.2f}" if extracted.get('total_amount') else "      Total: N/A")
        elif doc_type == 'delivery_note':
            print(f"      DN #: {extracted.get('delivery_note_number', 'N/A')}")
            print(f"      PO #: {extracted.get('po_number', 'N/A')}")
            print(f"      Vendor: {extracted.get('vendor_name', 'N/A')}")
        
        line_items = extracted.get('line_items', [])
        print(f"      Line Items: {len(line_items)}")
        if line_items:
            print(f"      First item: {line_items[0].get('description', 'N/A')}")
    
    return doc_id


def main():
    """Test all document types."""
    print("=" * 60)
    print("Document Processing Test Suite")
    print("=" * 60)
    
    # Create workspace
    print("\n[*] Creating test workspace...")
    response = requests.post(
        f"{API_URL}/api/workspaces",
        json={"name": "Test Suite Workspace", "is_temporary": True}
    )
    
    if response.status_code != 200:
        print(f"[ERROR] Failed to create workspace: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    workspace = response.json()
    workspace_id = workspace['id']
    print(f"[OK] Workspace created: {workspace_id}")
    
    # Find assets directory
    script_dir = Path(__file__).parent
    assets_dir = script_dir.parent.parent / "assets"
    
    # Test documents
    test_files = [
        (assets_dir / "test-invoice.pdf", "invoice"),
        (assets_dir / "test-po.pdf", "purchase_order"),
        (assets_dir / "test-delivery-note.pdf", "delivery_note"),
    ]
    
    results = {}
    for file_path, doc_type in test_files:
        doc_id = test_document_upload(workspace_id, file_path, doc_type)
        if doc_id:
            results[doc_type] = doc_id
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Workspace: {workspace_id}")
    print(f"Documents processed: {len(results)}/{len(test_files)}")
    for doc_type, doc_id in results.items():
        print(f"  {doc_type}: {doc_id}")
    
    if len(results) == len(test_files):
        print("\n[SUCCESS] All documents processed successfully!")
    else:
        print(f"\n[WARNING] {len(test_files) - len(results)} document(s) failed to process")


if __name__ == "__main__":
    main()


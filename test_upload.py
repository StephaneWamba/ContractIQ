import requests
import sys

# Create workspace
workspace_response = requests.post(
    "http://localhost:8100/api/workspaces",
    json={"name": "Test Workspace", "is_temporary": True}
)
workspace = workspace_response.json()
workspace_id = workspace["id"]
print(f"✅ Workspace created: {workspace_id}")

# Upload document
with open("assets/sample-invoice.pdf", "rb") as f:
    files = {"file": ("sample-invoice.pdf", f, "application/pdf")}
    params = {
        "workspace_id": workspace_id,
        "document_type": "invoice"
    }
    
    print("📤 Uploading document...")
    response = requests.post(
        "http://localhost:8100/api/documents/upload",
        params=params,
        files=files
    )
    
    if response.status_code == 200:
        doc = response.json()
        print(f"✅ Upload successful!")
        print(f"   Document ID: {doc['id']}")
        print(f"   Status: {doc['status']}")
        print(f"   File: {doc['file_name']}")
        
        # Get extracted data
        if doc['status'] == 'PROCESSED':
            print("\n📊 Fetching extracted data...")
            extracted = requests.get(
                f"http://localhost:8100/api/extracted-data/document/{doc['id']}"
            )
            if extracted.status_code == 200:
                data = extracted.json()
                print(f"   Invoice Number: {data.get('invoice_number', 'N/A')}")
                print(f"   Vendor: {data.get('vendor_name', 'N/A')}")
                print(f"   Total: ${data.get('total_amount', 'N/A')}")
                print(f"   Line Items: {len(data.get('line_items', []))}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")



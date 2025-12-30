"""
Extract and display raw data from all documents, then manually assess matching.
"""
import requests
import json
from pathlib import Path

API_URL = "http://localhost:8100"

def get_extracted_data(doc_id: str, doc_type: str):
    """Get extracted data for a document."""
    response = requests.get(f"{API_URL}/api/extracted-data/document/{doc_id}")
    if response.status_code == 200:
        return response.json()
    return None

def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_field(label: str, value):
    """Print a field with formatting."""
    if value is None:
        value = "[NOT EXTRACTED]"
    elif value == "":
        value = "[EMPTY]"
    print(f"  {label:30} {value}")

def print_line_items(items):
    """Print line items in a table format."""
    if not items:
        print("  [NO LINE ITEMS EXTRACTED]")
        return
    
    print(f"\n  Line Items ({len(items)}):")
    print(f"  {'-' * 80}")
    print(f"  {'Item #':<10} {'Description':<35} {'Qty':<8} {'Unit Price':<12} {'Total':<12}")
    print(f"  {'-' * 80}")
    
    for idx, item in enumerate(items, 1):
        item_num = item.get('item_number') or f"#{idx}"
        desc = (item.get('description') or 'N/A')[:33]
        qty = item.get('quantity') or 'N/A'
        unit_price = item.get('unit_price') or 'N/A'
        if isinstance(unit_price, (int, float)):
            unit_price = f"${unit_price:.2f}"
        total = item.get('line_total') or 'N/A'
        if isinstance(total, (int, float)):
            total = f"${total:.2f}"
        
        print(f"  {str(item_num):<10} {desc:<35} {str(qty):<8} {str(unit_price):<12} {str(total):<12}")

def main():
    """Extract and display all document data for manual assessment."""
    print("\n" + "=" * 80)
    print("  DOCUMENT EXTRACTION & MATCHING ASSESSMENT")
    print("=" * 80)
    
    # Get the last workspace (or create one)
    print("\n[*] Fetching recent workspace...")
    response = requests.get(f"{API_URL}/api/workspaces")
    if response.status_code != 200 or not response.json():
        print("[ERROR] No workspaces found. Please upload documents first.")
        return
    
    workspaces = response.json()
    workspace = workspaces[-1]  # Get the most recent
    workspace_id = workspace['id']
    print(f"[OK] Using workspace: {workspace_id}")
    
    # Get all documents in workspace
    print("\n[*] Fetching documents...")
    response = requests.get(f"{API_URL}/api/documents/workspace/{workspace_id}")
    if response.status_code != 200:
        print(f"[ERROR] Failed to get documents: {response.status_code}")
        return
    
    documents = response.json()
    print(f"[OK] Found {len(documents)} documents")
    
    # Organize documents by type
    docs_by_type = {}
    for doc in documents:
        doc_type = doc['document_type']
        if doc_type not in docs_by_type:
            docs_by_type[doc_type] = []
        docs_by_type[doc_type].append(doc)
    
    # Extract data for each document
    extracted_data = {}
    
    for doc_type, docs in docs_by_type.items():
        for doc in docs:
            doc_id = doc['id']
            print(f"\n[*] Extracting data from {doc_type} (ID: {doc_id[:8]}...)")
            data = get_extracted_data(doc_id, doc_type)
            if data:
                extracted_data[doc_id] = {
                    'type': doc_type,
                    'file_name': doc['file_name'],
                    'data': data
                }
                print(f"[OK] Data extracted")
            else:
                print(f"[ERROR] Failed to extract data")
    
    # Display extracted data
    print("\n\n" + "=" * 80)
    print("  EXTRACTED DATA - RAW OUTPUT")
    print("=" * 80)
    
    invoice_data = None
    po_data = None
    dn_data = None
    
    for doc_id, doc_info in extracted_data.items():
        doc_type = doc_info['type']
        data = doc_info['data']
        file_name = doc_info['file_name']
        
        print_section(f"{doc_type.upper().replace('_', ' ')} - {file_name}")
        
        if doc_type == 'invoice':
            invoice_data = data
            print_field("Invoice Number", data.get('invoice_number'))
            print_field("PO Number", data.get('po_number'))
            print_field("Vendor Name", data.get('vendor_name'))
            print_field("Vendor Address", data.get('vendor_address'))
            print_field("Invoice Date", data.get('invoice_date'))
            print_field("Due Date", data.get('due_date'))
            print_field("Subtotal", data.get('subtotal'))
            print_field("Tax", data.get('tax'))
            print_field("Total Amount", data.get('total_amount'))
            print_field("Currency", data.get('currency'))
            print_line_items(data.get('line_items', []))
            
        elif doc_type == 'purchase_order':
            po_data = data
            print_field("PO Number", data.get('po_number'))
            print_field("Vendor Name", data.get('vendor_name'))
            print_field("Vendor Address", data.get('vendor_address'))
            print_field("Order Date", data.get('order_date'))
            print_field("Delivery Date", data.get('delivery_date'))
            print_field("Subtotal", data.get('subtotal'))
            print_field("Tax", data.get('tax'))
            print_field("Total Amount", data.get('total_amount'))
            print_field("Currency", data.get('currency'))
            print_line_items(data.get('line_items', []))
            
        elif doc_type == 'delivery_note':
            dn_data = data
            print_field("Delivery Note Number", data.get('delivery_note_number'))
            print_field("PO Number", data.get('po_number'))
            print_field("Vendor Name", data.get('vendor_name'))
            print_field("Vendor Address", data.get('vendor_address'))
            print_field("Delivery Date", data.get('delivery_date'))
            print_line_items(data.get('line_items', []))
    
    # Manual Assessment
    print("\n\n" + "=" * 80)
    print("  MANUAL MATCHING ASSESSMENT")
    print("=" * 80)
    
    print("\n[ASSESSMENT] Comparing extracted data across documents...\n")
    
    # Check PO Number matching
    print("1. PO NUMBER MATCHING:")
    invoice_po = invoice_data.get('po_number') if invoice_data else None
    po_po = po_data.get('po_number') if po_data else None
    dn_po = dn_data.get('po_number') if dn_data else None
    
    print(f"   Invoice PO#: {invoice_po or '[NOT FOUND]'}")
    print(f"   PO PO#:      {po_po or '[NOT FOUND]'}")
    print(f"   DN PO#:      {dn_po or '[NOT FOUND]'}")
    
    if invoice_po and po_po:
        match = invoice_po == po_po
        print(f"   Invoice <-> PO: {'[MATCH]' if match else '[MISMATCH]'}")
    if po_po and dn_po:
        match = po_po == dn_po
        print(f"   PO <-> DN:      {'[MATCH]' if match else '[MISMATCH]'}")
    if invoice_po and dn_po:
        match = invoice_po == dn_po
        print(f"   Invoice <-> DN:  {'[MATCH]' if match else '[MISMATCH]'}")
    
    # Check Vendor matching
    print("\n2. VENDOR NAME MATCHING:")
    invoice_vendor = invoice_data.get('vendor_name') if invoice_data else None
    po_vendor = po_data.get('vendor_name') if po_data else None
    dn_vendor = dn_data.get('vendor_name') if dn_data else None
    
    print(f"   Invoice Vendor: {invoice_vendor or '[NOT FOUND]'}")
    print(f"   PO Vendor:       {po_vendor or '[NOT FOUND]'}")
    print(f"   DN Vendor:       {dn_vendor or '[NOT FOUND]'}")
    
    if invoice_vendor and po_vendor:
        # Normalize for comparison (case-insensitive, strip whitespace)
        inv_norm = invoice_vendor.strip().upper() if invoice_vendor else ""
        po_norm = po_vendor.strip().upper() if po_vendor else ""
        match = inv_norm == po_norm
        print(f"   Invoice <-> PO:   {'[MATCH]' if match else '[MISMATCH]'}")
    if po_vendor and dn_vendor:
        po_norm = po_vendor.strip().upper() if po_vendor else ""
        dn_norm = dn_vendor.strip().upper() if dn_vendor else ""
        match = po_norm == dn_norm
        print(f"   PO <-> DN:        {'[MATCH]' if match else '[MISMATCH]'}")
    
    # Check Total Amount matching
    print("\n3. TOTAL AMOUNT MATCHING:")
    invoice_total = invoice_data.get('total_amount') if invoice_data else None
    po_total = po_data.get('total_amount') if po_data else None
    
    print(f"   Invoice Total: ${invoice_total:.2f}" if invoice_total else "   Invoice Total: [NOT FOUND]")
    print(f"   PO Total:      ${po_total:.2f}" if po_total else "   PO Total:      [NOT FOUND]")
    
    if invoice_total and po_total:
        diff = abs(invoice_total - po_total)
        match = diff < 0.01  # Allow for floating point precision
        print(f"   Difference:    ${diff:.2f}")
        print(f"   Invoice <-> PO:  {'[MATCH]' if match else '[MISMATCH]'}")
    
    # Check Line Items matching
    print("\n4. LINE ITEMS MATCHING:")
    invoice_items = invoice_data.get('line_items', []) if invoice_data else []
    po_items = po_data.get('line_items', []) if po_data else []
    dn_items = dn_data.get('line_items', []) if dn_data else []
    
    print(f"   Invoice Items: {len(invoice_items)}")
    print(f"   PO Items:      {len(po_items)}")
    print(f"   DN Items:      {len(dn_items)}")
    
    if len(invoice_items) > 0 and len(po_items) > 0:
        print(f"   Invoice <-> PO:   {'[SAME COUNT]' if len(invoice_items) == len(po_items) else '[DIFFERENT COUNT]'}")
    if len(po_items) > 0 and len(dn_items) > 0:
        print(f"   PO <-> DN:        {'[SAME COUNT]' if len(po_items) == len(dn_items) else '[DIFFERENT COUNT]'}")
    
    # Detailed item comparison
    if invoice_items and po_items:
        print("\n   Item-by-Item Comparison (Invoice vs PO):")
        max_items = max(len(invoice_items), len(po_items))
        for i in range(max_items):
            inv_item = invoice_items[i] if i < len(invoice_items) else None
            po_item = po_items[i] if i < len(po_items) else None
            
            if inv_item and po_item:
                inv_desc = inv_item.get('description', 'N/A')
                po_desc = po_item.get('description', 'N/A')
                inv_qty = inv_item.get('quantity')
                po_qty = po_item.get('quantity')
                inv_price = inv_item.get('unit_price')
                po_price = po_item.get('unit_price')
                
                desc_match = inv_desc == po_desc
                qty_match = inv_qty == po_qty if (inv_qty and po_qty) else False
                price_match = abs(inv_price - po_price) < 0.01 if (inv_price and po_price) else False
                
                status = "[OK]" if (desc_match and qty_match and price_match) else "[MISMATCH]"
                desc_status = "[OK]" if desc_match else "[DIFF]"
                qty_status = "[OK]" if qty_match else "[DIFF]"
                price_status = "[OK]" if price_match else "[DIFF]"
                print(f"     Item {i+1}: {status} | Desc: {desc_status} | Qty: {qty_status} | Price: {price_status}")
                if not desc_match:
                    print(f"              Invoice: '{inv_desc}' vs PO: '{po_desc}'")
                if not qty_match:
                    print(f"              Invoice Qty: {inv_qty} vs PO Qty: {po_qty}")
                if not price_match:
                    print(f"              Invoice Price: ${inv_price} vs PO Price: ${po_price}")
    
    print("\n" + "=" * 80)
    print("  ASSESSMENT COMPLETE")
    print("=" * 80)
    print("\n[NOTE] This is a manual visual assessment. Matching logic will be")
    print("       implemented in Phase 3 of the roadmap.\n")

if __name__ == "__main__":
    main()


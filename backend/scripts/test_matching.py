"""
Test script for document matching functionality.
"""
import requests
import json
from pathlib import Path

API_URL = "http://localhost:8100"


def test_matching(workspace_id: str):
    """Test matching documents in a workspace."""
    print(f"\n{'='*80}")
    print("TESTING DOCUMENT MATCHING")
    print(f"{'='*80}\n")

    print(f"[*] Workspace ID: {workspace_id}")

    # Trigger matching
    print("\n[*] Triggering document matching...")
    response = requests.post(
        f"{API_URL}/api/matching/workspace/{workspace_id}/match")

    if response.status_code != 200:
        print(f"[ERROR] Matching failed: {response.status_code}")
        print(response.text)
        return

    results = response.json()
    print(f"[OK] Matching complete! Found {len(results)} match(es)\n")

    # Display results
    for i, result in enumerate(results, 1):
        print(f"{'='*80}")
        print(f"MATCH RESULT {i}")
        print(f"{'='*80}")
        print(f"Match ID: {result['id']}")
        print(f"Matched By: {result['matched_by']}")
        print(f"Confidence: {result['match_confidence']}")
        print(f"\nDocuments:")
        print(f"  PO: {result['po_document_id']}")
        print(f"  Invoice: {result['invoice_document_id']}")
        print(
            f"  Delivery Note: {result['delivery_note_document_id'] or 'None'}")
        print(f"\nTotals:")
        print(f"  PO Amount: ${result['total_po_amount']}")
        print(f"  Invoice Amount: ${result['total_invoice_amount']}")
        print(
            f"  Delivery Amount: ${result['total_delivery_amount'] or 'N/A'}")
        print(f"  Difference: ${result['total_difference']}")

        discrepancies = result.get('discrepancies', [])
        print(f"\nDiscrepancies: {len(discrepancies)}")
        if discrepancies:
            for j, disc in enumerate(discrepancies, 1):
                print(
                    f"\n  {j}. {disc['type'].upper()} - {disc['severity'].upper()}")
                print(
                    f"     Item: {disc.get('item_number', 'N/A')} - {disc.get('description', 'N/A')}")
                print(f"     Message: {disc.get('message', 'N/A')}")
                if disc.get('po_value'):
                    print(f"     PO Value: {disc['po_value']}")
                if disc.get('invoice_value'):
                    print(f"     Invoice Value: {disc['invoice_value']}")
                if disc.get('delivery_value'):
                    print(f"     Delivery Value: {disc['delivery_value']}")
        else:
            print("  [OK] No discrepancies found - perfect match!")

        print()

    # Get matching results
    print(f"\n[*] Retrieving matching results...")
    response = requests.get(
        f"{API_URL}/api/matching/workspace/{workspace_id}/results")
    if response.status_code == 200:
        all_results = response.json()
        print(f"[OK] Total matching results in workspace: {len(all_results)}")

    print(f"\n{'='*80}\n")


def main():
    """Test matching with the most recent workspace."""
    print("\n[*] Fetching recent workspace...")
    response = requests.get(f"{API_URL}/api/workspaces")

    if response.status_code != 200 or not response.json():
        print("[ERROR] No workspaces found. Please upload documents first.")
        return

    workspaces = response.json()
    workspace = workspaces[-1]  # Get the most recent
    workspace_id = workspace['id']
    print(f"[OK] Using workspace: {workspace_id}")

    # Check documents
    response = requests.get(
        f"{API_URL}/api/documents/workspace/{workspace_id}")
    if response.status_code == 200:
        documents = response.json()
        print(f"[OK] Found {len(documents)} documents in workspace")
        for doc in documents:
            print(
                f"  - {doc['document_type']}: {doc['file_name']} ({doc['status']})")

    # Test matching
    test_matching(workspace_id)


if __name__ == "__main__":
    main()


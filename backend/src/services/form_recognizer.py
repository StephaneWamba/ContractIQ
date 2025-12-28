from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from typing import Optional, Dict, Any
import io

from src.core.config import settings
from src.models.document import DocumentType


class FormRecognizerService:
    """Azure Form Recognizer service for document extraction"""

    def __init__(self):
        self.client = DocumentAnalysisClient(
            endpoint=settings.AZURE_FORM_RECOGNIZER_ENDPOINT,
            credential=AzureKeyCredential(settings.AZURE_FORM_RECOGNIZER_KEY),
        )

    def analyze_invoice(self, file_content: bytes) -> Dict[str, Any]:
        """Extract data from invoice using pre-built model"""
        try:
            poller = self.client.begin_analyze_document(
                model_id="prebuilt-invoice",
                document=file_content,
            )
            result = poller.result()

            extracted_data = {
                "invoice_number": None,
                "vendor_name": None,
                "vendor_address": None,
                "date": None,
                "total_amount": None,
                "line_items": [],
                "confidence_scores": {},
            }

            # Extract fields from result
            for idx, document in enumerate(result.documents):
                if idx == 0:  # Primary document
                    # Extract invoice number
                    if "InvoiceId" in document.fields:
                        extracted_data["invoice_number"] = document.fields["InvoiceId"].value
                        extracted_data["confidence_scores"]["invoice_number"] = document.fields["InvoiceId"].confidence

                    # Extract vendor name
                    if "VendorName" in document.fields:
                        extracted_data["vendor_name"] = document.fields["VendorName"].value
                        extracted_data["confidence_scores"]["vendor_name"] = document.fields["VendorName"].confidence

                    # Extract vendor address
                    if "VendorAddress" in document.fields:
                        vendor_address = document.fields["VendorAddress"].value
                        if vendor_address:
                            # AddressValue is an object with attributes, not a dict
                            address_parts = []
                            if hasattr(vendor_address, "street_address") and vendor_address.street_address:
                                address_parts.append(vendor_address.street_address)
                            if hasattr(vendor_address, "city") and vendor_address.city:
                                address_parts.append(vendor_address.city)
                            if hasattr(vendor_address, "state") and vendor_address.state:
                                address_parts.append(vendor_address.state)
                            if hasattr(vendor_address, "postal_code") and vendor_address.postal_code:
                                address_parts.append(vendor_address.postal_code)
                            extracted_data["vendor_address"] = ", ".join(address_parts) if address_parts else None
                            extracted_data["confidence_scores"]["vendor_address"] = document.fields["VendorAddress"].confidence

                    # Extract invoice date
                    if "InvoiceDate" in document.fields:
                        extracted_data["date"] = document.fields["InvoiceDate"].value
                        extracted_data["confidence_scores"]["date"] = document.fields["InvoiceDate"].confidence

                    # Extract total amount
                    if "AmountDue" in document.fields:
                        amount = document.fields["AmountDue"].value
                        if amount:
                            extracted_data["total_amount"] = float(amount.amount)
                            extracted_data["confidence_scores"]["total_amount"] = document.fields["AmountDue"].confidence

                    # Extract line items
                    if "Items" in document.fields:
                        items = document.fields["Items"].value
                        if items:
                            for item in items:
                                line_item = {
                                    "item_number": None,
                                    "description": None,
                                    "quantity": None,
                                    "unit_price": None,
                                    "line_total": None,
                                }

                                if "Description" in item.value:
                                    line_item["description"] = item.value["Description"].value

                                if "Quantity" in item.value:
                                    qty = item.value["Quantity"].value
                                    if qty:
                                        line_item["quantity"] = float(qty)

                                if "UnitPrice" in item.value:
                                    price = item.value["UnitPrice"].value
                                    if price:
                                        line_item["unit_price"] = float(price.amount)

                                if "Amount" in item.value:
                                    amount = item.value["Amount"].value
                                    if amount:
                                        line_item["line_total"] = float(amount.amount)

                                extracted_data["line_items"].append(line_item)

            return extracted_data

        except Exception as e:
            raise Exception(f"Failed to analyze invoice: {str(e)}")

    def analyze_purchase_order(self, file_content: bytes) -> Dict[str, Any]:
        """Extract data from purchase order using pre-built model"""
        try:
            # Use general document model for PO (no pre-built PO model)
            poller = self.client.begin_analyze_document(
                model_id="prebuilt-layout",
                document=file_content,
            )
            result = poller.result()

            extracted_data = {
                "po_number": None,
                "vendor_name": None,
                "vendor_address": None,
                "date": None,
                "total_amount": None,
                "line_items": [],
                "confidence_scores": {},
            }

            # Extract from key-value pairs and tables
            for document in result.documents:
                # Try to find PO number in key-value pairs
                for key, field in result.key_value_pairs.items():
                    key_lower = key.lower() if key else ""
                    if "po" in key_lower or "purchase order" in key_lower or "order number" in key_lower:
                        extracted_data["po_number"] = field.value if hasattr(field, "value") else str(field)
                        break

                # Extract from tables (line items)
                for table in result.tables:
                    for row in table.rows:
                        if len(row.cells) >= 4:  # Assuming: description, quantity, price, total
                            line_item = {
                                "item_number": row.cells[0].content if len(row.cells) > 0 else None,
                                "description": row.cells[1].content if len(row.cells) > 1 else None,
                                "quantity": None,
                                "unit_price": None,
                                "line_total": None,
                            }

                            # Try to parse quantities and prices
                            if len(row.cells) > 2:
                                try:
                                    line_item["quantity"] = float(row.cells[2].content)
                                except (ValueError, IndexError):
                                    pass

                            if len(row.cells) > 3:
                                try:
                                    # Remove currency symbols
                                    price_str = row.cells[3].content.replace("$", "").replace(",", "").strip()
                                    line_item["unit_price"] = float(price_str)
                                except (ValueError, IndexError):
                                    pass

                            if len(row.cells) > 4:
                                try:
                                    total_str = row.cells[4].content.replace("$", "").replace(",", "").strip()
                                    line_item["line_total"] = float(total_str)
                                except (ValueError, IndexError):
                                    pass

                            extracted_data["line_items"].append(line_item)

            return extracted_data

        except Exception as e:
            raise Exception(f"Failed to analyze purchase order: {str(e)}")

    def analyze_delivery_note(self, file_content: bytes) -> Dict[str, Any]:
        """Extract data from delivery note using general layout model"""
        try:
            poller = self.client.begin_analyze_document(
                model_id="prebuilt-layout",
                document=file_content,
            )
            result = poller.result()

            extracted_data = {
                "delivery_note_number": None,
                "vendor_name": None,
                "vendor_address": None,
                "date": None,
                "line_items": [],
                "confidence_scores": {},
            }

            # Similar extraction logic as PO
            for document in result.documents:
                # Extract delivery note number
                for key, field in result.key_value_pairs.items():
                    key_lower = key.lower() if key else ""
                    if "delivery" in key_lower or "dn" in key_lower or "note" in key_lower:
                        extracted_data["delivery_note_number"] = field.value if hasattr(field, "value") else str(field)
                        break

                # Extract line items from tables
                for table in result.tables:
                    for row in table.rows:
                        if len(row.cells) >= 3:
                            line_item = {
                                "item_number": row.cells[0].content if len(row.cells) > 0 else None,
                                "description": row.cells[1].content if len(row.cells) > 1 else None,
                                "quantity": None,
                            }

                            if len(row.cells) > 2:
                                try:
                                    line_item["quantity"] = float(row.cells[2].content)
                                except (ValueError, IndexError):
                                    pass

                            extracted_data["line_items"].append(line_item)

            return extracted_data

        except Exception as e:
            raise Exception(f"Failed to analyze delivery note: {str(e)}")

    def extract_document(self, document_type: DocumentType, file_content: bytes) -> Dict[str, Any]:
        """Extract data based on document type"""
        if document_type == DocumentType.INVOICE:
            return self.analyze_invoice(file_content)
        elif document_type == DocumentType.PURCHASE_ORDER:
            return self.analyze_purchase_order(file_content)
        elif document_type == DocumentType.DELIVERY_NOTE:
            return self.analyze_delivery_note(file_content)
        else:
            raise ValueError(f"Unsupported document type: {document_type}")


form_recognizer_service = FormRecognizerService()


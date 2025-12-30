"""
Document Matching & Reconciliation Service

Implements:
- PO number and vendor name matching
- Line item comparison with fuzzy matching
- Three-way reconciliation (PO ↔ Invoice ↔ Delivery Note)
- Discrepancy detection and severity calculation
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional, Tuple
from rapidfuzz import fuzz
from decimal import Decimal
import json

from src.models.document import Document, DocumentType
from src.models.extracted_data import ExtractedData
from src.models.matching import MatchingResult, DiscrepancyType, DiscrepancySeverity


class MatchingService:
    """Service for matching and reconciling documents"""

    def __init__(self, db: Session):
        self.db = db
        # Thresholds for matching
        self.VENDOR_NAME_SIMILARITY_THRESHOLD = 85  # Percentage
        self.ITEM_DESCRIPTION_SIMILARITY_THRESHOLD = 80
        self.PRICE_TOLERANCE = 0.01  # $0.01 tolerance for floating point
        self.QUANTITY_TOLERANCE = 0.01

    def match_documents_in_workspace(self, workspace_id: str) -> List[MatchingResult]:
        """
        Match all documents in a workspace and create matching results.

        Returns:
            List of MatchingResult objects
        """
        # Get all processed documents in workspace
        documents = self.db.query(Document).filter(
            Document.workspace_id == workspace_id,
            Document.status == "PROCESSED"
        ).all()

        # Separate by type
        pos = [d for d in documents if d.document_type ==
               DocumentType.PURCHASE_ORDER]
        invoices = [d for d in documents if d.document_type ==
                    DocumentType.INVOICE]
        delivery_notes = [
            d for d in documents if d.document_type == DocumentType.DELIVERY_NOTE]

        matching_results = []

        # Match PO with Invoice and Delivery Note
        for po in pos:
            po_data = self._get_extracted_data(po.id)
            if not po_data:
                continue

            # Find matching invoice
            matched_invoice = self._find_matching_invoice(
                po, po_data, invoices)

            # Find matching delivery note
            matched_dn = self._find_matching_delivery_note(
                po, po_data, delivery_notes)

            # Create matching result if we have at least PO + Invoice
            if matched_invoice:
                invoice_data = self._get_extracted_data(matched_invoice.id)
                dn_data = self._get_extracted_data(
                    matched_dn.id) if matched_dn else None

                result = self._create_matching_result(
                    workspace_id=workspace_id,
                    po=po,
                    po_data=po_data,
                    invoice=matched_invoice,
                    invoice_data=invoice_data,
                    delivery_note=matched_dn,
                    dn_data=dn_data,
                )
                matching_results.append(result)

        # Handle unmatched invoices (invoices without PO)
        for invoice in invoices:
            # Check if already matched
            already_matched = any(
                mr.invoice_document_id == invoice.id for mr in matching_results
            )
            if not already_matched:
                # Try to match by vendor name only
                invoice_data = self._get_extracted_data(invoice.id)
                if invoice_data and invoice_data.vendor_name:
                    # Find PO with same vendor
                    for po in pos:
                        po_data = self._get_extracted_data(po.id)
                        if po_data and self._vendor_names_match(
                            invoice_data.vendor_name, po_data.vendor_name
                        ):
                            matched_dn = self._find_matching_delivery_note(
                                po, po_data, delivery_notes
                            )
                            dn_data = self._get_extracted_data(
                                matched_dn.id) if matched_dn else None

                            result = self._create_matching_result(
                                workspace_id=workspace_id,
                                po=po,
                                po_data=po_data,
                                invoice=invoice,
                                invoice_data=invoice_data,
                                delivery_note=matched_dn,
                                dn_data=dn_data,
                            )
                            matching_results.append(result)
                            break

        # Save all results
        for result in matching_results:
            self.db.add(result)
        self.db.commit()

        return matching_results

    def _get_extracted_data(self, document_id: str) -> Optional[ExtractedData]:
        """Get extracted data for a document"""
        return self.db.query(ExtractedData).filter(
            ExtractedData.document_id == document_id
        ).first()

    def _find_matching_invoice(
        self, po: Document, po_data: ExtractedData, invoices: List[Document]
    ) -> Optional[Document]:
        """Find matching invoice for a PO"""
        if not po_data:
            return None

        for invoice in invoices:
            invoice_data = self._get_extracted_data(invoice.id)
            if not invoice_data:
                continue

            # Try PO number match first
            if po_data.po_number and invoice_data.po_number:
                if po_data.po_number.strip().upper() == invoice_data.po_number.strip().upper():
                    return invoice

            # Try vendor name match
            if po_data.vendor_name and invoice_data.vendor_name:
                if self._vendor_names_match(po_data.vendor_name, invoice_data.vendor_name):
                    return invoice

        return None

    def _find_matching_delivery_note(
        self, po: Document, po_data: ExtractedData, delivery_notes: List[Document]
    ) -> Optional[Document]:
        """Find matching delivery note for a PO"""
        if not po_data:
            return None

        for dn in delivery_notes:
            dn_data = self._get_extracted_data(dn.id)
            if not dn_data:
                continue

            # Try PO number match
            if po_data.po_number and dn_data.po_number:
                if po_data.po_number.strip().upper() == dn_data.po_number.strip().upper():
                    return dn

            # Try vendor name match
            if po_data.vendor_name and dn_data.vendor_name:
                if self._vendor_names_match(po_data.vendor_name, dn_data.vendor_name):
                    return dn

        return None

    def _vendor_names_match(self, name1: str, name2: str) -> bool:
        """Check if two vendor names match using fuzzy matching"""
        if not name1 or not name2:
            return False

        name1_clean = name1.strip().upper()
        name2_clean = name2.strip().upper()

        # Exact match
        if name1_clean == name2_clean:
            return True

        # Fuzzy match
        similarity = fuzz.ratio(name1_clean, name2_clean)
        return similarity >= self.VENDOR_NAME_SIMILARITY_THRESHOLD

    def _create_matching_result(
        self,
        workspace_id: str,
        po: Document,
        po_data: ExtractedData,
        invoice: Document,
        invoice_data: ExtractedData,
        delivery_note: Optional[Document] = None,
        dn_data: Optional[ExtractedData] = None,
    ) -> MatchingResult:
        """Create a matching result with reconciliation"""

        # Determine how documents were matched
        matched_by = "po_number" if (
            po_data.po_number and invoice_data.po_number and
            po_data.po_number.strip().upper() == invoice_data.po_number.strip().upper()
        ) else "vendor_name"

        # Calculate confidence scores
        confidence_scores = self._calculate_confidence_scores(
            po_data, invoice_data, dn_data, matched_by
        )

        # Perform line item comparison
        discrepancies = self._compare_line_items(
            po_data, invoice_data, dn_data)

        # Check currency mismatch
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(
            f"[CURRENCY CHECK] PO currency: {po_data.currency_code}, "
            f"Invoice currency: {invoice_data.currency_code}"
        )
        
        if po_data.currency_code and invoice_data.currency_code:
            if po_data.currency_code.upper() != invoice_data.currency_code.upper():
                logger.warning(
                    f"[CURRENCY MISMATCH DETECTED] PO={po_data.currency_code}, Invoice={invoice_data.currency_code}"
                )
                discrepancies.append({
                    "type": "currency_mismatch",
                    "severity": DiscrepancySeverity.HIGH.value,
                    "item_number": None,
                    "description": "Currency Mismatch",
                    "po_value": {"currency_code": po_data.currency_code},
                    "invoice_value": {"currency_code": invoice_data.currency_code},
                    "delivery_value": None,
                    "message": f"Currency mismatch: PO={po_data.currency_code}, Invoice={invoice_data.currency_code}",
                })
            else:
                logger.info(f"[CURRENCY CHECK] Currencies match: {po_data.currency_code}")
        else:
            logger.warning(
                f"[CURRENCY CHECK] Missing currency codes - PO: {po_data.currency_code}, Invoice: {invoice_data.currency_code}"
            )

        # Check tax discrepancies
        if po_data.tax_rate is not None and invoice_data.tax_rate is not None:
            tax_rate_diff = abs(po_data.tax_rate - invoice_data.tax_rate)
            if tax_rate_diff > 0.1:  # 0.1% tolerance
                severity = DiscrepancySeverity.CRITICAL if tax_rate_diff > 5.0 else DiscrepancySeverity.HIGH
                discrepancies.append({
                    "type": "tax_rate_mismatch",
                    "severity": severity.value,
                    "item_number": None,
                    "description": "Tax Rate Mismatch",
                    "po_value": {"tax_rate": float(po_data.tax_rate), "tax_amount": float(po_data.tax_amount) if po_data.tax_amount else None},
                    "invoice_value": {"tax_rate": float(invoice_data.tax_rate), "tax_amount": float(invoice_data.tax_amount) if invoice_data.tax_amount else None},
                    "delivery_value": None,
                    "message": f"Tax rate mismatch: PO={po_data.tax_rate:.2f}%, Invoice={invoice_data.tax_rate:.2f}%",
                })

        # Calculate totals - use extracted total_amount if available, otherwise calculate from line items
        # This is faithful to the document: if total_amount is extracted, use it; otherwise, the total IS in the document as sum of line items
        po_total = float(po_data.total_amount) if po_data.total_amount else self._calculate_total_from_line_items(po_data.line_items)
        invoice_total = float(invoice_data.total_amount) if invoice_data.total_amount else self._calculate_total_from_line_items(invoice_data.line_items)
        dn_total = float(dn_data.total_amount) if (dn_data and dn_data.total_amount) else (self._calculate_total_from_line_items(dn_data.line_items) if dn_data and dn_data.line_items else 0.0)

        total_difference = abs(invoice_total - po_total)

        # Get vendor name (prefer PO, fallback to invoice)
        vendor_name = po_data.vendor_name or invoice_data.vendor_name or "Unknown Vendor"
        
        # Create matching result
        result = MatchingResult(
            workspace_id=workspace_id,
            po_document_id=po.id,
            invoice_document_id=invoice.id,
            delivery_note_document_id=delivery_note.id if delivery_note else None,
            match_confidence=json.dumps(confidence_scores),
            matched_by=matched_by,
            total_po_amount=str(po_total),
            total_invoice_amount=str(invoice_total),
            total_delivery_amount=str(dn_total) if dn_total else None,
            total_difference=str(total_difference),
            discrepancies=discrepancies,
        )
        
        # Store vendor_name in match_confidence for now (until we add a proper field)
        confidence_scores["vendor_name"] = vendor_name
        result.match_confidence = json.dumps(confidence_scores)

        return result

    def _calculate_total_from_line_items(self, line_items: List[Dict[str, Any]]) -> float:
        """Calculate total from line items - this is data that IS in the document"""
        if not line_items:
            return 0.0
        total = 0.0
        for item in line_items:
            line_total = item.get("line_total")
            if line_total:
                try:
                    total += float(line_total)
                except (ValueError, TypeError):
                    pass
        return total

    def _calculate_confidence_scores(
        self,
        po_data: ExtractedData,
        invoice_data: ExtractedData,
        dn_data: Optional[ExtractedData],
        matched_by: str,
    ) -> Dict[str, Any]:
        """Calculate confidence scores for matching"""
        scores = {
            "po_number_match": 0,
            "vendor_name_match": 0,
            "overall": 0,
        }

        # PO number match score
        if po_data.po_number and invoice_data.po_number:
            if po_data.po_number.strip().upper() == invoice_data.po_number.strip().upper():
                scores["po_number_match"] = 100
            else:
                scores["po_number_match"] = 0
        else:
            scores["po_number_match"] = 0

        # Vendor name match score
        if po_data.vendor_name and invoice_data.vendor_name:
            similarity = fuzz.ratio(
                po_data.vendor_name.strip().upper(),
                invoice_data.vendor_name.strip().upper()
            )
            scores["vendor_name_match"] = similarity
        else:
            scores["vendor_name_match"] = 0

        # Overall confidence
        if matched_by == "po_number":
            scores["overall"] = scores["po_number_match"]
        else:
            scores["overall"] = scores["vendor_name_match"]

        return scores

    def _compare_line_items(
        self,
        po_data: ExtractedData,
        invoice_data: ExtractedData,
        dn_data: Optional[ExtractedData] = None,
    ) -> List[Dict[str, Any]]:
        """
        Compare line items across documents and detect discrepancies.

        Returns:
            List of discrepancy dictionaries
        """
        discrepancies = []

        po_items = po_data.line_items or []
        invoice_items = invoice_data.line_items or []
        dn_items = dn_data.line_items if dn_data else []

        # Match items between PO and Invoice
        matched_items = self._match_items(
            po_items, invoice_items, "PO", "Invoice")

        # Check for discrepancies in matched items
        for match in matched_items:
            po_item = match["po_item"]
            invoice_item = match["invoice_item"]
            match_score = match["score"]

            # Quantity mismatch
            po_qty = po_item.get("quantity") or 0
            inv_qty = invoice_item.get("quantity") or 0
            if abs(po_qty - inv_qty) > self.QUANTITY_TOLERANCE:
                severity = self._calculate_quantity_discrepancy_severity(
                    po_qty, inv_qty)
                discrepancies.append({
                    "type": DiscrepancyType.QUANTITY_MISMATCH.value,
                    "severity": severity.value,
                    "item_number": po_item.get("item_number") or invoice_item.get("item_number"),
                    "description": po_item.get("description") or invoice_item.get("description"),
                    "po_value": {"quantity": po_qty},
                    "invoice_value": {"quantity": inv_qty},
                    "delivery_value": None,
                    "message": f"Quantity mismatch: PO={po_qty}, Invoice={inv_qty}",
                })

            # Price change
            po_price = po_item.get("unit_price") or 0
            inv_price = invoice_item.get("unit_price") or 0
            if po_price > 0 and inv_price > 0:
                if abs(po_price - inv_price) > self.PRICE_TOLERANCE:
                    severity = self._calculate_price_discrepancy_severity(
                        po_price, inv_price)
                    discrepancies.append({
                        "type": DiscrepancyType.PRICE_CHANGE.value,
                        "severity": severity.value,
                        "item_number": po_item.get("item_number") or invoice_item.get("item_number"),
                        "description": po_item.get("description") or invoice_item.get("description"),
                        "po_value": {"unit_price": po_price},
                        "invoice_value": {"unit_price": inv_price},
                        "delivery_value": None,
                        "message": f"Price change: PO=${po_price:.2f}, Invoice=${inv_price:.2f}",
                    })

            # Description mismatch (low confidence match)
            if match_score < self.ITEM_DESCRIPTION_SIMILARITY_THRESHOLD:
                discrepancies.append({
                    "type": DiscrepancyType.DESCRIPTION_MISMATCH.value,
                    "severity": DiscrepancySeverity.LOW.value,
                    "item_number": po_item.get("item_number") or invoice_item.get("item_number"),
                    "description": po_item.get("description") or invoice_item.get("description"),
                    "po_value": {"description": po_item.get("description")},
                    "invoice_value": {"description": invoice_item.get("description")},
                    "delivery_value": None,
                    "message": f"Description similarity: {match_score}%",
                })

        # Find missing items (in PO but not in Invoice)
        matched_invoice_indices = {
            match["invoice_index"] for match in matched_items}
        for i, po_item in enumerate(po_items):
            if i not in {match["po_index"] for match in matched_items}:
                discrepancies.append({
                    "type": DiscrepancyType.MISSING_ITEM.value,
                    "severity": DiscrepancySeverity.HIGH.value,
                    "item_number": po_item.get("item_number"),
                    "description": po_item.get("description"),
                    "po_value": po_item,
                    "invoice_value": None,
                    "delivery_value": None,
                    "message": f"Item in PO but not in Invoice: {po_item.get('description')}",
                })

        # Find extra items (in Invoice but not in PO)
        matched_po_indices = {match["po_index"] for match in matched_items}
        for i, invoice_item in enumerate(invoice_items):
            if i not in matched_invoice_indices:
                discrepancies.append({
                    "type": DiscrepancyType.EXTRA_ITEM.value,
                    "severity": DiscrepancySeverity.MEDIUM.value,
                    "item_number": invoice_item.get("item_number"),
                    "description": invoice_item.get("description"),
                    "po_value": None,
                    "invoice_value": invoice_item,
                    "delivery_value": None,
                    "message": f"Item in Invoice but not in PO: {invoice_item.get('description')}",
                })

        # Compare with Delivery Note if available
        if dn_items:
            dn_matched_items = self._match_items(
                po_items, dn_items, "PO", "DN")
            for match in dn_matched_items:
                po_item = match["po_item"]
                # The _match_items function returns keys based on source names
                # For "PO" and "DN", it returns "po_item" and "dn_item"
                dn_item = match.get("dn_item")
                if not dn_item:
                    # Fallback if key naming is different
                    continue

                po_qty = po_item.get("quantity") or 0
                dn_qty = dn_item.get("quantity") or 0

                if abs(po_qty - dn_qty) > self.QUANTITY_TOLERANCE:
                    # Update or add discrepancy
                    item_num = po_item.get("item_number")
                    existing = next(
                        (d for d in discrepancies if d.get("item_number") == item_num and d.get(
                            "type") == DiscrepancyType.QUANTITY_MISMATCH.value),
                        None
                    )
                    if existing:
                        existing["delivery_value"] = {"quantity": dn_qty}
                        existing["message"] += f", DN={dn_qty}"
                    else:
                        severity = self._calculate_quantity_discrepancy_severity(
                            po_qty, dn_qty)
                        discrepancies.append({
                            "type": DiscrepancyType.QUANTITY_MISMATCH.value,
                            "severity": severity.value,
                            "item_number": item_num,
                            "description": po_item.get("description"),
                            "po_value": {"quantity": po_qty},
                            "invoice_value": None,
                            "delivery_value": {"quantity": dn_qty},
                            "message": f"Quantity mismatch: PO={po_qty}, DN={dn_qty}",
                        })

        return discrepancies

    def _normalize_item_number(self, item_num: str) -> str:
        """Normalize item numbers by removing leading zeros and handling formats"""
        if not item_num:
            return ""
        item_num = item_num.strip()
        # Try to normalize numeric item numbers (e.g., "013" -> "13")
        try:
            # If it's numeric, convert to int then back to string to remove leading zeros
            normalized = str(int(item_num))
            return normalized
        except ValueError:
            # If not numeric, return as-is (could be alphanumeric like "A001")
            return item_num

    def _match_items(
        self, items1: List[Dict], items2: List[Dict], source1: str, source2: str
    ) -> List[Dict[str, Any]]:
        """
        Match items between two lists using fuzzy matching on descriptions.

        Returns:
            List of match dictionaries with indices, items, and scores
        """
        matches = []
        used_indices_2 = set()

        for i, item1 in enumerate(items1):
            best_match = None
            best_score = 0
            best_index = -1

            desc1 = (item1.get("description") or "").strip()
            item_num1 = (item1.get("item_number") or "").strip()
            normalized_num1 = self._normalize_item_number(item_num1)

            for j, item2 in enumerate(items2):
                if j in used_indices_2:
                    continue

                desc2 = (item2.get("description") or "").strip()
                item_num2 = (item2.get("item_number") or "").strip()
                normalized_num2 = self._normalize_item_number(item_num2)

                # Try normalized item number match first (handles "013" = "13")
                if normalized_num1 and normalized_num2 and normalized_num1 == normalized_num2:
                    best_match = item2
                    best_score = 100
                    best_index = j
                    break

                # Try exact item number match (fallback for non-numeric item numbers)
                if item_num1 and item_num2 and item_num1 == item_num2:
                    best_match = item2
                    best_score = 100
                    best_index = j
                    break

                # Fuzzy match on description
                if desc1 and desc2:
                    score = fuzz.ratio(desc1.upper(), desc2.upper())
                    if score > best_score and score >= self.ITEM_DESCRIPTION_SIMILARITY_THRESHOLD:
                        best_match = item2
                        best_score = score
                        best_index = j

            if best_match:
                matches.append({
                    f"{source1.lower()}_index": i,
                    f"{source1.lower()}_item": item1,
                    f"{source2.lower()}_index": best_index,
                    f"{source2.lower()}_item": best_match,
                    "score": best_score,
                })
                used_indices_2.add(best_index)

        return matches

    def _calculate_quantity_discrepancy_severity(
        self, expected_qty: float, actual_qty: float
    ) -> DiscrepancySeverity:
        """Calculate severity based on quantity difference"""
        if expected_qty == 0:
            return DiscrepancySeverity.MEDIUM

        diff_percentage = abs(expected_qty - actual_qty) / expected_qty * 100

        if diff_percentage >= 50:
            return DiscrepancySeverity.CRITICAL
        elif diff_percentage >= 20:
            return DiscrepancySeverity.HIGH
        elif diff_percentage >= 10:
            return DiscrepancySeverity.MEDIUM
        else:
            return DiscrepancySeverity.LOW

    def _calculate_price_discrepancy_severity(
        self, expected_price: float, actual_price: float
    ) -> DiscrepancySeverity:
        """Calculate severity based on price difference"""
        if expected_price == 0:
            return DiscrepancySeverity.MEDIUM

        diff_percentage = abs(
            expected_price - actual_price) / expected_price * 100

        if diff_percentage >= 20:
            return DiscrepancySeverity.CRITICAL
        elif diff_percentage >= 10:
            return DiscrepancySeverity.HIGH
        elif diff_percentage >= 5:
            return DiscrepancySeverity.MEDIUM
        else:
            return DiscrepancySeverity.LOW

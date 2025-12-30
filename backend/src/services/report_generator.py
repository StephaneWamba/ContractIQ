"""
Report Generation Service

Generates PDF, JSON, and CSV reports for document matching and reconciliation results.
"""
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
import json
import csv
import io

from src.models.matching import MatchingResult
from src.models.document import Document
from src.models.extracted_data import ExtractedData
from src.services.matching import MatchingService


class ReportGenerator:
    """Service for generating reconciliation reports"""

    def __init__(self, db: Session):
        self.db = db

    def generate_pdf_report(self, matching_result_id: str) -> bytes:
        """Generate PDF reconciliation report"""
        # Get matching result
        result = self.db.query(MatchingResult).filter(
            MatchingResult.id == matching_result_id
        ).first()
        
        if not result:
            raise ValueError("Matching result not found")

        # Get related documents and extracted data
        po_data = None
        invoice_data = None
        dn_data = None

        if result.po_document_id:
            po_doc = self.db.query(Document).filter(Document.id == result.po_document_id).first()
            if po_doc:
                po_data = self.db.query(ExtractedData).filter(
                    ExtractedData.document_id == po_doc.id
                ).first()

        if result.invoice_document_id:
            inv_doc = self.db.query(Document).filter(Document.id == result.invoice_document_id).first()
            if inv_doc:
                invoice_data = self.db.query(ExtractedData).filter(
                    ExtractedData.document_id == inv_doc.id
                ).first()

        if result.delivery_note_document_id:
            dn_doc = self.db.query(Document).filter(Document.id == result.delivery_note_document_id).first()
            if dn_doc:
                dn_data = self.db.query(ExtractedData).filter(
                    ExtractedData.document_id == dn_doc.id
                ).first()

        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#000000'),
            spaceAfter=12,
            alignment=TA_CENTER,
        )
        story.append(Paragraph("Document Reconciliation Report", title_style))
        story.append(Spacer(1, 0.15*inch))

        # Parse match_confidence JSON string
        match_conf = result.match_confidence
        if isinstance(match_conf, str):
            try:
                match_conf = json.loads(match_conf)
            except:
                match_conf = {}
        elif match_conf is None:
            match_conf = {}

        # Report metadata
        metadata_data = [
            ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Match Confidence:', f"{match_conf.get('overall', 0):.1f}%"],
            ['Matched By:', result.matched_by.replace('_', ' ').title()],
        ]
        metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#404040')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(metadata_table)
        story.append(Spacer(1, 0.2*inch))

        # Executive Summary
        summary_style = ParagraphStyle(
            'Summary',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#000000'),
            spaceAfter=8,
        )
        story.append(Paragraph("Executive Summary", summary_style))

        total_po = float(result.total_po_amount)
        total_inv = float(result.total_invoice_amount)
        total_dn = float(result.total_delivery_amount) if result.total_delivery_amount else None
        total_diff = float(result.total_difference)

        summary_data = [
            ['Document Type', 'Total Amount'],
            ['Purchase Order', f'${total_po:,.2f}'],
            ['Invoice', f'${total_inv:,.2f}'],
        ]
        if total_dn:
            summary_data.append(['Delivery Note', f'${total_dn:,.2f}'])

        summary_data.append(['Difference', f'${abs(total_diff):,.2f}'])

        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a1a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E5E5')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FAFAFA')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.2*inch))

        # Discrepancies Section
        discrepancies = result.discrepancies
        if isinstance(discrepancies, str):
            try:
                discrepancies = json.loads(discrepancies)
            except:
                discrepancies = []
        elif discrepancies is None:
            discrepancies = []
        
        if discrepancies and len(discrepancies) > 0:
            story.append(Paragraph("Discrepancies", summary_style))
            
            disc_data = [['Type', 'Severity', 'Item', 'Description', 'Message']]
            for disc in discrepancies:
                disc_data.append([
                    disc.get('type', 'N/A').replace('_', ' ').title(),
                    disc.get('severity', 'N/A').upper(),
                    disc.get('item_number', 'N/A') or 'N/A',
                    (disc.get('description', 'N/A') or 'N/A')[:50],
                    (disc.get('message', 'N/A') or 'N/A')[:80],
                ])

            disc_table = Table(disc_data, colWidths=[1*inch, 0.8*inch, 0.8*inch, 1.5*inch, 2.4*inch])
            disc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a1a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E5E5')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FAFAFA')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(disc_table)
            story.append(Spacer(1, 0.2*inch))
        else:
            story.append(Paragraph("No Discrepancies Found - Perfect Match!", summary_style))
            story.append(Spacer(1, 0.2*inch))

        # Line Items Comparison
        if po_data and invoice_data and po_data.line_items and invoice_data.line_items:
            story.append(PageBreak())
            story.append(Paragraph("Line Items Comparison", summary_style))

            # Create comparison table
            items_data = [['Item #', 'Description', 'PO Qty', 'PO Price', 'Inv Qty', 'Inv Price', 'Status']]
            row_colors = []
            
            # Match items and compare
            po_items = {item.get('item_number'): item for item in po_data.line_items if item.get('item_number')}
            inv_items = {item.get('item_number'): item for item in invoice_data.line_items if item.get('item_number')}
            
            all_item_numbers = set(list(po_items.keys()) + list(inv_items.keys()))
            
            for item_num in sorted(all_item_numbers):
                po_item = po_items.get(item_num, {})
                inv_item = inv_items.get(item_num, {})
                
                po_qty = po_item.get('quantity', 0) or 0
                po_price = po_item.get('unit_price', 0) or 0
                inv_qty = inv_item.get('quantity', 0) or 0
                inv_price = inv_item.get('unit_price', 0) or 0
                
                # Determine status and row color
                if not po_item:
                    status = "Extra in Invoice"
                    row_color = colors.HexColor('#FFF3CD')
                elif not inv_item:
                    status = "Missing in Invoice"
                    row_color = colors.HexColor('#F8D7DA')
                elif abs(float(po_qty) - float(inv_qty)) > 0.01 or abs(float(po_price) - float(inv_price)) > 0.01:
                    status = "Mismatch"
                    row_color = colors.HexColor('#FFF3CD')
                else:
                    status = "Match"
                    row_color = colors.white
                
                items_data.append([
                    item_num or 'N/A',
                    (po_item.get('description') or inv_item.get('description') or 'N/A')[:40],
                    f"{float(po_qty):.2f}" if po_item else "-",
                    f"${float(po_price):.2f}" if po_item else "-",
                    f"{float(inv_qty):.2f}" if inv_item else "-",
                    f"${float(inv_price):.2f}" if inv_item else "-",
                    status,
                ])
                row_colors.append(row_color)

            items_table = Table(items_data, colWidths=[0.7*inch, 1.8*inch, 0.7*inch, 0.8*inch, 0.7*inch, 0.8*inch, 1*inch])
            
            # Build table style
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a1a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 1), (5, -1), 'RIGHT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E5E5')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]
            
            # Add row backgrounds
            for idx, row_color in enumerate(row_colors):
                table_style.append(('BACKGROUND', (0, idx + 1), (-1, idx + 1), row_color))
            
            items_table.setStyle(TableStyle(table_style))
            story.append(items_table)

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()

    def generate_json_report(self, matching_result_id: str) -> Dict[str, Any]:
        """Generate JSON report"""
        result = self.db.query(MatchingResult).filter(
            MatchingResult.id == matching_result_id
        ).first()
        
        if not result:
            raise ValueError("Matching result not found")

        # Get related documents
        po_doc = None
        inv_doc = None
        dn_doc = None

        if result.po_document_id:
            po_doc = self.db.query(Document).filter(Document.id == result.po_document_id).first()
        if result.invoice_document_id:
            inv_doc = self.db.query(Document).filter(Document.id == result.invoice_document_id).first()
        if result.delivery_note_document_id:
            dn_doc = self.db.query(Document).filter(Document.id == result.delivery_note_document_id).first()

        # Get extracted data
        po_data = None
        inv_data = None
        dn_data = None

        if po_doc:
            po_data = self.db.query(ExtractedData).filter(ExtractedData.document_id == po_doc.id).first()
        if inv_doc:
            inv_data = self.db.query(ExtractedData).filter(ExtractedData.document_id == inv_doc.id).first()
        if dn_doc:
            dn_data = self.db.query(ExtractedData).filter(ExtractedData.document_id == dn_doc.id).first()

        report = {
            "report_generated_at": datetime.now().isoformat(),
            "matching_result_id": result.id,
            "workspace_id": result.workspace_id,
            "match_confidence": result.match_confidence if isinstance(result.match_confidence, dict) else json.loads(result.match_confidence or "{}"),
            "matched_by": result.matched_by,
            "totals": {
                "po_amount": float(result.total_po_amount),
                "invoice_amount": float(result.total_invoice_amount),
                "delivery_amount": float(result.total_delivery_amount) if result.total_delivery_amount else None,
                "difference": float(result.total_difference),
            },
            "discrepancies": (
                json.loads(result.discrepancies) if isinstance(result.discrepancies, str) 
                else (result.discrepancies or [])
            ),
            "documents": {
                "purchase_order": {
                    "document_id": result.po_document_id,
                    "file_name": po_doc.file_name if po_doc else None,
                    "extracted_data": {
                        "po_number": po_data.po_number if po_data else None,
                        "vendor_name": po_data.vendor_name if po_data else None,
                        "date": po_data.date if po_data else None,
                        "line_items": po_data.line_items if po_data else [],
                    } if po_data else None,
                },
                "invoice": {
                    "document_id": result.invoice_document_id,
                    "file_name": inv_doc.file_name if inv_doc else None,
                    "extracted_data": {
                        "invoice_number": inv_data.invoice_number if inv_data else None,
                        "po_number": inv_data.po_number if inv_data else None,
                        "vendor_name": inv_data.vendor_name if inv_data else None,
                        "date": inv_data.date if inv_data else None,
                        "line_items": inv_data.line_items if inv_data else [],
                    } if inv_data else None,
                },
                "delivery_note": {
                    "document_id": result.delivery_note_document_id,
                    "file_name": dn_doc.file_name if dn_doc else None,
                    "extracted_data": {
                        "delivery_note_number": dn_data.delivery_note_number if dn_data else None,
                        "po_number": dn_data.po_number if dn_data else None,
                        "vendor_name": dn_data.vendor_name if dn_data else None,
                        "date": dn_data.date if dn_data else None,
                        "line_items": dn_data.line_items if dn_data else [],
                    } if dn_data else None,
                } if result.delivery_note_document_id else None,
            },
        }

        return report

    def generate_csv_report(self, matching_result_id: str) -> str:
        """Generate CSV report for line items comparison"""
        result = self.db.query(MatchingResult).filter(
            MatchingResult.id == matching_result_id
        ).first()
        
        if not result:
            raise ValueError("Matching result not found")

        # Get extracted data
        po_data = None
        inv_data = None

        if result.po_document_id:
            po_doc = self.db.query(Document).filter(Document.id == result.po_document_id).first()
            if po_doc:
                po_data = self.db.query(ExtractedData).filter(ExtractedData.document_id == po_doc.id).first()

        if result.invoice_document_id:
            inv_doc = self.db.query(Document).filter(Document.id == result.invoice_document_id).first()
            if inv_doc:
                inv_data = self.db.query(ExtractedData).filter(ExtractedData.document_id == inv_doc.id).first()

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            'Item Number',
            'Description',
            'PO Quantity',
            'PO Unit Price',
            'PO Line Total',
            'Invoice Quantity',
            'Invoice Unit Price',
            'Invoice Line Total',
            'Quantity Difference',
            'Price Difference',
            'Status',
        ])

        # Match and compare items using the same logic as MatchingService
        if po_data and inv_data and po_data.line_items and inv_data.line_items:
            # Use MatchingService to match items (handles item_number and description matching)
            matching_service = MatchingService(self.db)
            matched_items = matching_service._match_items(
                po_data.line_items, 
                inv_data.line_items, 
                "PO", 
                "Invoice"
            )
            
            # Create maps for matched items
            matched_po_indices = {match.get("po_index") for match in matched_items}
            matched_inv_indices = {match.get("invoice_index") for match in matched_items}
            
            # Create a map of PO index -> Invoice item for matched items
            po_to_inv_map = {}
            for match in matched_items:
                po_idx = match.get("po_index")
                if po_idx is not None:
                    po_to_inv_map[po_idx] = match.get("invoice_item", {})
            
            # Process all PO items
            for i, po_item in enumerate(po_data.line_items):
                inv_item = po_to_inv_map.get(i, {})
                
                po_qty = float(po_item.get('quantity', 0) or 0)
                po_price = float(po_item.get('unit_price', 0) or 0)
                po_total = float(po_item.get('line_total', 0) or 0)
                
                inv_qty = float(inv_item.get('quantity', 0) or 0) if inv_item else 0
                inv_price = float(inv_item.get('unit_price', 0) or 0) if inv_item else 0
                inv_total = float(inv_item.get('line_total', 0) or 0) if inv_item else 0
                
                qty_diff = inv_qty - po_qty if inv_item else 0
                price_diff = inv_price - po_price if inv_item else 0
                
                if not inv_item:
                    status = "Missing in Invoice"
                elif abs(qty_diff) > 0.01 or abs(price_diff) > 0.01:
                    status = "Mismatch"
                else:
                    status = "Match"
                
                writer.writerow([
                    po_item.get('item_number') or '',
                    po_item.get('description') or '',
                    po_qty,
                    po_price,
                    po_total,
                    inv_qty if inv_item else '',
                    inv_price if inv_item else '',
                    inv_total if inv_item else '',
                    qty_diff if inv_item else '',
                    price_diff if inv_item else '',
                    status,
                ])
            
            # Process invoice items that weren't matched (extra items)
            for i, inv_item in enumerate(inv_data.line_items):
                if i not in matched_inv_indices:
                    inv_qty = float(inv_item.get('quantity', 0) or 0)
                    inv_price = float(inv_item.get('unit_price', 0) or 0)
                    inv_total = float(inv_item.get('line_total', 0) or 0)
                    
                    writer.writerow([
                        inv_item.get('item_number') or '',
                        inv_item.get('description') or '',
                        '',  # PO Quantity
                        '',  # PO Unit Price
                        '',  # PO Line Total
                        inv_qty,
                        inv_price,
                        inv_total,
                        '',  # Quantity Difference
                        '',  # Price Difference
                        'Extra in Invoice',
                    ])

        # Add discrepancies section
        discrepancies = result.discrepancies
        if isinstance(discrepancies, str):
            try:
                discrepancies = json.loads(discrepancies)
            except json.JSONDecodeError:
                discrepancies = []
        elif discrepancies is None:
            discrepancies = []

        if discrepancies and len(discrepancies) > 0:
            writer.writerow([])  # Empty row separator
            writer.writerow(['=== DISCREPANCIES ==='])
            writer.writerow([
                'Type',
                'Severity',
                'Item Number',
                'Description',
                'Message',
                'PO Value',
                'Invoice Value',
                'Delivery Note Value',
            ])

            for disc in discrepancies:
                # Format values for display
                po_value_str = ''
                inv_value_str = ''
                dn_value_str = ''

                if disc.get('po_value'):
                    po_value_str = ', '.join([f"{k}: {v}" for k, v in disc.get('po_value', {}).items()])
                if disc.get('invoice_value'):
                    inv_value_str = ', '.join([f"{k}: {v}" for k, v in disc.get('invoice_value', {}).items()])
                if disc.get('delivery_value'):
                    dn_value_str = ', '.join([f"{k}: {v}" for k, v in disc.get('delivery_value', {}).items()])

                writer.writerow([
                    disc.get('type', '').replace('_', ' ').title(),
                    disc.get('severity', '').upper(),
                    disc.get('item_number') or '',
                    disc.get('description') or '',
                    disc.get('message', ''),
                    po_value_str,
                    inv_value_str,
                    dn_value_str,
                ])

        output.seek(0)
        return output.getvalue()


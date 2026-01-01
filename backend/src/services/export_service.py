"""
Export Service

Handles exporting clauses, checklists, and contracts in various formats.
"""
from typing import List, Dict, Optional
from datetime import datetime
from io import BytesIO, StringIO
import json
import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
import fitz  # PyMuPDF

from src.models.clause import Clause
from src.models.document import Document


class ExportService:
    """Service for exporting contract analysis results"""

    def __init__(self):
        self.styles = getSampleStyleSheet()

    def export_clauses_json(self, clauses: List[Clause]) -> bytes:
        """Export clauses as JSON"""
        clauses_data = []
        for clause in clauses:
            # Safely get document name
            doc_name = None
            try:
                if clause.document:
                    doc_name = clause.document.name
            except Exception:
                # If document relationship is not loaded, use document_id
                doc_name = str(clause.document_id)
            
            clauses_data.append({
                "id": str(clause.id),
                "document_id": str(clause.document_id),
                "document_name": doc_name,
                "clause_type": clause.clause_type,
                "extracted_text": clause.extracted_text or "",
                "page_number": clause.page_number,
                "section_name": clause.section,
                "risk_score": clause.risk_score or 0,
                "risk_flags": clause.risk_flags or [],
                "risk_reasoning": clause.risk_reasoning or "",
                "created_at": clause.created_at.isoformat() if clause.created_at else None,
            })
        return json.dumps(clauses_data, indent=2, ensure_ascii=False).encode("utf-8")

    def export_clauses_csv(self, clauses: List[Clause]) -> bytes:
        """Export clauses as CSV"""
        # Use StringIO for text-based CSV, then encode to bytes
        buffer = StringIO()
        writer = csv.writer(buffer)
        
        # Header
        writer.writerow([
            "ID",
            "Document Name",
            "Clause Type",
            "Page",
            "Section",
            "Risk Score",
            "Risk Flags",
            "Extracted Text",
            "Risk Reasoning",
        ])
        
        # Data rows
        for clause in clauses:
            risk_flags_str = ", ".join(clause.risk_flags) if clause.risk_flags else ""
            # Safely get document name
            doc_name = ""
            try:
                if clause.document:
                    doc_name = clause.document.name
            except Exception:
                # If document relationship is not loaded, use document_id
                doc_name = str(clause.document_id)
            
            writer.writerow([
                str(clause.id),
                doc_name,
                clause.clause_type,
                clause.page_number,
                clause.section or "",
                clause.risk_score or 0,
                risk_flags_str,
                (clause.extracted_text[:500] + "...") if clause.extracted_text and len(clause.extracted_text) > 500 else (clause.extracted_text or ""),
                clause.risk_reasoning or "",
            ])
        
        buffer.seek(0)
        # Encode string to bytes
        return buffer.getvalue().encode("utf-8")

    def export_review_checklist_pdf(
        self,
        clauses: List[Clause],
        document_name: Optional[str] = None,
    ) -> bytes:
        """Generate PDF review checklist from clauses"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
        )
        story = []

        # Styles
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=self.styles["Heading1"],
            fontSize=18,
            textColor=colors.HexColor("#1a1a1a"),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
        )

        heading_style = ParagraphStyle(
            "HeadingStyle",
            parent=self.styles["Heading2"],
            fontSize=12,
            textColor=colors.HexColor("#2c3e50"),
            spaceAfter=8,
            spaceBefore=12,
            fontName="Helvetica-Bold",
        )

        # Title
        story.append(Paragraph("Contract Review Checklist", title_style))
        if document_name:
            story.append(
                Paragraph(
                    f"<i>Document: {document_name}</i>",
                    ParagraphStyle(
                        "SubtitleStyle",
                        parent=self.styles["Normal"],
                        fontSize=11,
                        textColor=colors.HexColor("#7f8c8d"),
                        alignment=TA_CENTER,
                        spaceAfter=20,
                    ),
                )
            )
        story.append(Spacer(1, 0.2 * inch))

        # Summary statistics
        total_clauses = len(clauses)
        high_risk = sum(1 for c in clauses if (c.risk_score or 0) >= 70)
        medium_risk = sum(1 for c in clauses if 40 <= (c.risk_score or 0) < 70)
        low_risk = sum(1 for c in clauses if (c.risk_score or 0) < 40)

        summary_data = [
            ["Total Clauses", str(total_clauses)],
            ["High Risk (≥70)", str(high_risk)],
            ["Medium Risk (40-69)", str(medium_risk)],
            ["Low Risk (<40)", str(low_risk)],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ecf0f1")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2c3e50")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#bdc3c7")),
                ]
            )
        )
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))

        # Checklist items
        story.append(Paragraph("Review Items", heading_style))

        # Group by risk level
        high_risk_clauses = [c for c in clauses if (c.risk_score or 0) >= 70]
        medium_risk_clauses = [c for c in clauses if 40 <= (c.risk_score or 0) < 70]
        low_risk_clauses = [c for c in clauses if (c.risk_score or 0) < 40]

        # High risk section
        if high_risk_clauses:
            story.append(
                Paragraph(
                    "High Priority (Risk Score ≥ 70)",
                    ParagraphStyle(
                        "RiskHeadingStyle",
                        parent=self.styles["Heading3"],
                        fontSize=11,
                        textColor=colors.HexColor("#e74c3c"),
                        spaceAfter=6,
                        spaceBefore=10,
                        fontName="Helvetica-Bold",
                    ),
                )
            )
            for clause in high_risk_clauses:
                self._add_checklist_item(story, clause, colors.HexColor("#fee"))
                story.append(Spacer(1, 0.1 * inch))

        # Medium risk section
        if medium_risk_clauses:
            story.append(
                Paragraph(
                    "Medium Priority (Risk Score 40-69)",
                    ParagraphStyle(
                        "RiskHeadingStyle",
                        parent=self.styles["Heading3"],
                        fontSize=11,
                        textColor=colors.HexColor("#f39c12"),
                        spaceAfter=6,
                        spaceBefore=10,
                        fontName="Helvetica-Bold",
                    ),
                )
            )
            for clause in medium_risk_clauses:
                self._add_checklist_item(story, clause, colors.HexColor("#fff9e6"))
                story.append(Spacer(1, 0.1 * inch))

        # Low risk section
        if low_risk_clauses:
            story.append(
                Paragraph(
                    "Low Priority (Risk Score < 40)",
                    ParagraphStyle(
                        "RiskHeadingStyle",
                        parent=self.styles["Heading3"],
                        fontSize=11,
                        textColor=colors.HexColor("#27ae60"),
                        spaceAfter=6,
                        spaceBefore=10,
                        fontName="Helvetica-Bold",
                    ),
                )
            )
            for clause in low_risk_clauses:
                self._add_checklist_item(story, clause, colors.HexColor("#e8f8f5"))
                story.append(Spacer(1, 0.1 * inch))

        # Footer
        story.append(Spacer(1, 0.3 * inch))
        footer_text = (
            f"<i>Generated by ContractIQ on "
            f"{datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</i>"
        )
        story.append(
            Paragraph(
                footer_text,
                ParagraphStyle(
                    "FooterStyle",
                    parent=self.styles["Normal"],
                    fontSize=8,
                    textColor=colors.HexColor("#95a5a6"),
                    alignment=TA_CENTER,
                ),
            )
        )

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _add_checklist_item(
        self, story: List, clause: Clause, bg_color: colors.HexColor
    ):
        """Add a checklist item for a clause"""
                # Checkbox and clause info
        item_data = [
            [
                "☐",
                f"<b>{clause.clause_type}</b> (Page {clause.page_number})",
                f"Risk: {clause.risk_score or 0}/100",
            ],
            ["", f"<i>{clause.section or 'N/A'}</i>", ""],
        ]

        if clause.risk_flags:
            flags_text = ", ".join(clause.risk_flags)
            item_data.append(["", f"<b>Flags:</b> {flags_text}", ""])

        if clause.risk_reasoning:
            reasoning_text = (clause.risk_reasoning[:200] + "...") if clause.risk_reasoning and len(clause.risk_reasoning) > 200 else (clause.risk_reasoning or "")
            if reasoning_text:
                item_data.append(["", f"<i>{reasoning_text}</i>", ""])

        item_table = Table(item_data, colWidths=[0.3 * inch, 4.5 * inch, 1.2 * inch])
        item_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), bg_color),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2c3e50")),
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                    ("ALIGN", (1, 0), (1, -1), "LEFT"),
                    ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(item_table)

    def export_highlighted_contract_pdf(
        self, document_path: str, clauses: List[Clause]
    ) -> bytes:
        """
        Export contract PDF with highlighted risky clauses.
        Uses PyMuPDF to add annotations/highlights.
        """
        # Open the original PDF
        doc = fitz.open(document_path)

        # Group clauses by page
        clauses_by_page: Dict[int, List[Clause]] = {}
        for clause in clauses:
            page_num = clause.page_number - 1  # PyMuPDF is 0-indexed
            if page_num not in clauses_by_page:
                clauses_by_page[page_num] = []
            clauses_by_page[page_num].append(clause)

        # Highlight clauses on each page
        for page_num, page_clauses in clauses_by_page.items():
            if page_num >= len(doc):
                continue

            page = doc[page_num]

            for clause in page_clauses:
                # Determine highlight color based on risk score
                risk_score = clause.risk_score or 0
                if risk_score >= 70:
                    color = (1.0, 0.2, 0.2)  # Red for high risk
                elif risk_score >= 40:
                    color = (1.0, 0.8, 0.2)  # Orange for medium risk
                else:
                    color = (1.0, 1.0, 0.2)  # Yellow for low risk

                # Try to find and highlight the clause text
                # Search for the clause text on the page
                text_instances = page.search_for(clause.extracted_text[:100])
                
                if text_instances:
                    # Highlight the first occurrence
                    highlight = page.add_highlight_annot(text_instances[0])
                    highlight.set_colors(stroke=color)
                    highlight.set_opacity(0.3)
                    highlight.update()
                else:
                    # If exact text not found, try to use coordinates if available
                    # For now, we'll skip if text not found
                    pass

        # Save to bytes
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes


"""
Evidence Pack Generator Service

Generates PDF evidence packs from Q&A conversations with citations.
"""
from typing import List, Dict, Optional
from datetime import datetime
from io import BytesIO
import re
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
    KeepTogether,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas

from src.schemas.conversation import CitationResponse


class EvidencePackGenerator:
    """Service for generating evidence pack PDFs from Q&A conversations"""

    def __init__(self):
        self.styles = getSampleStyleSheet()

    def _markdown_to_html(self, markdown_text: str) -> str:
        """
        Convert markdown to HTML that ReportLab can parse.
        ReportLab supports basic HTML tags: <b>, <i>, <u>, <br/>, <p>, etc.
        Preserves spacing and line breaks.
        """
        if not markdown_text:
            return ""

        text = markdown_text

        # Preserve multiple spaces by converting to non-breaking spaces in paragraphs
        # But first, let's handle markdown formatting

        # Convert markdown bold **text** to <b>text</b>
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        # Also handle __text__ for bold
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)

        # Convert markdown italic *text* to <i>text</i> (but not if it's part of **text**)
        # We need to be careful not to match * inside **
        text = re.sub(
            r'(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
        # Also handle _text_ for italic (but not if it's part of __text__)
        text = re.sub(r'(?<!_)_([^_]+?)_(?!_)', r'<i>\1</i>', text)

        # Convert markdown code `text` to <font name="Courier">text</font>
        text = re.sub(r'`([^`]+?)`', r'<font name="Courier">\1</font>', text)

        # Convert markdown headers (do this before splitting lines)
        text = re.sub(r'^### (.+?)$', r'<b>\1</b>', text, flags=re.MULTILINE)
        text = re.sub(
            r'^## (.+?)$', r'<b><font size="14">\1</font></b>', text, flags=re.MULTILINE)
        text = re.sub(
            r'^# (.+?)$', r'<b><font size="16">\1</font></b>', text, flags=re.MULTILINE)

        # Split into lines for processing
        lines = text.split('\n')
        in_list = False
        result_lines = []

        for line in lines:
            # Check for list items
            if re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                # Remove list marker and wrap in <li>
                list_item = re.sub(r'^\s*[-*+]\s+', '', line)
                list_item = re.sub(r'^\s*\d+\.\s+', '', list_item)
                result_lines.append(f'<li>{list_item}</li>')
            else:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                if line.strip():
                    # Preserve the line content, including spaces
                    result_lines.append(f'<p>{line}</p>')
                else:
                    # Empty line - add a break
                    result_lines.append('<br/>')

        if in_list:
            result_lines.append('</ul>')

        # Join without newlines to avoid extra breaks
        text = ''.join(result_lines)

        # Clean up consecutive empty paragraphs (but preserve single breaks)
        text = re.sub(r'<br/><br/>+', '<br/>', text)
        text = re.sub(r'<p>\s*</p>', '', text)

        # Preserve spacing within paragraphs by converting multiple spaces to non-breaking spaces
        # But only within <p> tags to avoid breaking HTML structure
        def preserve_spaces(match):
            para_content = match.group(1)
            # Replace 2+ spaces with non-breaking spaces (but keep single spaces)
            para_content = re.sub(
                r' {2,}', lambda m: '&nbsp;' * len(m.group(0)), para_content)
            return f'<p>{para_content}</p>'

        text = re.sub(r'<p>(.*?)</p>', preserve_spaces, text, flags=re.DOTALL)

        return text

    def generate_evidence_pack(
        self,
        question: str,
        answer: str,
        citations: List[CitationResponse],
        workspace_name: Optional[str] = None,
        conversation_title: Optional[str] = None,
    ) -> bytes:
        """
        Generate a PDF evidence pack containing:
        - Question
        - Answer
        - Supporting evidence (citations with excerpts)

        Args:
            question: The user's question
            answer: The AI-generated answer
            citations: List of citations with excerpts
            workspace_name: Optional workspace name for header
            conversation_title: Optional conversation title

        Returns:
            bytes: PDF content
        """
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

        # Define custom styles
        title_style = ParagraphStyle(
            "EvidencePackTitle",
            parent=self.styles["Heading1"],
            fontSize=20,
            textColor=colors.HexColor("#1a1a1a"),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
        )

        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=self.styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#2c3e50"),
            spaceAfter=8,
            spaceBefore=12,
            fontName="Helvetica-Bold",
        )

        question_style = ParagraphStyle(
            "QuestionStyle",
            parent=self.styles["Normal"],
            fontSize=12,
            textColor=colors.HexColor("#34495e"),
            spaceAfter=10,
            fontName="Helvetica-Bold",
            backColor=colors.HexColor("#ecf0f1"),
            borderPadding=8,
            leftIndent=10,
        )

        answer_style = ParagraphStyle(
            "AnswerStyle",
            parent=self.styles["Normal"],
            fontSize=11,
            textColor=colors.HexColor("#2c3e50"),
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leading=14,
        )

        citation_style = ParagraphStyle(
            "CitationStyle",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#7f8c8d"),
            spaceAfter=6,
            leftIndent=20,
        )

        excerpt_style = ParagraphStyle(
            "ExcerptStyle",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#34495e"),
            spaceAfter=10,
            leftIndent=20,
            alignment=TA_JUSTIFY,
            leading=12,
            backColor=colors.HexColor("#f8f9fa"),
            borderPadding=6,
        )

        # Header
        if workspace_name or conversation_title:
            header_text = []
            if workspace_name:
                header_text.append(f"<b>Workspace:</b> {workspace_name}")
            if conversation_title:
                header_text.append(
                    f"<b>Conversation:</b> {conversation_title}")
            header_text.append(
                f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            header_para = Paragraph(
                "<br/>".join(header_text),
                ParagraphStyle(
                    "HeaderStyle",
                    parent=self.styles["Normal"],
                    fontSize=9,
                    textColor=colors.HexColor("#7f8c8d"),
                    alignment=TA_CENTER,
                ),
            )
            story.append(header_para)
            story.append(Spacer(1, 0.2 * inch))

        # Title
        story.append(Paragraph("Evidence Pack", title_style))
        story.append(Spacer(1, 0.3 * inch))

        # Question Section
        story.append(Paragraph("Question", heading_style))
        story.append(Paragraph(f"<b>Q:</b> {question}", question_style))
        story.append(Spacer(1, 0.2 * inch))

        # Answer Section
        story.append(Paragraph("Answer", heading_style))
        # Clean answer text (remove any invalid source references)
        clean_answer = self._clean_answer_text(answer, len(citations))
        # Convert markdown to HTML for ReportLab
        html_answer = self._markdown_to_html(clean_answer)
        story.append(Paragraph(html_answer, answer_style))
        story.append(Spacer(1, 0.3 * inch))

        # Evidence Section
        if citations:
            story.append(Paragraph("Supporting Evidence", heading_style))
            story.append(Spacer(1, 0.1 * inch))

            for idx, citation in enumerate(citations, 1):
                # Citation header
                citation_header = f"<b>Source {idx}:</b> {citation.document_name} (Page {citation.page_number})"
                if citation.section_name:
                    citation_header += f" • Section: {citation.section_name}"

                story.append(Paragraph(citation_header, citation_style))

                # Excerpt
                if citation.text_excerpt:
                    excerpt_text = self._escape_html(citation.text_excerpt)
                    story.append(Paragraph(f'"{excerpt_text}"', excerpt_style))

                # Similarity score (if available)
                if hasattr(citation, "similarity_score") and citation.similarity_score:
                    score_text = f"<i>Relevance: {citation.similarity_score:.2%}</i>"
                    story.append(
                        Paragraph(
                            score_text,
                            ParagraphStyle(
                                "ScoreStyle",
                                parent=self.styles["Normal"],
                                fontSize=9,
                                textColor=colors.HexColor("#95a5a6"),
                                leftIndent=20,
                                spaceAfter=12,
                            ),
                        )
                    )
                else:
                    story.append(Spacer(1, 0.1 * inch))

                # Add page break between citations if there are many
                if idx < len(citations) and idx % 3 == 0:
                    story.append(Spacer(1, 0.1 * inch))

        # Footer
        story.append(Spacer(1, 0.3 * inch))
        footer_text = (
            f"<i>This evidence pack was generated by ContractIQ on "
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

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _clean_answer_text(self, answer: str, num_sources: int) -> str:
        """Remove invalid source references from answer text, preserving spacing"""
        # Remove references to sources that don't exist
        import re

        # Pattern to match [Source N] or Source N where N > num_sources
        pattern = r'\[Source\s+(\d+)\]|Source\s+(\d+)'

        def replace_source(match):
            source_num = int(match.group(1) or match.group(2))
            if source_num > num_sources:
                return ""  # Remove invalid references
            return match.group(0)  # Keep valid references

        cleaned = re.sub(pattern, replace_source, answer)

        # Only clean up excessive whitespace (3+ spaces, 3+ newlines)
        # Preserve normal spacing and paragraph breaks
        # Replace 3+ spaces with 2 spaces
        cleaned = re.sub(r' {3,}', '  ', cleaned)
        # Replace 3+ newlines with 2
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        # Don't strip - preserve leading/trailing whitespace that might be intentional
        return cleaned

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters for ReportLab"""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def generate_conversation_evidence_pack(
        self,
        conversation_messages: List[Dict],
        workspace_name: Optional[str] = None,
        conversation_title: Optional[str] = None,
    ) -> bytes:
        """
        Generate a PDF evidence pack for an entire conversation with all Q&A pairs.

        Args:
            conversation_messages: List of message dicts with 'role', 'content', 'citations', 'created_at'
            workspace_name: Optional workspace name for header
            conversation_title: Optional conversation title

        Returns:
            bytes: PDF content
        """
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

        # Define custom styles (same as single evidence pack)
        title_style = ParagraphStyle(
            "EvidencePackTitle",
            parent=self.styles["Heading1"],
            fontSize=20,
            textColor=colors.HexColor("#1a1a1a"),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
        )

        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=self.styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#2c3e50"),
            spaceAfter=8,
            spaceBefore=12,
            fontName="Helvetica-Bold",
        )

        question_style = ParagraphStyle(
            "QuestionStyle",
            parent=self.styles["Normal"],
            fontSize=12,
            textColor=colors.HexColor("#34495e"),
            spaceAfter=10,
            fontName="Helvetica-Bold",
            backColor=colors.HexColor("#ecf0f1"),
            borderPadding=8,
            leftIndent=10,
        )

        answer_style = ParagraphStyle(
            "AnswerStyle",
            parent=self.styles["Normal"],
            fontSize=11,
            textColor=colors.HexColor("#2c3e50"),
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leading=14,
        )

        citation_style = ParagraphStyle(
            "CitationStyle",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#7f8c8d"),
            spaceAfter=6,
            leftIndent=20,
        )

        excerpt_style = ParagraphStyle(
            "ExcerptStyle",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#34495e"),
            spaceAfter=10,
            leftIndent=20,
            alignment=TA_JUSTIFY,
            leading=12,
            backColor=colors.HexColor("#f8f9fa"),
            borderPadding=6,
        )

        # Header
        if workspace_name or conversation_title:
            header_text = []
            if workspace_name:
                header_text.append(f"<b>Workspace:</b> {workspace_name}")
            if conversation_title:
                header_text.append(
                    f"<b>Conversation:</b> {conversation_title}")
            header_text.append(
                f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            header_para = Paragraph(
                "<br/>".join(header_text),
                ParagraphStyle(
                    "HeaderStyle",
                    parent=self.styles["Normal"],
                    fontSize=9,
                    textColor=colors.HexColor("#7f8c8d"),
                    alignment=TA_CENTER,
                ),
            )
            story.append(header_para)
            story.append(Spacer(1, 0.2 * inch))

        # Title
        story.append(Paragraph("Conversation Evidence Pack", title_style))
        story.append(Spacer(1, 0.3 * inch))

        # Process messages in pairs (user question, assistant answer)
        qa_pairs = []
        current_question = None

        for msg in conversation_messages:
            if msg.get("role") == "user":
                current_question = msg
            elif msg.get("role") == "assistant" and current_question:
                qa_pairs.append({
                    "question": current_question,
                    "answer": msg
                })
                current_question = None

        # Generate sections for each Q&A pair
        for idx, pair in enumerate(qa_pairs, 1):
            question = pair["question"]
            answer = pair["answer"]

            # Question Section
            story.append(Paragraph(f"Question {idx}", heading_style))
            story.append(
                Paragraph(f"<b>Q:</b> {question.get('content', '')}", question_style))
            story.append(Spacer(1, 0.2 * inch))

            # Answer Section
            story.append(Paragraph(f"Answer {idx}", heading_style))
            answer_content = answer.get("content", "")
            # Clean answer text
            citations = answer.get("citations", [])
            clean_answer = self._clean_answer_text(
                answer_content, len(citations))
            # Convert markdown to HTML
            html_answer = self._markdown_to_html(clean_answer)
            story.append(Paragraph(html_answer, answer_style))
            story.append(Spacer(1, 0.3 * inch))

            # Evidence Section
            if citations:
                story.append(
                    Paragraph(f"Supporting Evidence {idx}", heading_style))
                story.append(Spacer(1, 0.1 * inch))

                for cit_idx, citation in enumerate(citations, 1):
                    # Handle both dict and CitationResponse objects
                    if isinstance(citation, dict):
                        doc_name = citation.get("document_name", "Unknown")
                        page_num = citation.get("page_number", 0)
                        section = citation.get("section_name", "")
                        excerpt = citation.get("text_excerpt", "")
                        similarity = citation.get("similarity_score", 0)
                    else:
                        doc_name = citation.document_name
                        page_num = citation.page_number
                        section = citation.section_name
                        excerpt = citation.text_excerpt
                        similarity = getattr(citation, "similarity_score", 0)

                    # Citation header
                    citation_header = f"<b>Source {cit_idx}:</b> {doc_name} (Page {page_num})"
                    if section:
                        citation_header += f" • Section: {section}"

                    story.append(Paragraph(citation_header, citation_style))

                    # Excerpt
                    if excerpt:
                        excerpt_text = self._escape_html(excerpt)
                        story.append(
                            Paragraph(f'"{excerpt_text}"', excerpt_style))

                    # Similarity score
                    if similarity:
                        score_text = f"<i>Relevance: {similarity:.2%}</i>"
                        story.append(
                            Paragraph(
                                score_text,
                                ParagraphStyle(
                                    "ScoreStyle",
                                    parent=self.styles["Normal"],
                                    fontSize=9,
                                    textColor=colors.HexColor("#95a5a6"),
                                    leftIndent=20,
                                    spaceAfter=12,
                                ),
                            )
                        )
                    else:
                        story.append(Spacer(1, 0.1 * inch))

                story.append(Spacer(1, 0.3 * inch))

            # Add page break between Q&A pairs (except the last one)
            if idx < len(qa_pairs):
                story.append(PageBreak())

        # Footer
        story.append(Spacer(1, 0.3 * inch))
        footer_text = (
            f"<i>This evidence pack was generated by ContractIQ on "
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

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

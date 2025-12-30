import fitz  # PyMuPDF
from typing import Tuple, Optional


def get_pdf_page_count(file_content: bytes) -> int:
    """Get the number of pages in a PDF"""
    try:
        doc = fitz.open(stream=file_content, filetype="pdf")
        page_count = len(doc)
        doc.close()
        return page_count
    except Exception as e:
        raise Exception(f"Failed to get PDF page count: {str(e)}")


def validate_pdf(file_content: bytes, max_pages: int = 100) -> Tuple[bool, Optional[str]]:
    """Validate PDF file"""
    try:
        doc = fitz.open(stream=file_content, filetype="pdf")
        page_count = len(doc)

        if page_count > max_pages:
            doc.close()
            return False, f"PDF has {page_count} pages, maximum allowed is {max_pages}"

        doc.close()
        return True, None
    except Exception as e:
        return False, f"Invalid PDF file: {str(e)}"


def extract_text_from_pdf(file_content: bytes, page_range: Optional[Tuple[int, int]] = None) -> str:
    """Extract text from PDF, optionally from specific page range"""
    try:
        doc = fitz.open(stream=file_content, filetype="pdf")
        text_parts = []

        start_page = page_range[0] if page_range else 0
        end_page = page_range[1] if page_range else len(doc)

        for page_num in range(start_page, min(end_page, len(doc))):
            page = doc[page_num]
            text_parts.append(page.get_text())

        doc.close()
        return "\n".join(text_parts)
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")



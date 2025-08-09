import pdfplumber
from typing import Optional

def pdf_to_text(file_path: str) -> Optional[str]:
    """
    Extract text from a PDF resume using pdfplumber.
    Args:
        file_path (str): Path to the PDF file
    Returns:
        str: Extracted text or None if failed
    """
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip() if text else None
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return None

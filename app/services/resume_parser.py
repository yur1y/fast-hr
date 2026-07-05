import logging
import os

logger = logging.getLogger(__name__)


async def extract_text_from_resume(filename: str, content: bytes) -> str:
    suffix = os.path.splitext(filename)[1].lower()
    if suffix == ".pdf":
        from pymupdf import fitz

        doc = fitz.open(stream=content, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    if suffix == ".docx":
        import io

        from docx import Document

        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    if suffix == ".txt":
        return content.decode("utf-8", errors="ignore")
    raise ValueError(f"Unsupported resume format: {suffix}")

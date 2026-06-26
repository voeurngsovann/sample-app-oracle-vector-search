"""
chunker.py  –  File parsing + text chunking
Supports: PDF, DOCX, TXT, MD, CSV
"""
from __future__ import annotations

import csv
import io
import re


def extract_text_from_pdf(data: bytes) -> str:
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    doc = fitz.open(stream=data, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def extract_text_from_docx(data: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(data))
    return "\n".join(para.text for para in doc.paragraphs)


def extract_text_from_txt(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def extract_text_from_csv(data: bytes) -> str:
    """
    Convert CSV rows into natural-language sentences for meaningful embeddings.

    Each row becomes: "Column1 is Value1. Column2 is Value2. Column3 is Value3."

    This produces far better semantic search results than storing raw
    comma-separated values, because the embedding model can understand
    "Status is Active" but not "Active,,,,".

    Empty cells are skipped to keep sentences clean.
    Rows with no non-empty cells are skipped entirely.
    """
    text = data.decode("utf-8", errors="replace")

    # Try comma first, fall back to semicolon and tab
    for delimiter in (",", ";", "\t"):
        sample = text[:2048]
        if sample.count(delimiter) >= sample.count("\n"):
            break

    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    sentences: list[str] = []

    for row in reader:
        parts = [
            f"{col.strip()} is {val.strip()}"
            for col, val in row.items()
            if col and val and val.strip()
        ]
        if parts:
            sentences.append(". ".join(parts) + ".")

    if not sentences:
        # Fallback: return raw text if CSV parsing produced nothing
        return text

    return "\n".join(sentences)


EXTRACTORS = {
    ".pdf":  extract_text_from_pdf,
    ".docx": extract_text_from_docx,
    ".txt":  extract_text_from_txt,
    ".md":   extract_text_from_txt,
    ".csv":  extract_text_from_csv,
}

SUPPORTED_EXTENSIONS = tuple(EXTRACTORS)


def extract_text(filename: str, data: bytes) -> str:
    ext = "." + filename.rsplit(".", 1)[-1].lower()
    fn = EXTRACTORS.get(ext)
    if fn is None:
        raise ValueError(
            f"Unsupported file type: {ext}. "
            f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    return fn(data)


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """
    Split text into overlapping word-windows.
    chunk_size and overlap are in words — maps predictably to VARCHAR2(4000).
    """
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split()

    if not words:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if len(chunk.encode("utf-8")) > 3900:
            chunk = chunk.encode("utf-8")[:3900].decode("utf-8", errors="ignore")
        chunks.append(chunk)
        if end == len(words):
            break
        start += chunk_size - overlap

    return chunks

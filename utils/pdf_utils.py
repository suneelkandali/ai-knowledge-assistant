from typing import TypedDict

import pymupdf


class PageText(TypedDict):
    page: int
    text: str


class TextChunk(TypedDict):
    text: str
    page: int
    chunk: int


def extract_pages_from_pdf(pdf_bytes: bytes) -> list[PageText]:
    """Extract text from each page of a PDF."""

    try:
        document = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise RuntimeError(
            "The PDF could not be opened. Ensure the file is "
            "a valid PDF. "
            f"Original error: {exc}"
        ) from exc

    pages: list[PageText] = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text()

        if text and text.strip():
            pages.append(
                {
                    "page": page_number,
                    "text": text.strip(),
                }
            )

    return pages


def chunk_pages(
    pages: list[PageText],
    chunk_size: int = 900,
    overlap: int = 150,
) -> list[TextChunk]:
    """Split page text into overlapping chunks."""

    if not pages:
        return []

    chunks: list[TextChunk] = []
    chunk_index = 0

    for page in pages:
        text = page["text"]
        page_number = page["page"]
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            if chunk_text.strip():
                chunks.append(
                    {
                        "text": chunk_text.strip(),
                        "page": page_number,
                        "chunk": chunk_index,
                    }
                )
                chunk_index += 1

            start += chunk_size - overlap

    return chunks


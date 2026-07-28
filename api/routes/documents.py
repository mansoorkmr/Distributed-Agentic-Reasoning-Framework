"""
Distributed Agentic Reasoning Framework (DARF)

Document Routes

Provides secure document ingestion endpoints for the DARF framework.
"""

from __future__ import annotations

import io
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile
from pypdf import PdfReader

from documents.document_store import document_store


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

# ============================================================
# CONFIGURATION
# ============================================================

MAX_PDF_SIZE = 20 * 1024 * 1024  # 20 MB


# ============================================================
# POST /documents/upload
# ============================================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
):
    """
    Upload and extract text from a PDF document.

    This endpoint currently performs:
    - PDF validation
    - File-size validation
    - Text extraction
    - Basic document metadata generation

    Vector indexing is handled separately.
    """

    filename = file.filename or "document.pdf"

    # --------------------------------------------------------
    # FILE TYPE VALIDATION
    # --------------------------------------------------------

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF documents are supported.",
        )

    if file.content_type not in (
        "application/pdf",
        "application/octet-stream",
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF content type.",
        )

    # --------------------------------------------------------
    # READ FILE
    # --------------------------------------------------------

    try:
        contents = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Unable to read uploaded document.",
        ) from exc
    finally:
        await file.close()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty.",
        )

    if len(contents) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF exceeds the maximum allowed size of 20 MB.",
        )

    # --------------------------------------------------------
    # PDF EXTRACTION
    # --------------------------------------------------------

    try:
        reader = PdfReader(io.BytesIO(contents))

        page_texts: list[str] = []

        for page in reader.pages:
            text = page.extract_text() or ""

            if text.strip():
                page_texts.append(text.strip())

        extracted_text = "\n\n".join(page_texts)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Unable to parse the uploaded PDF.",
        ) from exc

    if not extracted_text.strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "No extractable text was found in the PDF. "
                "The document may contain scanned images only."
            ),
        )

    # --------------------------------------------------------
    # DOCUMENT METADATA
    # --------------------------------------------------------

    document_id = str(uuid.uuid4())
    
    try:
        chunk_count = document_store.add_document(
            document_id=document_id,
            filename=filename,
            text=extracted_text,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="PDF text was extracted but document indexing failed.",
        ) from exc

    return {
        "success": True,
        "message": "PDF processed and indexed successfully.",
        "document_id": document_id,
        "filename": filename,
        "content_type": file.content_type,
        "size_bytes": len(contents),
        "pages": len(reader.pages),
        "characters": len(extracted_text),
        "chunks": chunk_count,
        "indexed": True,
    }


# ============================================================
# GET /documents/{document_id}/search
# ============================================================

@router.get("/{document_id}/search")
def search_document(
    document_id: str,
    query: str,
    top_k: int = 5,
):
    """
    Retrieve semantically relevant chunks from an indexed PDF.
    """

    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty.",
        )

    if not document_store.has_document(document_id):
        raise HTTPException(
            status_code=404,
            detail="Document not found in the active document store.",
        )

    try:
        results = document_store.search(
            document_id=document_id,
            query=query,
            top_k=top_k,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Document retrieval failed.",
        ) from exc

    return {
        "success": True,
        "document_id": document_id,
        "query": query,
        "results": results,
        "result_count": len(results),
    }
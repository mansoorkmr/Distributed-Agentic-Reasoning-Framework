"""
Distributed Agentic Reasoning Framework (DARF)

Document Store

Provides isolated in-memory document storage and semantic retrieval
for uploaded PDF documents.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Dict, List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


@dataclass
class DocumentIndex:
    """Vector index and text chunks belonging to one document."""

    filename: str
    index: faiss.IndexFlatL2
    chunks: List[str] = field(default_factory=list)


class DocumentStore:
    """
    Semantic document store isolated from conversational memory.
    """

    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1200,
        chunk_overlap: int = 200,
    ) -> None:
        self.embedding_model_name = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.embedder = SentenceTransformer(embedding_model)

        dimension = self.embedder.get_sentence_embedding_dimension()

        if dimension is None:
            raise RuntimeError(
                "Unable to determine embedding dimension."
            )

        self.dimension = int(dimension)
        self.documents: Dict[str, DocumentIndex] = {}
        self.lock = threading.RLock()

    def chunk_text(self, text: str) -> List[str]:
        """Split document text into overlapping chunks."""

        text = text.strip()

        if not text:
            return []

        chunks: List[str] = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= len(text):
                break

            start = max(end - self.chunk_overlap, start + 1)

        return chunks

    def add_document(
        self,
        document_id: str,
        filename: str,
        text: str,
    ) -> int:
        """Chunk, embed and index an uploaded document."""

        chunks = self.chunk_text(text)

        if not chunks:
            raise ValueError("Document contains no indexable text.")

        embeddings = self.embedder.encode(
            chunks,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        vectors = np.asarray(
            embeddings,
            dtype="float32",
        )

        index = faiss.IndexFlatL2(self.dimension)
        index.add(vectors)

        with self.lock:
            self.documents[document_id] = DocumentIndex(
                filename=filename,
                index=index,
                chunks=chunks,
            )

        return len(chunks)

    def search(
        self,
        document_id: str,
        query: str,
        top_k: int = 5,
    ) -> List[str]:
        """Retrieve relevant chunks from one uploaded document."""

        with self.lock:
            document = self.documents.get(document_id)

        if document is None:
            raise KeyError(
                f"Unknown document '{document_id}'."
            )

        if not query.strip():
            return []

        query_embedding = self.embedder.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        vector = np.asarray(
            query_embedding,
            dtype="float32",
        )

        k = min(top_k, len(document.chunks))

        _, indices = document.index.search(vector, k)

        results: List[str] = []

        for index_position in indices[0]:
            if 0 <= index_position < len(document.chunks):
                results.append(
                    document.chunks[index_position]
                )

        return results

    def has_document(self, document_id: str) -> bool:
        with self.lock:
            return document_id in self.documents

    def document_count(self) -> int:
        with self.lock:
            return len(self.documents)

    def chunk_count(self, document_id: str) -> int:
        with self.lock:
            document = self.documents.get(document_id)

            if document is None:
                return 0

            return len(document.chunks)


# Shared document store for the running backend process.
document_store = DocumentStore()
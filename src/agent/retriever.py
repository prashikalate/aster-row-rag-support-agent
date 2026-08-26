from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer

from .loader import Document, load_documents


@dataclass
class SearchResult:
    document: Document
    score: float
    adjusted_score: float


class KnowledgeBase:
    def __init__(self, knowledge_base_path: str):
        self.documents = load_documents(knowledge_base_path)

        if not self.documents:
            raise ValueError("Knowledge base is empty")

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        texts = [
            f"{document.title}\n"
            f"{document.heading}\n"
            f"{document.content}"
            for document in self.documents
        ]

        self.embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )

    def _authority_bonus(self, document: Document) -> float:
        """
        Prefer current authoritative content over legacy/internal content.
        This affects ranking, but never changes the original source text.
        """

        bonus = 0.0

        status = document.status.lower()
        document_type = document.document_type.lower()

        if status == "active":
            bonus += 0.15
        elif status in {"legacy", "superseded", "inactive"}:
            bonus -= 0.15

        if document_type == "policy":
            bonus += 0.10
        elif document_type in {"internal", "internal_note"}:
            bonus -= 0.20

        return bonus

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )[0]

        scores = np.dot(self.embeddings, query_embedding)

        candidates = []

        for index, score in enumerate(scores):
            document = self.documents[index]

            adjusted_score = (
                float(score)
                + self._authority_bonus(document)
            )

            candidates.append(
                SearchResult(
                    document=document,
                    score=float(score),
                    adjusted_score=adjusted_score,
                )
            )

        candidates.sort(
            key=lambda result: result.adjusted_score,
            reverse=True
        )

        return candidates[:top_k]
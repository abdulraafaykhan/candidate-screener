"""RAG retriever for sourcing context chunks."""

from dataclasses import dataclass
from hashlib import sha256

from chromadb import PersistentClient
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from backend.config import settings
from backend.core.resume_parser import ResumeData


@dataclass(frozen=True)
class RetrievedChunk:
    """Retrieved chunk structure."""

    text: str
    source: str
    page: int
    relevance_score: float


class RAGRetriever:
    """Retrieve context chunks for interview generation."""

    def __init__(self) -> None:
        """Initialize embeddings and ChromaDB client."""

        self._embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        self._client = PersistentClient(path=settings.chroma_persist_path)

    def retrieve(self, query: str, role: str, k: int = 5) -> list[RetrievedChunk]:
        """Retrieve top-k relevant chunks for a query."""

        vector_store = Chroma(
            collection_name=f"role_{role}",
            client=self._client,
            embedding_function=self._embeddings,
            collection_metadata={"hnsw:space": "cosine"},
        )
        results = vector_store.similarity_search_with_relevance_scores(query, k=k)
        chunks: list[RetrievedChunk] = []
        for doc, score in results:
            metadata = doc.metadata
            chunks.append(
                RetrievedChunk(
                    text=doc.page_content,
                    source=str(metadata.get("source_file", "")),
                    page=int(metadata.get("page_number", 0)),
                    relevance_score=float(score),
                )
            )
        return chunks

    def build_interview_query(self, resume_data: ResumeData, role: str) -> list[str]:
        """Generate targeted queries based on resume data and role."""

        top_skills = resume_data.skills[:5]
        queries: list[str] = []
        for skill in top_skills:
            queries.append(f"{skill} interview questions for {role}")
        if not queries:
            queries.append(f"core fundamentals for {role}")
        if resume_data.domains:
            queries.append(f"{resume_data.domains[0]} fundamentals")
        return queries[:5]

    def get_context_for_generation(self, resume_data: ResumeData, role: str) -> str:
        """Retrieve and deduplicate context for question generation."""

        queries = self.build_interview_query(resume_data, role)
        deduped_chunks: list[RetrievedChunk] = []
        seen_hashes: set[str] = set()
        for query in queries:
            for chunk in self.retrieve(query, role):
                content_hash = sha256(chunk.text.encode("utf-8")).hexdigest()
                if content_hash in seen_hashes:
                    continue
                seen_hashes.add(content_hash)
                deduped_chunks.append(chunk)
        combined = [chunk.text for chunk in deduped_chunks]
        return "\n\n".join(combined)

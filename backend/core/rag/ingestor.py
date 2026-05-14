"""Knowledge base ingestion for RAG."""

from dataclasses import dataclass
from pathlib import Path

from chromadb import PersistentClient
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from backend.config import settings


@dataclass(frozen=True)
class CollectionStats:
    """Collection stats for a role."""

    role: str
    chunk_count: int


class KnowledgeBaseIngestor:
    """Ingest knowledge base PDFs into ChromaDB."""

    def __init__(self) -> None:
        """Initialize embeddings and ChromaDB client."""

        self._embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        self._client = PersistentClient(path=settings.chroma_persist_path)

    def ingest_for_role(self, role: str, pdf_paths: list[str]) -> int:
        """Ingest PDFs for a specific role into ChromaDB."""

        if not pdf_paths:
            return 0

        collection_name = f"role_{role}"
        vector_store = Chroma(
            collection_name=collection_name,
            client=self._client,
            embedding_function=self._embeddings,
            collection_metadata={"hnsw:space": "cosine"},
        )

        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
        total_chunks = 0

        for pdf_path in pdf_paths:
            loader = PyMuPDFLoader(pdf_path)
            documents = loader.load()
            chunks = splitter.split_documents(documents)
            for index, chunk in enumerate(chunks):
                chunk.metadata.update(
                    {
                        "source_file": Path(pdf_path).name,
                        "page_number": chunk.metadata.get("page", 0),
                        "role": role,
                        "chunk_index": index,
                    }
                )
            vector_store.add_documents(chunks)
            total_chunks += len(chunks)

        return total_chunks

    def get_collection_stats(self) -> dict[str, int]:
        """Return per-role chunk counts for all collections."""

        stats: dict[str, int] = {}
        for collection in self._client.list_collections():
            count = collection.count()
            stats[collection.name] = count
        return stats


def list_pdf_files(raw_dir: str) -> list[str]:
    """List PDF files in the knowledge base raw directory."""

    return [str(path) for path in Path(raw_dir).glob("*.pdf")]

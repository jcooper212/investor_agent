# ABOUTME: ChromaDB vector store configuration and management
# ABOUTME: Handles document embedding, storage, and retrieval for RAG pipeline

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from dotenv import load_dotenv

load_dotenv()


class VectorStore:
    """Manages the ChromaDB vector store for UBS House View reports and SEC filings."""

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: str = "investment_research",
    ):
        """
        Initialize the vector store.

        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the ChromaDB collection
        """
        self.persist_directory = persist_directory or os.getenv(
            "CHROMA_PERSIST_DIR", "./data/chroma_db"
        )
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        self.collection_name = collection_name

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        # Set up OpenAI embedding function
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large"),
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "Investment research documents and reports"},
        )

        print(f"✅ ChromaDB initialized at: {self.persist_directory}")
        print(f"✅ Collection '{self.collection_name}' ready")
        print(f"   Documents in collection: {self.collection.count()}")

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ) -> None:
        """
        Add documents to the vector store.

        Args:
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: List of unique document IDs
        """
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        print(f"✅ Added {len(documents)} documents to collection")

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Query the vector store.

        Args:
            query_text: Query string
            n_results: Number of results to return
            where: Optional metadata filter

        Returns:
            Query results with documents, distances, and metadata
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
        )
        return results

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        return {
            "name": self.collection_name,
            "count": self.collection.count(),
            "persist_directory": self.persist_directory,
        }

    def reset_collection(self) -> None:
        """Reset the collection (delete all documents)."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "Investment research documents and reports"},
        )
        print(f"✅ Collection '{self.collection_name}' reset")


class DocumentProcessor:
    """Processes PDF documents for ingestion into the vector store."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        Initialize the document processor.

        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def load_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Load and process a PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of document chunks with metadata
        """
        print(f"📄 Loading PDF: {pdf_path}")

        # Load PDF
        loader = PyMuPDFLoader(pdf_path)
        pages = loader.load()

        # Extract metadata
        pdf_name = Path(pdf_path).stem
        source_type = self._infer_source_type(pdf_name)

        # Split into chunks
        chunks = []
        for page_num, page in enumerate(pages):
            page_chunks = self.text_splitter.split_text(page.page_content)

            for chunk_num, chunk_text in enumerate(page_chunks):
                chunk_id = f"{pdf_name}_page{page_num}_chunk{chunk_num}"
                chunks.append(
                    {
                        "id": chunk_id,
                        "text": chunk_text,
                        "metadata": {
                            "source": pdf_name,
                            "source_type": source_type,
                            "page": page_num,
                            "chunk": chunk_num,
                            "file_path": pdf_path,
                        },
                    }
                )

        print(f"✅ Processed {len(pages)} pages into {len(chunks)} chunks")
        return chunks

    def _infer_source_type(self, filename: str) -> str:
        """Infer the type of document from filename."""
        filename_lower = filename.lower()

        if "ubs" in filename_lower or "house_view" in filename_lower:
            return "ubs_house_view"
        elif "10-k" in filename_lower or "10k" in filename_lower:
            return "sec_10k"
        elif "10-q" in filename_lower or "10q" in filename_lower:
            return "sec_10q"
        else:
            return "unknown"


def ingest_pdfs_to_vectorstore(
    pdf_directory: str,
    vector_store: VectorStore,
    processor: DocumentProcessor,
) -> Dict[str, Any]:
    """
    Ingest all PDFs from a directory into the vector store.

    Args:
        pdf_directory: Directory containing PDF files
        vector_store: VectorStore instance
        processor: DocumentProcessor instance

    Returns:
        Ingestion statistics
    """
    pdf_dir = Path(pdf_directory)
    pdf_files = list(pdf_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"⚠️  No PDF files found in {pdf_directory}")
        return {"total_files": 0, "total_chunks": 0}

    print(f"\n🚀 Starting ingestion of {len(pdf_files)} PDF files...")

    all_documents = []
    all_metadatas = []
    all_ids = []

    for pdf_file in pdf_files:
        try:
            chunks = processor.load_pdf(str(pdf_file))

            for chunk in chunks:
                all_documents.append(chunk["text"])
                all_metadatas.append(chunk["metadata"])
                all_ids.append(chunk["id"])

        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {e}")
            continue

    if all_documents:
        vector_store.add_documents(all_documents, all_metadatas, all_ids)

    stats = {
        "total_files": len(pdf_files),
        "total_chunks": len(all_documents),
        "collection_stats": vector_store.get_collection_stats(),
    }

    print(f"\n✅ Ingestion complete!")
    print(f"   Files processed: {stats['total_files']}")
    print(f"   Total chunks: {stats['total_chunks']}")

    return stats


if __name__ == "__main__":
    # Test the vector store setup
    print("🧪 Testing ChromaDB setup...")

    vector_store = VectorStore()
    processor = DocumentProcessor()

    print("\n" + "=" * 60)
    print("ChromaDB Configuration Test Complete!")
    print("=" * 60)

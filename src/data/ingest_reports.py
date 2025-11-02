# ABOUTME: Script to ingest UBS House View reports into ChromaDB
# ABOUTME: Processes PDFs, creates embeddings, and loads into vector store

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.vector_store import VectorStore, DocumentProcessor, ingest_pdfs_to_vectorstore


def main():
    """Main ingestion workflow."""
    print("\n" + "=" * 70)
    print("UBS House View Reports - Vector Store Ingestion")
    print("=" * 70 + "\n")

    # Initialize components
    print("🔧 Initializing components...")
    vector_store = VectorStore()
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)

    # Ingest PDFs
    pdf_directory = "./data/pdfs"
    stats = ingest_pdfs_to_vectorstore(pdf_directory, vector_store, processor)

    # Display final statistics
    print("\n" + "=" * 70)
    print("Ingestion Complete - Final Statistics")
    print("=" * 70)
    print(f"📁 PDF Files Processed: {stats['total_files']}")
    print(f"📄 Total Chunks Created: {stats['total_chunks']}")
    print(f"💾 ChromaDB Collection: {stats['collection_stats']['name']}")
    print(f"📊 Documents in Collection: {stats['collection_stats']['count']}")
    print(f"📍 Persist Directory: {stats['collection_stats']['persist_directory']}")
    print("=" * 70 + "\n")

    # Test a sample query
    print("🧪 Testing sample query...")
    query_text = "What is UBS's view on US equities?"
    results = vector_store.query(query_text, n_results=3)

    print(f"\nQuery: '{query_text}'")
    print(f"Results found: {len(results['documents'][0])}\n")

    for i, (doc, distance, metadata) in enumerate(
        zip(
            results["documents"][0],
            results["distances"][0],
            results["metadatas"][0],
        )
    ):
        print(f"Result {i+1}:")
        print(f"  Source: {metadata['source']}")
        print(f"  Page: {metadata['page']}")
        print(f"  Distance: {distance:.4f}")
        print(f"  Text preview: {doc[:200]}...")
        print()

    print("✅ Ingestion and testing complete!")


if __name__ == "__main__":
    main()

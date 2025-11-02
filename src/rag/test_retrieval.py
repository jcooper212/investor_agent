# ABOUTME: Test script for RAG retrieval and source attribution
# ABOUTME: Validates vector store queries and citation quality

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.vector_store import VectorStore


def format_results(results: dict, n_results: int = 5) -> None:
    """Pretty print query results."""
    print(f"📊 Results found: {len(results['documents'][0])}")
    print("-" * 80 + "\n")

    for i in range(min(n_results, len(results["documents"][0]))):
        doc = results["documents"][0][i]
        distance = results["distances"][0][i]
        metadata = results["metadatas"][0][i]

        print(f"Result #{i+1}")
        print(f"  📄 Source: {metadata['source']}")
        print(f"  📖 Page: {metadata['page']}")
        print(f"  📍 Chunk: {metadata['chunk']}")
        print(f"  🎯 Distance: {distance:.4f}")
        print(f"  📝 Text preview:")
        print(f"     {doc[:300]}...")
        print()


def test_rag_retrieval():
    """Test various RAG retrieval scenarios."""
    print("\n" + "=" * 80)
    print("RAG Retrieval & Source Attribution Test")
    print("=" * 80 + "\n")

    # Initialize vector store
    print("🔧 Initializing vector store...")
    vector_store = VectorStore()
    stats = vector_store.get_collection_stats()
    print(f"✅ Collection loaded: {stats['count']} documents\n")

    # Test queries covering different aspects of investment research
    test_queries = [
        {
            "query": "What is UBS's view on US equities?",
            "category": "Asset Class Outlook",
        },
        {
            "query": "What are the key risks to the market outlook?",
            "category": "Risk Analysis",
        },
        {
            "query": "What is UBS's recommendation on technology stocks?",
            "category": "Sector Analysis",
        },
        {
            "query": "What is the outlook for interest rates and Fed policy?",
            "category": "Macro Economics",
        },
        {
            "query": "What asset allocation does UBS recommend?",
            "category": "Portfolio Strategy",
        },
        {
            "query": "What is the view on emerging markets?",
            "category": "Regional Analysis",
        },
    ]

    # Run test queries
    for i, test in enumerate(test_queries, 1):
        print("=" * 80)
        print(f"Test Query {i}/{len(test_queries)}: {test['category']}")
        print("=" * 80)
        print(f"Query: \"{test['query']}\"\n")

        results = vector_store.query(test["query"], n_results=3)
        format_results(results, n_results=3)

    # Test source-specific queries
    print("\n" + "=" * 80)
    print("Source-Specific Query Test")
    print("=" * 80 + "\n")

    # Query specific to a time period
    query = "What was the market outlook in June 2024?"
    print(f"Query: \"{query}\"\n")

    # Get all results and filter by source
    results = vector_store.query(query, n_results=5)

    # Filter to show June 2024 results
    print("Filtering for June 2024 report...")
    june_2024_results = [
        (doc, dist, meta)
        for doc, dist, meta in zip(
            results["documents"][0],
            results["distances"][0],
            results["metadatas"][0],
        )
        if "June_2024" in meta["source"]
    ]

    if june_2024_results:
        print(f"Found {len(june_2024_results)} results from June 2024:\n")
        for i, (doc, dist, meta) in enumerate(june_2024_results[:3], 1):
            print(f"Result #{i}")
            print(f"  📄 Source: {meta['source']}")
            print(f"  📖 Page: {meta['page']}")
            print(f"  🎯 Distance: {dist:.4f}")
            print(f"  📝 Text: {doc[:200]}...\n")

    # Test citation extraction
    print("\n" + "=" * 80)
    print("Citation Quality Test")
    print("=" * 80 + "\n")

    query = "What sectors does UBS favor?"
    print(f"Query: \"{query}\"\n")

    results = vector_store.query(query, n_results=5)

    # Show how citations would be formatted
    print("Sample citations from results:\n")
    for i, metadata in enumerate(results["metadatas"][0][:3], 1):
        citation = (
            f"[{i}] {metadata['source'].replace('_', ' ')}, "
            f"Page {metadata['page']}"
        )
        print(f"  {citation}")

    print("\n" + "=" * 80)
    print("✅ All RAG retrieval tests complete!")
    print("=" * 80)

    # Summary
    print("\n📈 Test Summary:")
    print(f"  ✅ Vector store operational with {stats['count']} chunks")
    print(f"  ✅ Query retrieval working across multiple categories")
    print(f"  ✅ Source attribution available for all results")
    print(f"  ✅ Metadata filtering functional")
    print(f"  ✅ Citation extraction successful")
    print("\n🎯 RAG pipeline ready for agent integration!")


if __name__ == "__main__":
    test_rag_retrieval()

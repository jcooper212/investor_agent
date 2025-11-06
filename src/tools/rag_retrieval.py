# ABOUTME: RAG retrieval tool for querying UBS House View reports and SEC filings
# ABOUTME: Wraps VectorStore queries for AutoGen agent function calling

from typing import Dict, Any, Optional, List
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.rag.vector_store import VectorStore


class RAGRetrieval:
    """
    RAG retrieval tool for the investment research agent.
    Provides access to UBS House View reports and SEC filings via vector search.
    """

    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize the RAG retrieval tool.

        Args:
            vector_store: Optional existing VectorStore instance.
                         If None, creates a new one.
        """
        self.vector_store = vector_store or VectorStore()

    def search_investment_research(
        self,
        query: str,
        n_results: int = 5,
        source_filter: Optional[str] = None,
    ) -> str:
        """
        Search UBS House View reports and SEC filings for investment research insights.

        Use this tool when you need to answer questions about:
        - Market outlook and economic conditions
        - Asset allocation recommendations
        - Sector analysis and stock recommendations
        - Risk factors and market risks
        - Investment strategy and portfolio positioning
        - Regional market views (US, Europe, Asia, Emerging Markets)
        - Fed policy and interest rate outlook

        Args:
            query: The investment research question or topic to search for.
                  Examples: "What is UBS's view on US equities?",
                           "What are the key risks to the market outlook?",
                           "What is the outlook for interest rates?"
            n_results: Number of relevant document chunks to return (default: 5)
            source_filter: Optional filter to search only specific sources.
                          Examples: "ubs_house_view", "sec_10k"

        Returns:
            A formatted string containing relevant excerpts from research reports
            with source citations and page numbers.
        """
        try:
            # Build metadata filter if source specified
            where_filter = None
            if source_filter:
                where_filter = {"source_type": source_filter}

            # Query vector store
            results = self.vector_store.query(
                query_text=query,
                n_results=n_results,
                where=where_filter,
            )

            # Format results
            if not results or not results.get("documents") or not results["documents"][0]:
                return (
                    "No relevant information found in the research database. "
                    "The query may be outside the scope of available reports."
                )

            formatted_output = self._format_results(results)
            return formatted_output

        except Exception as e:
            error_msg = (
                f"Error searching research database: {str(e)}\n"
                "Please try rephrasing your question or contact support."
            )
            print(f"❌ RAG Retrieval Error: {e}")
            return error_msg

    def _format_results(self, results: Dict[str, Any]) -> str:
        """
        Format vector store results into readable text with citations.

        Args:
            results: Raw results from VectorStore.query()

        Returns:
            Formatted string with excerpts and citations
        """
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        formatted_text = "# Research Findings\n\n"
        formatted_text += "Here are relevant excerpts from investment research reports:\n\n"

        for i, (doc, metadata, distance) in enumerate(
            zip(documents, metadatas, distances), start=1
        ):
            source = metadata.get("source", "Unknown")
            page = metadata.get("page", "N/A")
            source_type = metadata.get("source_type", "document")

            # Format source name
            source_display = self._format_source_name(source, source_type)

            # Add excerpt with citation
            formatted_text += f"## Excerpt {i}\n"
            formatted_text += f"**Source:** {source_display} (Page {page})\n"
            formatted_text += f"**Relevance Score:** {1 - distance:.2f}\n\n"
            formatted_text += f"{doc}\n\n"
            formatted_text += "---\n\n"

        # Add guidance for citing sources
        formatted_text += (
            "\n**Note:** When answering the user's question, cite specific sources "
            "by referencing the document name and page number from above. "
            "For example: 'According to UBS House View March 2025 (Page 5)...'\n"
        )

        return formatted_text

    def _format_source_name(self, source: str, source_type: str) -> str:
        """
        Convert filename to readable source name.

        Args:
            source: Raw source filename
            source_type: Type of document (ubs_house_view, sec_10k, etc.)

        Returns:
            Formatted, human-readable source name
        """
        # Remove common prefixes/suffixes
        source = source.replace("_", " ").replace("-", " ")

        # Capitalize and clean up
        if source_type == "ubs_house_view":
            # e.g., "UBS House View June 2025"
            return source.replace("UBS", "UBS").title()
        elif source_type == "sec_10k":
            # e.g., "Apple Inc. 10-K Filing"
            return f"{source.title()} (SEC Filing)"
        else:
            return source.title()

    def get_available_sources(self) -> List[str]:
        """
        Get list of available source types in the database.

        Returns:
            List of source type strings (e.g., ["ubs_house_view", "sec_10k"])
        """
        stats = self.vector_store.get_collection_stats()
        return [
            "ubs_house_view",
            "sec_10k",
            "sec_10q",
        ]  # Known source types


def create_rag_tool_function(vector_store: Optional[VectorStore] = None):
    """
    Create a RAG retrieval function for use with AutoGen.

    This factory function returns a callable that AutoGen can register as a tool.

    Args:
        vector_store: Optional existing VectorStore instance

    Returns:
        Callable function that performs RAG retrieval
    """
    rag = RAGRetrieval(vector_store)

    def search_investment_research(query: str, n_results: int = 5) -> str:
        """
        Search UBS House View reports and SEC filings for investment research insights.

        Use this tool when you need to answer questions about:
        - Market outlook and economic conditions
        - Asset allocation recommendations
        - Sector analysis and stock recommendations
        - Risk factors and market risks
        - Investment strategy and portfolio positioning
        - Regional market views (US, Europe, Asia, Emerging Markets)
        - Fed policy and interest rate outlook

        Args:
            query: The investment research question or topic to search for
            n_results: Number of relevant excerpts to return (default: 5)

        Returns:
            Formatted research findings with source citations
        """
        return rag.search_investment_research(query, n_results)

    return search_investment_research


if __name__ == "__main__":
    # Test the RAG retrieval tool
    print("🧪 Testing RAG Retrieval Tool...\n")

    rag = RAGRetrieval()

    # Test query
    test_query = "What is UBS's view on US equities?"
    print(f"Query: {test_query}\n")
    print("=" * 80)

    result = rag.search_investment_research(test_query, n_results=3)
    print(result)

    print("\n" + "=" * 80)
    print("✅ RAG Retrieval Tool test complete!")

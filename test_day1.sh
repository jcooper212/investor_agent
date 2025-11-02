#!/bin/bash
# ABOUTME: End-to-end test script for Day 1 RAG pipeline
# ABOUTME: Validates download, ingestion, and retrieval components

set -e  # Exit on error

echo "========================================================================"
echo "Day 1 RAG Pipeline - End-to-End Test"
echo "========================================================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run: uv venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copy .env.example to .env and add your API keys."
    echo "   cp .env.example .env"
    exit 1
fi

# Check OpenAI API key
echo "🔑 Checking OpenAI API key..."
source .env
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ OPENAI_API_KEY not set in .env file"
    exit 1
fi
echo "✅ OpenAI API key found"
echo ""

# Step 1: Download PDFs
echo "========================================================================"
echo "Step 1: Downloading UBS House View Reports"
echo "========================================================================"
python src/data/download_ubs_reports.py
echo ""

# Check if PDFs were downloaded
PDF_COUNT=$(ls data/pdfs/*.pdf 2>/dev/null | wc -l | tr -d ' ')
if [ "$PDF_COUNT" -lt 4 ]; then
    echo "❌ Expected 4 PDFs, found $PDF_COUNT"
    exit 1
fi
echo "✅ All PDFs downloaded"
echo ""

# Step 2: Ingest into ChromaDB
echo "========================================================================"
echo "Step 2: Ingesting Reports into ChromaDB"
echo "========================================================================"
python src/data/ingest_reports.py
echo ""

# Check if ChromaDB was created
if [ ! -d "data/chroma_db" ]; then
    echo "❌ ChromaDB directory not created"
    exit 1
fi
echo "✅ ChromaDB created"
echo ""

# Step 3: Test retrieval
echo "========================================================================"
echo "Step 3: Testing RAG Retrieval"
echo "========================================================================"
python src/rag/test_retrieval.py
echo ""

# Final summary
echo "========================================================================"
echo "✅ Day 1 Test Complete - All Systems Operational!"
echo "========================================================================"
echo ""
echo "📊 Summary:"
echo "   ✅ Virtual environment active"
echo "   ✅ API keys configured"
echo "   ✅ 4 UBS reports downloaded"
echo "   ✅ ChromaDB vector store populated"
echo "   ✅ RAG retrieval tested across 6 categories"
echo ""
echo "🎯 Ready for Day 2: Agent Development"
echo ""

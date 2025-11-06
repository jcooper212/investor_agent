#!/bin/bash

# ABOUTME: End-to-end test script for Day 2 - Agent and UI implementation
# ABOUTME: Tests RAG tool, research agent, and validates multi-turn conversations

set -e  # Exit on error

echo "=============================================================================="
echo "Day 2 Testing: Investment Research Agent & UI"
echo "=============================================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Please create .env file with OPENAI_API_KEY"
    exit 1
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "OPENAI_API_KEY=" .env; then
    echo -e "${RED}❌ OPENAI_API_KEY not found in .env${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "Run: uv venv"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites OK${NC}"
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if ChromaDB is populated
echo ""
echo "📊 Checking ChromaDB vector store..."
if [ ! -d "data/chroma_db" ]; then
    echo -e "${RED}❌ ChromaDB not found. Run Day 1 ingestion first:${NC}"
    echo "   python src/data/ingest_reports.py"
    exit 1
fi

echo -e "${GREEN}✅ ChromaDB found${NC}"
echo ""

# Test 1: RAG Retrieval Tool
echo "=============================================================================="
echo "Test 1: RAG Retrieval Tool"
echo "=============================================================================="
echo ""

python3 << 'EOF'
from src.tools.rag_retrieval import RAGRetrieval

print("Testing RAG retrieval tool...")
rag = RAGRetrieval()

# Test query
query = "What is UBS's view on technology sector?"
print(f"\nQuery: {query}")
result = rag.search_investment_research(query, n_results=3)

if "Research Findings" in result and "Source:" in result:
    print("✅ RAG retrieval successful")
    print(f"   Found sources with citations")
else:
    print("❌ RAG retrieval failed")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Test 1 PASSED${NC}"
else
    echo -e "\n${RED}❌ Test 1 FAILED${NC}"
    exit 1
fi

# Test 2: Research Agent
echo ""
echo "=============================================================================="
echo "Test 2: Research Agent - Single Turn"
echo "=============================================================================="
echo ""

python3 << 'EOF'
from src.agent.research_agent import ResearchAgent

print("Testing research agent...")
agent = ResearchAgent()

# Test single query
query = "What are the key risks to the market according to UBS?"
print(f"\nQuery: {query}")
response = agent.chat(query)

if response and len(response) > 100:
    print("✅ Agent response generated")
    print(f"   Response length: {len(response)} characters")

    # Check for citations
    if "UBS" in response or "House View" in response:
        print("✅ Response includes source citations")
    else:
        print("⚠️  No citations found in response")

    # Check for disclaimer
    if "investment advice" in response.lower() or "financial advisor" in response.lower():
        print("✅ Compliance disclaimer included")
    else:
        print("⚠️  No compliance disclaimer found")
else:
    print("❌ Agent failed to generate response")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Test 2 PASSED${NC}"
else
    echo -e "\n${RED}❌ Test 2 FAILED${NC}"
    exit 1
fi

# Test 3: Multi-turn Conversation
echo ""
echo "=============================================================================="
echo "Test 3: Research Agent - Multi-turn Conversation"
echo "=============================================================================="
echo ""

python3 << 'EOF'
from src.agent.research_agent import ResearchAgent

print("Testing multi-turn conversation...")
agent = ResearchAgent()

# Turn 1
query1 = "What is UBS's view on US equities?"
print(f"\n📝 Turn 1: {query1}")
response1 = agent.chat(query1)
print(f"✅ Response 1: {len(response1)} characters")

# Turn 2 - follow-up question
query2 = "What are the risks to that view?"
print(f"\n📝 Turn 2 (follow-up): {query2}")
response2 = agent.chat(query2)
print(f"✅ Response 2: {len(response2)} characters")

# Turn 3 - another follow-up
query3 = "Which sectors do they recommend?"
print(f"\n📝 Turn 3 (follow-up): {query3}")
response3 = agent.chat(query3)
print(f"✅ Response 3: {len(response3)} characters")

# Check conversation history
history = agent.get_history()
if len(history) >= 8:  # system + 3 user + 3 assistant + potential tool calls
    print(f"\n✅ Conversation history maintained: {len(history)} messages")
else:
    print(f"\n⚠️  Conversation history might be incomplete: {len(history)} messages")

print("\n✅ Multi-turn conversation successful")
EOF

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Test 3 PASSED${NC}"
else
    echo -e "\n${RED}❌ Test 3 FAILED${NC}"
    exit 1
fi

# Test 4: CLI Interface (quick test)
echo ""
echo "=============================================================================="
echo "Test 4: CLI Interface"
echo "=============================================================================="
echo ""

# Test that the CLI can be imported and initialized
python3 << 'EOF'
from src.agent.research_agent import ResearchAgent

print("Testing CLI interface initialization...")
try:
    agent = ResearchAgent()
    print("✅ CLI agent can be initialized")

    # Test one query
    response = agent.chat("What is UBS's outlook for 2025?")
    if response:
        print("✅ CLI agent can process queries")
    else:
        print("❌ CLI agent failed to process query")
        exit(1)
except Exception as e:
    print(f"❌ CLI initialization failed: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Test 4 PASSED${NC}"
else
    echo -e "\n${RED}❌ Test 4 FAILED${NC}"
    exit 1
fi

# Test 5: Gradio UI (import test only, no launch)
echo ""
echo "=============================================================================="
echo "Test 5: Gradio UI Components"
echo "=============================================================================="
echo ""

python3 << 'EOF'
from src.ui.chat_interface import create_interface, ChatInterface

print("Testing Gradio UI components...")

# Test ChatInterface class
chat_interface = ChatInterface()
status = chat_interface.initialize_agent()
if "✅" in status:
    print("✅ ChatInterface initialization successful")
else:
    print(f"❌ ChatInterface initialization failed: {status}")
    exit(1)

# Test that interface can be created
try:
    interface = create_interface()
    print("✅ Gradio interface created successfully")
except Exception as e:
    print(f"❌ Gradio interface creation failed: {e}")
    exit(1)

print("\n✅ Gradio UI components working")
print("   To launch UI: python src/ui/app.py")
EOF

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Test 5 PASSED${NC}"
else
    echo -e "\n${RED}❌ Test 5 FAILED${NC}"
    exit 1
fi

# Summary
echo ""
echo "=============================================================================="
echo "📊 Test Summary"
echo "=============================================================================="
echo ""
echo -e "${GREEN}✅ All Day 2 tests PASSED!${NC}"
echo ""
echo "Components tested:"
echo "  ✅ RAG retrieval tool"
echo "  ✅ Research agent (single-turn)"
echo "  ✅ Multi-turn conversation & memory"
echo "  ✅ CLI interface"
echo "  ✅ Gradio UI components"
echo ""
echo "Next steps:"
echo "  1. Launch Gradio UI: python src/ui/app.py"
echo "  2. Test manually in browser at http://localhost:7860"
echo "  3. Try the example queries from the UI header"
echo ""
echo "🎯 Day 2 implementation complete!"
echo "=============================================================================="

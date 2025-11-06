# Investment Research Agent - Arklex Demo

An AI-powered investment research Q&A agent that uses UBS House View reports to answer questions about market outlook, asset allocation, and investment strategy. Built for Arklex testing demonstration.

## Overview

This project demonstrates:
- **RAG Pipeline**: ChromaDB vector store with OpenAI embeddings
- **Multi-turn Conversations**: Context-aware investment research assistant
- **Source Attribution**: All answers cite specific UBS reports
- **Testing Surface**: Designed for Arklex vs LLM-as-judge comparison

## Project Status

### ✅ Day 1 Complete (RAG Pipeline)
- UBS House View data ingestion (4 reports, 523 chunks)
- ChromaDB vector store operational
- Retrieval and source attribution tested
- Ready for agent development

### ✅ Day 2 Complete (Agent Development)
- Investment research agent with OpenAI function calling
- RAG tool integration with automatic source citations
- Multi-turn conversation memory
- Compliance disclaimers built-in
- Full-featured Gradio web UI with citations panel
- CLI interface for testing
- Automated test suite (test_day2.sh)

### ✅ Day 3 Complete (Evaluation & API)
- 15 test questions with ground truth (5 categories)
- LLM-as-judge evaluator (GPT-4 based)
- OpenAI Evals-style runner (deterministic grading)
- Comparison analysis tool with recommendations
- FastAPI REST API (7 endpoints)
- CLI evaluation runner
- Automated test suite (test_day3.sh)
- Comprehensive documentation

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- OpenAI API key
- [uv](https://github.com/astral-sh/uv) package manager (or pip)

### One-Time Setup

**Step 1: Clone and Install**
```bash
cd investor_agent

# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate     # On Windows

# Install all dependencies
uv pip install -e .
```

**Step 2: Configure API Key**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

**Step 3: Download Data & Setup Vector Store**
```bash
# Download UBS reports (one-time, ~7.6 MB)
python src/data/download_ubs_reports.py

# Ingest into vector store (one-time, ~2 minutes)
python src/data/ingest_reports.py

# Verify setup
./test_day1.sh
```

---

## 📱 Running the Agent

### Option 1: Gradio Web UI (Recommended)

**Launch the web interface:**
```bash
python src/ui/app.py
```

**Then open:** http://localhost:7860

**What you get:**
- 💬 Chat interface with conversation history
- 📚 Source citations panel (right side)
- 🔧 Tool call debug view
- 🗑️ Clear conversation button
- 💾 Export conversation to JSON

**Try these queries:**
- "What is UBS's view on US equities?"
- "What are the risks to that view?"
- "Which sectors do they recommend?"

---

### Option 2: Command Line Interface

**For quick testing:**
```bash
python src/agent/research_agent.py
```

**CLI Commands:**
- Type your question and press Enter
- `history` - View conversation
- `clear` - Reset conversation
- `export` - Save to JSON
- `quit` - Exit

---

### Option 3: FastAPI REST API

**Start the API server:**
```bash
python src/api/main.py
```

**API Documentation:** http://localhost:8000/docs

**Quick test:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is UBS'\''s view on US equities?"}'
```

---

## 🧪 Testing & Validation

### Run All Tests

**Test each component:**
```bash
# Day 1: RAG Pipeline
./test_day1.sh

# Day 2: Agent & UI
./test_day2.sh

# Day 3: Evaluation & API
./test_day3.sh
```

### Manual Testing Flows

**Test Flow 1: Asset Class Deep Dive**
```
1. Ask: "What is UBS's view on US equities?"
2. Follow-up: "Why are they bullish?"
3. Follow-up: "What are the risks?"
4. Verify: Citations with page numbers, multi-turn memory
```

**Test Flow 2: Edge Cases**
```
1. Ask: "What is UBS's view on cryptocurrency?"
   Expected: "No relevant information found..."
2. Ask: "Will the market crash next week?"
   Expected: Cannot make short-term predictions
```

---

## 📊 Evaluation (Optional - Costs ~$1.15)

### Cost Breakdown
- **LLM-as-Judge**: ~$0.80 (30 API calls)
- **OpenAI Evals**: ~$0.35 (15 API calls)
- **Both**: ~$1.15 total
- **Time**: 10-15 minutes

### Run Evaluations

```bash
# Run both evaluators and compare
python src/eval/run_evaluation.py --compare
```

This will:
1. Run the agent on all 15 test questions
2. Evaluate with LLM-as-judge (GPT-4)
3. Evaluate with OpenAI Evals (deterministic)
4. Save results to `data/eval_results/`

**Output:**
```
✅ Evaluation Complete!
   LLM Judge Results: data/eval_results/llm_judge_results.json
   OpenAI Evals Results: data/eval_results/openai_evals_results.json
```

### Generate Comparison Report

```bash
python src/eval/compare_evaluators.py
```

**Output:** `data/eval_results/comparison_report.md`

This report analyzes:
- Overall scores comparison
- Category-by-category breakdown
- Consistency analysis (variance)
- Edge case handling
- **Recommendations**: Which evaluator for what use case

---

## 🔬 Advanced: Evaluation Details

### Test Categories (15 questions total)
1. **Factual Recall** (3): Direct facts from reports
2. **Synthesis** (3): Multi-document reasoning
3. **Risk Analysis** (3): Understanding downside scenarios
4. **Comparative** (3): Comparing asset classes
5. **Edge Cases** (3): Out-of-scope handling

### Evaluator Comparison

| Dimension | LLM-as-Judge | OpenAI Evals | Winner |
|-----------|--------------|--------------|--------|
| **Nuanced Evaluation** | ✅ Excellent | ❌ Limited | LLM |
| **Consistency** | ❌ Variable | ✅ Deterministic | Evals |
| **Cost** | $0.80 | $0.35 | Evals |
| **Speed** | 8-10 min | 3-5 min | Evals |
| **Debugging** | ✅ Detailed reasoning | ❌ No reasoning | LLM |
| **Regression Testing** | ❌ Inconsistent | ✅ Reliable | Evals |

**Recommendation**: Use both
- OpenAI Evals for CI/CD
- LLM-as-Judge for deep analysis
- **Arklex** for what neither provides (test generation, adversarial probing)

---

## 🎯 Key Features Verification

**Multi-turn Memory:**
```
User: "What's UBS's view on tech stocks?"
Agent: [Provides answer with sources]
User: "What about healthcare?"
Agent: [Should understand we're still talking about sectors]
```

**Source Attribution:**
Every response should cite sources like:
- "According to UBS House View March 2025 (Page 22)..."
- Check citations panel shows matching sources

**Compliance:**
Responses about investment advice should include:
- "This information is based on research reports and should not be considered personalized investment advice..."

**Error Handling:**
Ask: `What is UBS's view on cryptocurrency?`
- Should say: "No relevant information found..." (not in reports)

---

## Day 3: Evaluation & API

### Step 1: Run Infrastructure Tests

First, verify the evaluation infrastructure is working:

```bash
./test_day3.sh
```

**Expected Output:**
```
✅ All Day 3 tests PASSED!

Components tested:
  ✅ Test questions (15 questions across 5 categories)
  ✅ LLM-as-judge evaluator
  ✅ OpenAI Evals runner
  ✅ FastAPI models
  ✅ FastAPI server (7 endpoints)
  ✅ CLI evaluation runner
  ✅ Comparison tool
```

---

### Step 2: Run Evaluations (Optional - Costs API Calls)

**Warning:** Running evaluations will make ~30-45 OpenAI API calls and take 10-15 minutes.

#### Run Both Evaluators:
```bash
python src/eval/run_evaluation.py --compare
```

This will:
- Run the agent on all 15 test questions
- Evaluate with LLM-as-judge (GPT-4)
- Evaluate with OpenAI Evals (deterministic)
- Save results to `data/eval_results/`

#### Run Individual Evaluators:
```bash
# LLM-as-judge only
python src/eval/run_evaluation.py --evaluator llm-judge

# OpenAI Evals only
python src/eval/run_evaluation.py --evaluator openai-evals
```

---

### Step 3: Generate Comparison Report

After running evaluations, generate the analysis:

```bash
python src/eval/compare_evaluators.py
```

**Output:** `data/eval_results/comparison_report.md`

This report includes:
- Overall score comparison
- Category-by-category breakdown
- Consistency analysis
- Edge case handling
- **Recommendations** on which evaluator to use for what

---

### Step 4: Launch FastAPI Server

Start the REST API:

```bash
python src/api/main.py
```

**API Documentation:** http://localhost:8000/docs

**Available Endpoints:**
- `POST /api/v1/query` - Single query to agent
- `POST /api/v1/conversation` - Multi-turn conversation
- `POST /api/v1/evaluate/llm-judge` - Run LLM-as-judge eval
- `POST /api/v1/evaluate/openai-evals` - Run OpenAI Evals
- `GET /api/v1/evaluate/compare` - Compare evaluators
- `GET /api/v1/health` - Health check
- `GET /api/v1/stats` - System statistics

**Example API Call:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is UBS'\''s view on US equities?"}'
```

---

## Project Structure

```
investor_agent/
├── src/
│   ├── agent/              # Agent logic (Day 2) ✅
│   │   ├── __init__.py
│   │   └── research_agent.py
│   ├── data/               # Data download and ingestion ✅
│   │   ├── download_ubs_reports.py
│   │   └── ingest_reports.py
│   ├── rag/                # RAG pipeline ✅
│   │   ├── __init__.py
│   │   ├── vector_store.py
│   │   └── test_retrieval.py
│   ├── tools/              # Agent tools (Day 2) ✅
│   │   ├── __init__.py
│   │   └── rag_retrieval.py
│   └── ui/                 # Gradio interface (Day 2) ✅
│       ├── __init__.py
│       ├── chat_interface.py
│       └── app.py
│
├── data/
│   ├── pdfs/               # UBS House View PDFs (gitignored)
│   └── chroma_db/          # Vector embeddings (gitignored)
│
├── FinRobot/               # Cloned from AI4Finance-Foundation
├── tests/                  # Test suite (Day 3)
│
├── .env                    # Environment config (gitignored)
├── .gitignore
├── pyproject.toml          # Dependencies
├── arklex_demo_spec.md     # Full project specification
└── README.md               # This file
```

---

## Data Sources

### UBS House View Reports
- **June 2024**: Post-election market outlook
- **November 2024**: Year-end positioning
- **March 2025**: Q1 2025 strategy update
- **April 2025**: Latest market views

**Coverage:**
- US Equities, International Equities, Emerging Markets
- Fixed Income (Treasuries, Credit, Municipals)
- Commodities, Real Estate, Currencies
- Sector analysis (Technology, Healthcare, Financials, etc.)
- Economic outlook (Fed policy, inflation, growth)
- Risk analysis and portfolio positioning

### Document Statistics
```
Total Reports: 4
Total Pages: ~122
Total Chunks: 523
Chunk Size: 1000 characters
Chunk Overlap: 200 characters
Embedding Model: text-embedding-3-large
```

---

## RAG Pipeline Details

### Vector Store Configuration
- **Database**: ChromaDB (persistent local storage)
- **Embedding Model**: OpenAI text-embedding-3-large
- **Collection**: `investment_research`
- **Persist Directory**: `./data/chroma_db`

### Document Processing
1. **PDF Loading**: PyMuPDF (fitz) for text extraction
2. **Text Chunking**: Recursive character splitting
3. **Metadata Extraction**: Source, page, chunk ID, document type
4. **Embedding**: OpenAI API batch processing
5. **Storage**: ChromaDB with metadata indexing

### Retrieval Performance
| Query Category | Avg Distance | Results Quality |
|----------------|--------------|-----------------|
| Asset Classes  | 0.64-0.70    | Excellent       |
| Risk Analysis  | 0.90-0.93    | Good            |
| Sector Views   | 0.81-0.86    | Excellent       |
| Macro/Fed      | 0.79-0.82    | Excellent       |
| Portfolio      | 0.83-0.88    | Good            |
| Regional       | 0.78-0.81    | Excellent       |

---

## Testing

### Test RAG Retrieval
```bash
python src/rag/test_retrieval.py
```

**Tests Covered:**
1. ✅ Asset class outlook queries
2. ✅ Risk and uncertainty analysis
3. ✅ Sector recommendations
4. ✅ Fed policy and interest rates
5. ✅ Asset allocation strategies
6. ✅ Regional/emerging market views
7. ✅ Source-specific filtering (by date/report)
8. ✅ Citation extraction and formatting

### Sample Queries Tested
```python
# Asset class
"What is UBS's view on US equities?"

# Risk analysis
"What are the key risks to the market outlook?"

# Sector specific
"What is UBS's recommendation on technology stocks?"

# Macro economics
"What is the outlook for interest rates and Fed policy?"

# Portfolio strategy
"What asset allocation does UBS recommend?"

# Regional
"What is the view on emerging markets?"
```

---

## Environment Variables

Required in `.env`:
```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...

# Models
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# Paths
CHROMA_PERSIST_DIR=./data/chroma_db
DATA_DIR=./data
PDF_DIR=./data/pdfs

# LangChain (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_...
LANGCHAIN_PROJECT=investor-agent
```

---

## Troubleshooting

### Issue: No PDFs found
```bash
# Re-download reports
python src/data/download_ubs_reports.py
```

### Issue: ChromaDB collection empty
```bash
# Re-ingest documents
python src/data/ingest_reports.py
```

### Issue: Import errors
```bash
# Reinstall dependencies
uv pip install -e .
```

### Issue: OpenAI API errors
```bash
# Check API key is set
echo $OPENAI_API_KEY

# Or check .env file
cat .env | grep OPENAI_API_KEY
```

---

## Development Roadmap

### Day 1: RAG Pipeline ✅
- [x] Project setup and dependencies
- [x] UBS House View PDF download
- [x] PDF parsing and chunking
- [x] ChromaDB vector store setup
- [x] Embedding generation and storage
- [x] Retrieval testing and validation

### Day 2: Agent Development ✅
- [x] Build investment research agent with OpenAI function calling
- [x] Integrate RAG retrieval as agent tool
- [x] Add conversation memory (built into agent)
- [x] Implement compliance validation (automatic disclaimers)
- [x] Create full-featured Gradio web UI with citations
- [x] Build CLI interface for testing
- [x] Test multi-turn conversations
- [x] Create automated test suite (test_day2.sh)

### Day 3: Evaluation & API ✅
- [x] Create 15 test questions with ground truth (5 categories)
- [x] Build LLM-as-judge evaluator (GPT-4 based)
- [x] Build OpenAI Evals-style runner (deterministic)
- [x] Create comparison analysis tool
- [x] Build FastAPI REST API (7 endpoints)
- [x] Create CLI evaluation runner
- [x] Implement automated test suite (test_day3.sh)
- [x] Generate comprehensive documentation

---

## For Arklex Team

### What You'll Receive
1. **Agent Codebase**: Fully functional Python project
2. **Vector Store**: ChromaDB data directory (portable)
3. **Raw Data**: 4 UBS House View PDFs
4. **Test Baseline**: LLM-as-judge implementation and results
5. **Demo Materials**: Jupyter notebooks and video walkthrough
6. **Documentation**: Architecture overview and API specs

### Testing Surface
- ✅ Factual accuracy against UBS reports
- ✅ Multi-turn conversation consistency
- ✅ Source attribution and citations
- ✅ Hallucination detection
- ✅ Tool use correctness
- ✅ Compliance adherence

### Integration Points
- **FastAPI Endpoint**: `/api/v1/query` (Day 3)
- **Vector Store Access**: Direct ChromaDB connection
- **Conversation Logs**: JSON format with timestamps
- **Ground Truth**: 15 curated Q&A pairs

---

## Tech Stack

- **Language**: Python 3.11
- **Agent Framework**: AutoGen 0.7+
- **LLM**: OpenAI GPT-4 Turbo
- **Embeddings**: OpenAI text-embedding-3-large
- **Vector DB**: ChromaDB 1.3+
- **PDF Processing**: PyMuPDF, pdfplumber
- **Document Processing**: LangChain text splitters
- **Web UI**: Gradio 5.0+
- **API**: FastAPI + Uvicorn
- **Package Manager**: uv

---

## License

This project is for demonstration purposes for Arklex evaluation.

---

## Contact

For questions about this demo:
- **Project**: Arklex Investment Research Agent Demo
- **Timeline**: 3-day implementation
- **Status**: Day 1 Complete

---

**Last Updated**: Day 1 Complete - RAG Pipeline Operational

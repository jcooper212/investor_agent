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

### 🚧 Day 2 In Progress (Agent Development)
- AutoGen agent integration
- Tool calling (market data, SEC filings)
- Gradio web UI

### ⏳ Day 3 Planned (Testing & Polish)
- LLM-as-judge baseline
- FastAPI REST API
- Documentation for Arklex handoff

---

## Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key
- [uv](https://github.com/astral-sh/uv) package manager

### 1. Clone and Setup

```bash
cd investor_agent

# Create virtual environment
uv venv

# Install dependencies
uv pip install -e .

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Download UBS Reports

```bash
source .venv/bin/activate
python src/data/download_ubs_reports.py
```

**Expected Output:**
```
✅ Successful: 4/4
Downloaded files:
  • UBS_House_View_June_2025.pdf (1707.4 KB)
  • UBS_House_View_March_2025.pdf (1724.9 KB)
  • UBS_House_View_November_2024.pdf (1616.2 KB)
  • UBS_House_View_June_2024.pdf (2386.1 KB)
```

### 3. Ingest Reports into Vector Store

```bash
python src/data/ingest_reports.py
```

**Expected Output:**
```
✅ Ingestion complete!
   Files processed: 4
   Total chunks: 523

📊 Documents in Collection: 523
```

### 4. Test RAG Retrieval

```bash
python src/rag/test_retrieval.py
```

**Expected Output:**
```
✅ All RAG retrieval tests complete!

📈 Test Summary:
  ✅ Vector store operational with 523 chunks
  ✅ Query retrieval working across multiple categories
  ✅ Source attribution available for all results
  ✅ Metadata filtering functional
  ✅ Citation extraction successful

🎯 RAG pipeline ready for agent integration!
```

---

## Project Structure

```
investor_agent/
├── src/
│   ├── agent/              # Agent logic (Day 2)
│   ├── data/               # Data download and ingestion
│   │   ├── download_ubs_reports.py
│   │   └── ingest_reports.py
│   ├── rag/                # RAG pipeline
│   │   ├── __init__.py
│   │   ├── vector_store.py
│   │   └── test_retrieval.py
│   ├── tools/              # Agent tools (Day 2)
│   └── ui/                 # Gradio interface (Day 2)
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

### Day 2: Agent Development 🚧
- [ ] Extend FinRobot Financial Analyst Agent
- [ ] Integrate RAG with AutoGen
- [ ] Add conversation memory
- [ ] Build tool functions (market data, SEC filings)
- [ ] Implement compliance validation
- [ ] Create Gradio web UI
- [ ] Test multi-turn conversations

### Day 3: Testing & Polish ⏳
- [ ] Build LLM-as-judge evaluator
- [ ] Create 15 test questions with ground truth
- [ ] Run baseline evaluation
- [ ] Build FastAPI REST API
- [ ] Documentation for Arklex handoff
- [ ] Package vector store for export
- [ ] Create demo Jupyter notebooks

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

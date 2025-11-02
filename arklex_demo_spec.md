# Arklex Demo Spec: Investment Research Q&A Agent

## Executive Summary

**Objective**: Create a financial services AI agent demo that showcases Arklex's testing superiority over traditional "LLM as judge" approaches for investment research use cases.

**Use Case**: Multi-turn Investment Research Q&A Agent that answers questions about market outlook, investment recommendations, and risk analysis using UBS House View reports and SEC filings.

**Timeline**: 2-3 days for demo-quality implementation

**Handoff**: Agent codebase + vector DB access for Arklex to ingest and build comprehensive test generation

---

## Why This Demo Wins

### Client Impact
- **Instant Relatability**: Every wealth manager/asset manager/research analyst uses these reports daily
- **High Stakes**: Incorrect investment advice = client losses, compliance issues, reputation damage
- **Real Pain Point**: Analysts spend hours reading lengthy reports; automation with accuracy is golden

### Testing Surface for Arklex
- **Factual Accuracy**: Did the agent extract correct data from reports?
- **Consistency**: Does it give same answer across multiple turns?
- **Source Attribution**: Can it cite specific sections?
- **Reasoning Quality**: Does it synthesize information correctly?
- **Hallucination Detection**: Does it make up data not in reports?
- **Context Retention**: Does it maintain conversation state across turns?

---

## Architecture

### Base Platform
**Direct Fork**: [FinRobot](https://github.com/AI4Finance-Foundation/FinRobot)
- Open-source financial AI agent platform (AI4Finance Foundation)
- Built on AutoGen (Microsoft's multi-agent framework)
- Existing Financial Analyst Agent + Market Forecaster capabilities
- Proven integration with financial data sources (SEC, Yahoo Finance, Finnhub)
- Python-based with clear extension patterns
- We'll extend with UBS House View RAG and custom tools

### Our Agent: "Research Advisor Agent"

```
┌─────────────────────────────────────────────┐
│         User Query (Multi-turn)             │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│     Research Advisor Agent (AutoGen)        │
│   - Query understanding                     │
│   - Context tracking (conversation state)   │
│   - Response synthesis                      │
└────────┬────────────────────────────────────┘
         │
         ├──────────────┬──────────────┬───────────────┐
         ▼              ▼              ▼               ▼
   ┌─────────┐    ┌─────────┐   ┌──────────┐   ┌──────────┐
   │   RAG   │    │  Tools  │   │ Memory   │   │ Validator│
   │ Engine  │    │ Layer   │   │ Manager  │   │  (Rules) │
   └────┬────┘    └────┬────┘   └────┬─────┘   └────┬─────┘
        │              │              │              │
        ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────┐
│              Data Sources                               │
│  - UBS House View Reports (Vector DB)                   │
│  - SEC 10-K/10-Q Filings (Vector DB)                    │
│  - Market Data APIs (Yahoo Finance, Finnhub)            │
│  - Compliance Rules (RAG)                               │
└─────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. RAG Engine
- **Vector DB**: ChromaDB (persistent, portable, easy to handover)
- **Embeddings**: OpenAI text-embedding-3-large
- **Documents**:
  - UBS House View Reports (2024-2025, monthly editions)
  - SEC 10-K filings for major companies mentioned in reports
  - Fed/ECB policy documents (supplementary)

#### 2. Tool Calling Layer
- **get_stock_price**: Current market data via Yahoo Finance API
- **get_company_filing**: Retrieve specific SEC filing sections
- **calculate_metrics**: Basic financial ratio calculations
- **get_economic_indicators**: Fed data, inflation, rates

#### 3. Conversation Memory
- Track user questions across turns
- Maintain context of what was already discussed
- Reference previous answers in follow-ups

#### 4. Compliance Validator (Rules Engine)
- Check responses don't include: forward-looking guarantees, unlicensed advice
- Require disclaimers for investment recommendations
- Flag when agent lacks sufficient data

---

## Data Sources

### Primary: UBS House View Reports
**What**: Monthly investment strategy guides from UBS Chief Investment Office
**Content**:
- Global economic outlook
- Asset allocation recommendations
- Sector analysis (Tech, Healthcare, Financials, etc.)
- Regional perspectives (US, Europe, Asia, EM)
- Risk analysis

**Available**:
- Monthly reports 2024-2025 (PDF format)
- Publicly accessible via advisors.ubs.com and ubs.com
- ~50-100 pages per report, rich structured data

**Why Perfect**:
- High-quality professional research
- Clear factual statements (testable)
- Structured format (easier to verify)
- Real-world client use case

### Secondary: SEC EDGAR Filings
- 10-K annual reports for companies mentioned in UBS reports
- Use FinRobot's existing SEC integration
- Validates cross-referencing capability

### Tertiary: Market Data APIs
- Yahoo Finance (free, no auth)
- Finnhub (free tier available)
- Fed Economic Data (FRED API)

---

## Demo User Flows

### Flow 1: Single Asset Class Deep Dive
```
User: "What's UBS's view on US equities?"
Agent: [RAG lookup → UBS House View] "According to the March 2025 House View..."

User: "Why are they bullish?"
Agent: [Context + RAG] "The report cites three factors: 1) Fed policy..."

User: "What's the risk to this view?"
Agent: [RAG on risk section] "Key downside risks include..."

User: "Show me the tech sector specifics"
Agent: [RAG + structured extraction] "UBS recommends overweight on..."
```

### Flow 2: Cross-Document Synthesis
```
User: "What does UBS say about NVIDIA's outlook?"
Agent: [RAG UBS + Tool call to get NVDA data] "UBS is positive on semiconductors..."

User: "Does NVIDIA's 10-K support this thesis?"
Agent: [Tool: get_company_filing for NVDA] "Their revenue guidance shows..."

User: "What's the current stock price vs their target?"
Agent: [Tool: get_stock_price] "NVDA is trading at $XXX, UBS target is..."
```

### Flow 3: Portfolio Recommendation
```
User: "I'm 45, moderate risk tolerance, what should I invest in?"
Agent: [Compliance check → Add disclaimer + RAG] "I'm not a licensed advisor, but based on UBS House View..."

User: "What allocation do they suggest?"
Agent: [RAG + calculation tool] "60/40 equity/bonds with..."

User: "How would this perform in a recession?"
Agent: [RAG historical + synthesis] "Looking at UBS risk scenarios..."
```

---

## Testing Strategy

### What Arklex Will Test
- **Factual Accuracy**: Ground truth from UBS PDFs
- **Consistency**: Same question → same answer across sessions
- **Source Attribution**: Citations match document sections
- **Hallucination Detection**: Spot invented facts/numbers
- **Multi-turn Coherence**: Context maintained properly
- **Tool Use Correctness**: APIs called with right params
- **Compliance Adherence**: Disclaimers present, no violations

### LLM-as-Judge Baseline (We Build)

**Simple Implementation**:
```python
# Judge Agent evaluates Research Agent responses
judge_prompt = """
You are evaluating a financial research agent's response.

USER QUESTION: {question}
AGENT RESPONSE: {response}
SOURCE DOCUMENTS: {ground_truth}

Evaluate on 5 criteria (score 1-5):
1. Factual Accuracy: Does response match source documents?
2. Completeness: Did it answer the full question?
3. Source Attribution: Proper citations?
4. Clarity: Is it understandable?
5. Compliance: Appropriate disclaimers?

Output JSON with scores and reasoning.
"""
```

**Limitations to Demonstrate**:
- Judge LLM can hallucinate too
- Can't test multi-turn state reliably
- No adversarial scenario generation
- Manual ground truth creation required
- Inconsistent evaluation across runs
- No automated edge case discovery

### Arklex's Advantage
- Automated test case generation (we don't provide any)
- Multi-turn conversation testing
- Adversarial probing
- Consistency across runs
- Objective metrics not LLM-based
- Edge case discovery

---

## Tech Stack (Locked In)

### Core
- **Language**: Python 3.11+
- **Agent Framework**: AutoGen (from FinRobot fork)
- **LLM**: OpenAI GPT-4 Turbo
- **Vector DB**: ChromaDB (persistent local storage, portable for handover)
- **Embeddings**: OpenAI text-embedding-3-large

### Data Processing
- **PDF Parsing**: PyMuPDF (fitz) or pdfplumber
- **Document Chunking**: LangChain text splitters
- **SEC Data**: FinRobot's existing integration

### APIs
- **Market Data**: yfinance (Yahoo Finance)
- **Company Data**: Finnhub free tier
- **Economic Data**: fredapi (Federal Reserve)

### Interface (Priority Order)
- **Primary**: Gradio web UI (for live testing and demos)
- **Secondary**: FastAPI REST API (for Arklex integration)
- **Tertiary**: Command-line chat interface (for debugging)

### Testing & Eval
- **LLM Judge**: OpenAI GPT-4 (separate instance)
- **Test Questions**: 15 curated Q&A pairs with ground truth
- **Metrics**: Custom Python scripts for evaluation
- **Ground Truth Storage**: JSON files with question-answer-source mappings

---

## Implementation Plan (2-3 Days)

### Day 1: Setup & Data Ingestion
**Morning**:
- Fork FinRobot repo
- Set up environment (uv for deps)
- Configure OpenAI API keys
- Set up ChromaDB

**Afternoon**:
- Download UBS House View PDFs (2024-2025)
- Parse PDFs and chunk into documents
- Create embeddings and load into vector DB
- Verify RAG retrieval working

**Evening**:
- Test basic Q&A with RAG
- Validate source attribution

### Day 2: Agent Development
**Morning**:
- Extend FinRobot's Financial Analyst Agent
- Implement conversation memory (AutoGen built-in)
- Add tool functions (stock price, filings, metrics)

**Afternoon**:
- Build compliance validation rules
- Integrate tool calling with RAG
- Test multi-turn conversations

**Evening**:
- Build Gradio web UI (chat interface)
- Wire up agent to Gradio
- Manual testing of user flows in browser

### Day 3: Testing Infrastructure & Polish
**Morning**:
- Build LLM-as-judge evaluator
- Create 15 test questions with ground truth from UBS reports
- Run baseline LLM judge evaluation

**Afternoon**:
- Build FastAPI REST API endpoint (for Arklex)
- Document agent architecture for Arklex
- Package vector DB for handover
- Create demo scripts (Jupyter notebooks)

**Evening**:
- Polish error handling and UI/UX
- Add logging/observability
- Final testing of all three user flows
- Documentation and README

---

## Deliverables for Arklex Handover

### 1. Agent Codebase
- Fully functional Python repo
- Docker compose setup (agent + vector DB)
- API documentation (OpenAPI spec)
- README with architecture overview

### 2. Data Assets
- ChromaDB vector store (exportable)
- Raw UBS PDF files
- Embedding model details
- Sample ground truth Q&A pairs (for reference)

### 3. LLM Judge Baseline
- Judge implementation code
- Baseline test results
- Evaluation metrics
- Known limitations documented

### 4. Demo Materials
- Jupyter notebook with example conversations
- Video recording of agent in action
- Slide deck explaining the use case
- Test conversation transcripts

---

## Success Metrics

### For Client Demo
- **Wow Factor**: Client recognizes their workflow immediately
- **Accuracy**: Agent answers ≥90% of fact-based questions correctly
- **Relevance**: Responses directly cite UBS reports
- **Polish**: No crashes, clean error handling, fast responses

### For Arklex Comparison
- **LLM Judge Baseline**: Established quantitative scores
- **Test Surface**: Clear documentation of what can break
- **Differentiation**: Obvious gaps in LLM judge approach
- **Scalability**: Show how Arklex auto-generation beats manual tests

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| UBS PDFs not machine-readable | High | Pre-test PDF parsing; use OCR if needed |
| FinRobot too complex to extend | Medium | Keep fork minimal; build parallel if needed |
| RAG retrieval inaccurate | High | Tune chunking strategy; use reranking |
| API rate limits (free tiers) | Low | Cache responses; use mock data if needed |
| Multi-turn state bugs | Medium | Thorough testing of conversation flows |
| Compliance rules too complex | Low | Keep simple (disclaimers + basic checks) |

---

## Next Steps - Ready to Execute

**Spec Status**: ✅ Locked and approved by JC

### Confirmed Decisions
- ✅ OpenAI GPT-4 Turbo for agent + judge
- ✅ ChromaDB for vector storage
- ✅ Direct fork of FinRobot repo
- ✅ 15 test questions for LLM judge baseline
- ✅ Gradio web UI as primary interface

### Implementation Sequence
1. **Day 1 AM**: Fork FinRobot, setup environment with uv, configure OpenAI
2. **Day 1 PM**: Download UBS PDFs, parse, chunk, embed, load to ChromaDB
3. **Day 2 AM**: Extend FinRobot agent with tools and memory
4. **Day 2 PM**: Build compliance rules, integrate RAG + tools
5. **Day 2 Eve**: Build Gradio UI and test flows
6. **Day 3 AM**: Create LLM judge + 15 test questions
7. **Day 3 PM**: Build API, documentation, handover package

**Status**: Ready to kick off implementation on your signal, JC.

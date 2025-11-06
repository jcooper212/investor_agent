# ABOUTME: FastAPI REST API server for investment research agent
# ABOUTME: Provides endpoints for queries, evaluations, and system management

import sys
from pathlib import Path
import uuid
import json
import time
from datetime import datetime
from typing import Dict

sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.models import (
    QueryRequest,
    QueryResponse,
    ConversationRequest,
    ConversationResponse,
    EvaluationRequest,
    EvaluationResponse,
    ComparisonRequest,
    ComparisonResponse,
    HealthResponse,
    StatsResponse,
)
from src.agent.research_agent import ResearchAgent
from src.rag.vector_store import VectorStore
from src.eval.test_runner import TestRunner
from src.eval.openai_evals_runner import OpenAIEvalsRunner

# Initialize FastAPI app
app = FastAPI(
    title="Investment Research Agent API",
    description="REST API for querying investment research and running evaluations",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (in production, use proper state management)
agent_instance: ResearchAgent = None
conversations: Dict[str, ResearchAgent] = {}


def get_agent() -> ResearchAgent:
    """Get or create global agent instance."""
    global agent_instance
    if agent_instance is None:
        agent_instance = ResearchAgent()
    return agent_instance


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Investment Research Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


@app.get("/api/v1/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint.

    Returns service status and timestamp.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
    )


@app.get("/api/v1/stats", response_model=StatsResponse, tags=["System"])
async def get_stats():
    """
    Get system statistics.

    Returns vector store info and available evaluators.
    """
    try:
        vs = VectorStore()
        stats = vs.get_collection_stats()

        return StatsResponse(
            vector_store_documents=stats["count"],
            vector_store_path=stats["persist_directory"],
            available_evaluators=["llm-judge", "openai-evals"],
            api_version="1.0.0",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@app.post("/api/v1/query", response_model=QueryResponse, tags=["Agent"])
async def query_agent(request: QueryRequest):
    """
    Send a single query to the research agent.

    Args:
        request: Query request with question and parameters

    Returns:
        Agent response with sources and tool calls
    """
    try:
        agent = get_agent()

        # Clear history for fresh context
        agent.clear_history(keep_system_prompt=True)

        # Track time
        start_time = time.time()

        # Get response
        response = agent.chat(request.query)

        elapsed = time.time() - start_time

        # Extract sources from agent history (simplified)
        sources = []
        tool_calls = []

        # Parse agent messages for tool calls
        for msg in agent.get_history():
            if msg["role"] == "tool":
                sources.append({
                    "tool": msg.get("name", "unknown"),
                    "content_preview": msg.get("content", "")[:200],
                })

        return QueryResponse(
            response=response,
            sources=sources,
            tool_calls=tool_calls,
            response_time_seconds=elapsed,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/api/v1/conversation", response_model=ConversationResponse, tags=["Agent"])
async def conversation(request: ConversationRequest):
    """
    Multi-turn conversation endpoint with session management.

    Args:
        request: Conversation request with message and optional conversation ID

    Returns:
        Agent response with conversation tracking
    """
    try:
        # Get or create conversation
        if request.conversation_id and request.conversation_id in conversations:
            agent = conversations[request.conversation_id]
        else:
            agent = ResearchAgent()
            conv_id = request.conversation_id or str(uuid.uuid4())
            conversations[conv_id] = agent

        conv_id = request.conversation_id or list(conversations.keys())[-1]

        # Reset if requested
        if request.reset:
            agent.clear_history(keep_system_prompt=True)

        # Get response
        response = agent.chat(request.message)

        # Extract sources
        sources = []
        for msg in agent.get_history():
            if msg["role"] == "tool":
                sources.append({
                    "content_preview": msg.get("content", "")[:200],
                })

        return ConversationResponse(
            response=response,
            conversation_id=conv_id,
            message_count=len(agent.get_history()),
            sources=sources,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversation failed: {str(e)}")


@app.post("/api/v1/evaluate/llm-judge", response_model=EvaluationResponse, tags=["Evaluation"])
async def evaluate_llm_judge(request: EvaluationRequest):
    """
    Run LLM-as-judge evaluation on test set.

    Args:
        request: Evaluation request with test set path

    Returns:
        Evaluation results and summary
    """
    try:
        start_time = time.time()

        # Run evaluation
        runner = TestRunner(request.test_set_path)
        output_path = "data/eval_results/llm_judge_results.json" if request.save_results else None

        results = runner.run_full_evaluation(
            output_path=output_path,
            verbose=False,
        )

        elapsed = time.time() - start_time

        return EvaluationResponse(
            evaluator="llm-judge",
            total_questions=results["total_questions"],
            overall_average=results["summary"]["overall_average"],
            pass_rate=results["summary"]["pass_rate"],
            category_breakdown=results["summary"]["category_breakdown"],
            execution_time_seconds=elapsed,
            results_path=output_path,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@app.post("/api/v1/evaluate/openai-evals", response_model=EvaluationResponse, tags=["Evaluation"])
async def evaluate_openai_evals(request: EvaluationRequest):
    """
    Run OpenAI Evals-style evaluation on test set.

    Args:
        request: Evaluation request with test set path

    Returns:
        Evaluation results and summary
    """
    try:
        start_time = time.time()

        # Run evaluation
        runner = OpenAIEvalsRunner(request.test_set_path)
        results = runner.run_evaluation(verbose=False)

        output_path = None
        if request.save_results:
            output_path = "data/eval_results/openai_evals_results.json"
            runner.save_results(results, output_path)

        elapsed = time.time() - start_time

        return EvaluationResponse(
            evaluator="openai-evals",
            total_questions=results["total_questions"],
            overall_average=results["summary"]["overall_average"],
            pass_rate=results["summary"]["pass_rate"],
            category_breakdown=results["summary"]["category_breakdown"],
            execution_time_seconds=elapsed,
            results_path=output_path,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@app.get("/api/v1/evaluate/compare", response_model=ComparisonResponse, tags=["Evaluation"])
async def compare_evaluators(
    llm_judge_path: str = "data/eval_results/llm_judge_results.json",
    evals_path: str = "data/eval_results/openai_evals_results.json",
):
    """
    Compare LLM-as-judge and OpenAI Evals results.

    Args:
        llm_judge_path: Path to LLM judge results
        evals_path: Path to OpenAI Evals results

    Returns:
        Comparison analysis with recommendations
    """
    try:
        # Load both results
        with open(llm_judge_path, "r") as f:
            llm_results = json.load(f)

        with open(evals_path, "r") as f:
            evals_results = json.load(f)

        # Extract summaries
        llm_summary = llm_results.get("summary", {})
        evals_summary = evals_results.get("summary", {})

        # Simple comparison
        comparison = {
            "overall_score": {
                "llm_judge": llm_summary.get("overall_average", 0),
                "openai_evals": evals_summary.get("overall_average", 0),
            },
            "pass_rate": {
                "llm_judge": llm_summary.get("pass_rate", 0),
                "openai_evals": evals_summary.get("pass_rate", 0),
            },
        }

        # Generate recommendation
        llm_score = llm_summary.get("overall_average", 0)
        evals_score = evals_summary.get("overall_average", 0)

        if abs(llm_score - evals_score) < 0.2:
            recommendation = "Both evaluators show similar results. LLM-as-judge provides more detailed reasoning, while OpenAI Evals is more deterministic."
        elif llm_score > evals_score:
            recommendation = "LLM-as-judge scored higher, suggesting more nuanced evaluation. However, it may be less consistent across runs."
        else:
            recommendation = "OpenAI Evals scored higher with more deterministic grading. Better for regression testing."

        return ComparisonResponse(
            llm_judge_summary=llm_summary,
            openai_evals_summary=evals_summary,
            comparison_metrics=comparison,
            recommendation=recommendation,
        )

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Results file not found. Run evaluations first. {str(e)}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    print("=" * 80)
    print("Investment Research Agent API")
    print("=" * 80)
    print("\nStarting server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/api/v1/health")
    print("\n" + "=" * 80)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

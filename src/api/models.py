# ABOUTME: Pydantic models for FastAPI request/response validation
# ABOUTME: Defines data structures for all API endpoints

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# Query endpoints
class QueryRequest(BaseModel):
    """Request model for single query endpoint."""

    query: str = Field(..., description="User's investment research question")
    n_results: int = Field(5, description="Number of RAG results to retrieve")


class QueryResponse(BaseModel):
    """Response model for single query endpoint."""

    response: str = Field(..., description="Agent's response")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source citations")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="Tool calls made")
    response_time_seconds: float = Field(..., description="Response generation time")


# Conversation endpoints
class ConversationRequest(BaseModel):
    """Request model for multi-turn conversation endpoint."""

    message: str = Field(..., description="User's message")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")
    reset: bool = Field(False, description="Reset conversation history")


class ConversationResponse(BaseModel):
    """Response model for conversation endpoint."""

    response: str = Field(..., description="Agent's response")
    conversation_id: str = Field(..., description="Unique conversation ID")
    message_count: int = Field(..., description="Number of messages in conversation")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source citations")


# Evaluation endpoints
class EvaluationRequest(BaseModel):
    """Request model for running evaluations."""

    test_set_path: str = Field("data/test_questions.json", description="Path to test questions")
    evaluator: str = Field("llm-judge", description="Evaluator type: llm-judge or openai-evals")
    save_results: bool = Field(True, description="Save results to file")


class EvaluationResponse(BaseModel):
    """Response model for evaluation results."""

    evaluator: str = Field(..., description="Evaluator used")
    total_questions: int = Field(..., description="Number of questions evaluated")
    overall_average: float = Field(..., description="Overall average score")
    pass_rate: float = Field(..., description="Percentage of passed tests")
    category_breakdown: Dict[str, Any] = Field(..., description="Results by category")
    execution_time_seconds: float = Field(..., description="Total evaluation time")
    results_path: Optional[str] = Field(None, description="Path to saved results")


class ComparisonRequest(BaseModel):
    """Request model for comparing evaluators."""

    llm_judge_results_path: str = Field(
        "data/eval_results/llm_judge_results.json",
        description="Path to LLM judge results",
    )
    evals_results_path: str = Field(
        "data/eval_results/openai_evals_results.json",
        description="Path to OpenAI Evals results",
    )


class ComparisonResponse(BaseModel):
    """Response model for evaluator comparison."""

    llm_judge_summary: Dict[str, Any] = Field(..., description="LLM judge summary")
    openai_evals_summary: Dict[str, Any] = Field(..., description="OpenAI Evals summary")
    comparison_metrics: Dict[str, Any] = Field(..., description="Side-by-side comparison")
    recommendation: str = Field(..., description="Recommendation on which evaluator to use")


# Health and stats endpoints
class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field("healthy", description="Service health status")
    timestamp: str = Field(..., description="Current server timestamp")
    version: str = Field("1.0.0", description="API version")


class StatsResponse(BaseModel):
    """Response model for system statistics."""

    vector_store_documents: int = Field(..., description="Number of documents in vector store")
    vector_store_path: str = Field(..., description="Path to vector store")
    available_evaluators: List[str] = Field(..., description="List of available evaluators")
    api_version: str = Field("1.0.0", description="API version")

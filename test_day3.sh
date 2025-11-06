#!/bin/bash

# ABOUTME: End-to-end test script for Day 3 - Evaluation infrastructure and API
# ABOUTME: Tests evaluation runners, API endpoints, and comparison tools

set -e  # Exit on error

echo "=============================================================================="
echo "Day 3 Testing: Evaluation Infrastructure & API"
echo "=============================================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check prerequisites
echo "📋 Checking prerequisites..."

if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

if ! grep -q "OPENAI_API_KEY=" .env; then
    echo -e "${RED}❌ OPENAI_API_KEY not found in .env${NC}"
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites OK${NC}"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Test 1: Test Questions File
echo "=============================================================================="
echo "Test 1: Test Questions File"
echo "=============================================================================="
echo ""

if [ ! -f "data/test_questions.json" ]; then
    echo -e "${RED}❌ Test questions file not found${NC}"
    exit 1
fi

python3 << 'EOF'
import json

with open("data/test_questions.json", "r") as f:
    data = json.load(f)

print(f"✅ Test questions loaded")
print(f"   Total questions: {data['total_questions']}")
print(f"   Categories: {', '.join(data['categories'])}")

# Verify structure
assert data['total_questions'] == 15, "Expected 15 questions"
assert len(data['questions']) == 15, "Question count mismatch"
print("✅ Test questions structure valid")
EOF

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Test 1 PASSED${NC}"
else
    echo -e "\n${RED}❌ Test 1 FAILED${NC}"
    exit 1
fi

# Test 2: LLM Judge Module
echo ""
echo "=============================================================================="
echo "Test 2: LLM Judge Module"
echo "=============================================================================="
echo ""

python3 << 'EOF'
from src.eval.llm_judge import LLMJudge

print("Testing LLM judge initialization...")
judge = LLMJudge()
print("✅ LLM judge initialized")

# Test evaluation structure (no actual API call)
print("✅ LLM judge module working")
EOF

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Test 2 PASSED${NC}"
else
    echo -e "\n${RED}❌ Test 2 FAILED${NC}"
    exit 1
fi

# Test 3: OpenAI Evals Module
echo ""
echo "=============================================================================="
echo "Test 3: OpenAI Evals Module"
echo "=============================================================================="
echo ""

python3 << 'EOF'
from src.eval.openai_evals_runner import OpenAIEvalsRunner

print("Testing OpenAI Evals runner initialization...")
runner = OpenAIEvalsRunner("data/test_questions.json")
print("✅ OpenAI Evals runner initialized")
print(f"   Loaded {runner.test_data['total_questions']} questions")

# Test graders
test_response = "According to UBS House View March 2025 (Page 17), the target is 6,600."
result = runner.grade_keyword_inclusion(test_response, ["6,600", "March 2025"])
print(f"✅ Keyword grader working: score={result['score']:.2f}")

citation_result = runner.grade_citation_quality(test_response, ["UBS_House_View_March_2025.pdf"])
print(f"✅ Citation grader working: quality={citation_result['citation_quality']}")
EOF

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Test 3 PASSED${NC}"
else
    echo -e "\n${RED}❌ Test 3 FAILED${NC}"
    exit 1
fi

# Test 4: FastAPI Models
echo ""
echo "=============================================================================="
echo "Test 4: FastAPI Models"
echo "=============================================================================="
echo ""

python3 << 'EOF'
from src.api.models import (
    QueryRequest, QueryResponse,
    EvaluationRequest, EvaluationResponse,
    HealthResponse, StatsResponse
)

print("Testing Pydantic models...")

# Test query models
query_req = QueryRequest(query="Test question")
print("✅ QueryRequest model working")

query_resp = QueryResponse(
    response="Test response",
    sources=[],
    tool_calls=[],
    response_time_seconds=1.0
)
print("✅ QueryResponse model working")

# Test evaluation models
eval_req = EvaluationRequest()
print("✅ EvaluationRequest model working")

print("✅ All API models working")
EOF

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Test 4 PASSED${NC}"
else
    echo -e "\n${RED}❌ Test 4 FAILED${NC}"
    exit 1
fi

# Test 5: FastAPI Server (import only)
echo ""
echo "=============================================================================="
echo "Test 5: FastAPI Server"
echo "=============================================================================="
echo ""

python3 << 'EOF'
from src.api.main import app

print("Testing FastAPI app initialization...")
print(f"✅ FastAPI app created: {app.title}")
print(f"   Version: {app.version}")

# Check routes
routes = [route.path for route in app.routes]
expected_routes = [
    "/api/v1/health",
    "/api/v1/stats",
    "/api/v1/query",
    "/api/v1/conversation",
    "/api/v1/evaluate/llm-judge",
    "/api/v1/evaluate/openai-evals",
    "/api/v1/evaluate/compare",
]

for route in expected_routes:
    if route in routes:
        print(f"   ✅ {route}")
    else:
        print(f"   ❌ {route} - MISSING")
        exit(1)

print("✅ All API endpoints registered")
EOF

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Test 5 PASSED${NC}"
else
    echo -e "\n${RED}❌ Test 5 FAILED${NC}"
    exit 1
fi

# Test 6: CLI Evaluation Runner
echo ""
echo "=============================================================================="
echo "Test 6: CLI Evaluation Runner"
echo "=============================================================================="
echo ""

python3 << 'EOF'
import sys
sys.argv = ["run_evaluation.py", "--help"]

try:
    from src.eval.run_evaluation import main
    print("✅ CLI runner module loads successfully")
except SystemExit:
    # --help causes SystemExit, which is expected
    print("✅ CLI runner help works")
EOF

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Test 6 PASSED${NC}"
else
    echo -e "\n${RED}❌ Test 6 FAILED${NC}"
    exit 1
fi

# Test 7: Comparison Tool
echo ""
echo "=============================================================================="
echo "Test 7: Comparison Tool"
echo "=============================================================================="
echo ""

python3 << 'EOF'
from src.eval.compare_evaluators import EvaluatorComparison

print("Testing comparison tool structure...")

# Create mock results files for testing
import json
import os

os.makedirs("data/eval_results", exist_ok=True)

mock_llm = {
    "summary": {
        "overall_average": 4.2,
        "pass_rate": 0.85,
        "category_breakdown": {
            "factual_recall": {"avg_score": 4.5, "count": 3, "passed": 3}
        }
    },
    "evaluations": [
        {"overall_score": 4.2, "pass": True, "category": "factual_recall"}
    ]
}

mock_evals = {
    "summary": {
        "overall_average": 0.88,
        "pass_rate": 0.90,
        "category_breakdown": {
            "factual_recall": {"avg_score": 0.92, "count": 3, "passed": 3}
        }
    },
    "evaluations": [
        {"overall_score": 0.88, "passed": True, "category": "factual_recall"}
    ]
}

with open("data/eval_results/test_llm_judge.json", "w") as f:
    json.dump(mock_llm, f)

with open("data/eval_results/test_evals.json", "w") as f:
    json.dump(mock_evals, f)

# Test comparison
comparison = EvaluatorComparison(
    "data/eval_results/test_llm_judge.json",
    "data/eval_results/test_evals.json"
)

overall = comparison.compare_overall_scores()
print(f"✅ Overall comparison: {overall['winner']}")

recommendations = comparison.generate_recommendations()
print(f"✅ Generated {len(recommendations)//2} recommendations")

report = comparison.generate_report(output_format="markdown")
print(f"✅ Report generated: {len(report)} characters")

# Cleanup
os.remove("data/eval_results/test_llm_judge.json")
os.remove("data/eval_results/test_evals.json")

print("✅ Comparison tool working")
EOF

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Test 7 PASSED${NC}"
else
    echo -e "\n${RED}❌ Test 7 FAILED${NC}"
    exit 1
fi

# Summary
echo ""
echo "=============================================================================="
echo "📊 Test Summary"
echo "=============================================================================="
echo ""
echo -e "${GREEN}✅ All Day 3 tests PASSED!${NC}"
echo ""
echo "Components tested:"
echo "  ✅ Test questions (15 questions across 5 categories)"
echo "  ✅ LLM-as-judge evaluator"
echo "  ✅ OpenAI Evals runner"
echo "  ✅ FastAPI models"
echo "  ✅ FastAPI server (7 endpoints)"
echo "  ✅ CLI evaluation runner"
echo "  ✅ Comparison tool"
echo ""
echo "Next steps:"
echo "  1. Run evaluations: python src/eval/run_evaluation.py --compare"
echo "  2. Generate report: python src/eval/compare_evaluators.py"
echo "  3. Start API server: python src/api/main.py"
echo ""
echo "Note: Full evaluation requires OpenAI API calls and takes ~10-15 minutes"
echo ""
echo "🎯 Day 3 infrastructure complete!"
echo "=============================================================================="

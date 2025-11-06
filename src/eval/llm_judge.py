# ABOUTME: LLM-as-judge evaluation implementation
# ABOUTME: Uses GPT-4 to evaluate agent responses against ground truth

import os
import json
from typing import Dict, Any, List
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LLMJudge:
    """
    LLM-as-judge evaluator using GPT-4 to score agent responses.

    This is a simple baseline evaluator that demonstrates the traditional
    approach of using an LLM to evaluate another LLM's outputs.
    """

    def __init__(self, model: str = "gpt-4-turbo-preview"):
        """
        Initialize the LLM judge.

        Args:
            model: OpenAI model to use for judging (default: gpt-4-turbo-preview)
        """
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.evaluation_criteria = [
            "factual_accuracy",
            "source_attribution",
            "completeness",
            "hallucination_detection",
            "compliance",
        ]

    def create_judge_prompt(
        self,
        question: str,
        agent_response: str,
        ground_truth: str,
        source_docs: List[str],
        category: str,
    ) -> str:
        """
        Create the evaluation prompt for the judge.

        Args:
            question: Original question asked
            agent_response: Agent's response to evaluate
            ground_truth: Expected correct answer
            source_docs: List of source document names
            category: Question category (factual, synthesis, etc.)

        Returns:
            Formatted judge prompt
        """
        prompt = f"""You are evaluating a financial research agent's response to a question about investment research.

**QUESTION**: {question}

**AGENT'S RESPONSE**:
{agent_response}

**GROUND TRUTH** (Expected Answer):
{ground_truth}

**SOURCE DOCUMENTS AVAILABLE**:
{', '.join(source_docs) if source_docs else 'None specified'}

**QUESTION CATEGORY**: {category}

---

Please evaluate the agent's response on the following criteria using a 1-5 scale:

1. **Factual Accuracy** (1-5):
   - Does the response contain correct information matching the ground truth?
   - Are any facts incorrect or misleading?
   - Score: 5 = Perfect accuracy, 1 = Completely incorrect

2. **Source Attribution** (1-5):
   - Does the response properly cite sources (document names, page numbers)?
   - Are citations accurate and specific?
   - Score: 5 = Excellent citations, 1 = No citations or wrong citations

3. **Completeness** (1-5):
   - Does the response fully answer the question?
   - Is any important information missing?
   - Score: 5 = Completely answers question, 1 = Barely addresses question

4. **Hallucination Detection** (1-5):
   - Does the response contain any fabricated information not in source documents?
   - Are there any invented facts, numbers, or claims?
   - Score: 5 = No hallucinations, 1 = Major hallucinations

5. **Compliance** (1-5):
   - For investment advice: Does it include appropriate disclaimers?
   - For out-of-scope questions: Does it acknowledge limitations?
   - Score: 5 = Excellent compliance, 1 = Missing critical disclaimers

---

Return your evaluation as a JSON object with this exact structure:
{{
  "factual_accuracy": {{"score": <1-5>, "reasoning": "<explanation>"}},
  "source_attribution": {{"score": <1-5>, "reasoning": "<explanation>"}},
  "completeness": {{"score": <1-5>, "reasoning": "<explanation>"}},
  "hallucination_detection": {{"score": <1-5>, "reasoning": "<explanation>"}},
  "compliance": {{"score": <1-5>, "reasoning": "<explanation>"}},
  "overall_score": <average of all scores>,
  "pass": <true if overall_score >= 3.5, false otherwise>,
  "summary": "<2-3 sentence summary of evaluation>"
}}

IMPORTANT: Return ONLY the JSON object, no other text."""

        return prompt

    def evaluate_response(
        self,
        question: str,
        agent_response: str,
        ground_truth: str,
        source_docs: List[str],
        category: str = "general",
    ) -> Dict[str, Any]:
        """
        Evaluate a single agent response.

        Args:
            question: Original question
            agent_response: Agent's response to evaluate
            ground_truth: Expected answer
            source_docs: List of source documents
            category: Question category

        Returns:
            Evaluation results dictionary
        """
        try:
            # Create judge prompt
            judge_prompt = self.create_judge_prompt(
                question, agent_response, ground_truth, source_docs, category
            )

            # Get evaluation from judge
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert evaluator of AI agent responses. Provide objective, detailed evaluations.",
                    },
                    {"role": "user", "content": judge_prompt},
                ],
                temperature=0.1,  # Low temperature for consistency
                response_format={"type": "json_object"},
            )

            # Parse evaluation
            evaluation = json.loads(response.choices[0].message.content)

            # Add metadata
            evaluation["question"] = question
            evaluation["category"] = category
            evaluation["timestamp"] = datetime.now().isoformat()
            evaluation["judge_model"] = self.model

            return evaluation

        except Exception as e:
            print(f"❌ Evaluation error: {e}")
            return {
                "error": str(e),
                "question": question,
                "overall_score": 0,
                "pass": False,
            }

    def evaluate_test_set(
        self,
        test_questions: List[Dict[str, Any]],
        agent_responses: List[str],
    ) -> Dict[str, Any]:
        """
        Evaluate multiple test cases.

        Args:
            test_questions: List of test question dictionaries
            agent_responses: List of agent responses (same order as questions)

        Returns:
            Comprehensive evaluation results
        """
        if len(test_questions) != len(agent_responses):
            raise ValueError("Number of questions must match number of responses")

        results = {
            "evaluator": "llm_judge",
            "judge_model": self.model,
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(test_questions),
            "evaluations": [],
            "summary": {},
        }

        # Evaluate each question
        for i, (test_q, response) in enumerate(zip(test_questions, agent_responses)):
            print(f"📊 Evaluating question {i+1}/{len(test_questions)}: {test_q['id']}")

            evaluation = self.evaluate_response(
                question=test_q["question"],
                agent_response=response,
                ground_truth=test_q["ground_truth"],
                source_docs=test_q.get("source_documents", []),
                category=test_q.get("category", "general"),
            )

            evaluation["question_id"] = test_q["id"]
            results["evaluations"].append(evaluation)

        # Calculate summary statistics
        results["summary"] = self._calculate_summary(results["evaluations"])

        return results

    def _calculate_summary(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate summary statistics from evaluations.

        Args:
            evaluations: List of evaluation dictionaries

        Returns:
            Summary statistics
        """
        if not evaluations:
            return {}

        # Filter out error cases
        valid_evals = [e for e in evaluations if "error" not in e]

        if not valid_evals:
            return {"error": "All evaluations failed"}

        # Calculate average scores
        criteria_scores = {}
        for criterion in self.evaluation_criteria:
            scores = [
                e[criterion]["score"]
                for e in valid_evals
                if criterion in e and "score" in e[criterion]
            ]
            if scores:
                criteria_scores[criterion] = {
                    "average": sum(scores) / len(scores),
                    "min": min(scores),
                    "max": max(scores),
                }

        # Overall statistics
        overall_scores = [e["overall_score"] for e in valid_evals if "overall_score" in e]
        pass_count = sum(1 for e in valid_evals if e.get("pass", False))

        # Category breakdown
        category_stats = {}
        for eval in valid_evals:
            cat = eval.get("category", "unknown")
            if cat not in category_stats:
                category_stats[cat] = {"count": 0, "passed": 0, "avg_score": []}

            category_stats[cat]["count"] += 1
            if eval.get("pass", False):
                category_stats[cat]["passed"] += 1
            if "overall_score" in eval:
                category_stats[cat]["avg_score"].append(eval["overall_score"])

        # Calculate category averages
        for cat in category_stats:
            scores = category_stats[cat]["avg_score"]
            if scores:
                category_stats[cat]["avg_score"] = sum(scores) / len(scores)
            else:
                category_stats[cat]["avg_score"] = 0

        return {
            "criteria_scores": criteria_scores,
            "overall_average": sum(overall_scores) / len(overall_scores) if overall_scores else 0,
            "pass_rate": pass_count / len(valid_evals) if valid_evals else 0,
            "total_evaluated": len(valid_evals),
            "total_failed": len(evaluations) - len(valid_evals),
            "category_breakdown": category_stats,
        }


def main():
    """Test the LLM judge with a sample evaluation."""
    print("🧪 Testing LLM Judge...")

    judge = LLMJudge()

    # Sample evaluation
    test_question = "What is UBS's year-end S&P 500 target for December 2025?"
    test_response = "According to UBS House View March 2025 (Page 17), the year-end target for the S&P 500 is 6,600 for December 2025."
    test_ground_truth = "6,600 according to UBS House View March 2025"

    print(f"\nQuestion: {test_question}")
    print(f"Response: {test_response}")
    print(f"\nEvaluating...")

    result = judge.evaluate_response(
        question=test_question,
        agent_response=test_response,
        ground_truth=test_ground_truth,
        source_docs=["UBS_House_View_March_2025.pdf"],
        category="factual_recall",
    )

    print(f"\n{'='*80}")
    print("Evaluation Results:")
    print(f"{'='*80}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

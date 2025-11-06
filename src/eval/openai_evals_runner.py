# ABOUTME: OpenAI Evals-style evaluation implementation for research agent
# ABOUTME: Uses deterministic matching and custom graders for more consistent evaluation

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import time
import re

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agent.research_agent import ResearchAgent
from tqdm import tqdm


class OpenAIEvalsRunner:
    """
    Evaluation runner inspired by OpenAI Evals framework.

    Uses deterministic graders where possible:
    - Exact match for specific facts
    - Keyword inclusion checks
    - Citation validation
    - Format checking

    Falls back to semantic similarity for complex cases.
    """

    def __init__(self, test_questions_path: str):
        """
        Initialize evals runner.

        Args:
            test_questions_path: Path to test questions JSON
        """
        self.test_questions_path = test_questions_path
        self.test_data = self._load_test_questions()
        self.agent = None

    def _load_test_questions(self) -> Dict[str, Any]:
        """Load test questions from JSON."""
        with open(self.test_questions_path, "r") as f:
            return json.load(f)

    def grade_exact_match(self, response: str, expected: List[str]) -> Dict[str, Any]:
        """
        Grade based on exact string matching.

        Args:
            response: Agent response
            expected: List of expected strings (any match = pass)

        Returns:
            Grading result
        """
        response_lower = response.lower()

        for exp in expected:
            if exp.lower() in response_lower:
                return {
                    "score": 1.0,
                    "passed": True,
                    "matched": exp,
                    "grader": "exact_match",
                }

        return {
            "score": 0.0,
            "passed": False,
            "expected_one_of": expected,
            "grader": "exact_match",
        }

    def grade_keyword_inclusion(
        self,
        response: str,
        required_keywords: List[str],
        partial_credit: bool = True,
    ) -> Dict[str, Any]:
        """
        Grade based on keyword inclusion.

        Args:
            response: Agent response
            required_keywords: List of keywords that must appear
            partial_credit: If True, give partial score for some keywords

        Returns:
            Grading result
        """
        response_lower = response.lower()
        found_keywords = []
        missing_keywords = []

        for keyword in required_keywords:
            # Handle multi-word keywords and alternatives (separated by |)
            alternatives = keyword.split("|")
            found = False
            for alt in alternatives:
                if alt.strip().lower() in response_lower:
                    found = True
                    found_keywords.append(alt.strip())
                    break

            if not found:
                missing_keywords.append(keyword)

        if partial_credit:
            score = len(found_keywords) / len(required_keywords) if required_keywords else 0.0
        else:
            score = 1.0 if len(missing_keywords) == 0 else 0.0

        return {
            "score": score,
            "passed": score >= 0.7,  # 70% threshold
            "found_keywords": found_keywords,
            "missing_keywords": missing_keywords,
            "grader": "keyword_inclusion",
        }

    def grade_citation_quality(self, response: str, expected_sources: List[str]) -> Dict[str, Any]:
        """
        Grade quality of source citations.

        Args:
            response: Agent response
            expected_sources: List of expected source document names

        Returns:
            Grading result
        """
        # Check for citation patterns
        citation_patterns = [
            r"according to",
            r"UBS House View",
            r"Page \d+",
            r"\(Page \d+\)",
            r"March 2025|June 2024|June 2025|November 2024",
        ]

        has_citations = any(re.search(pattern, response, re.IGNORECASE) for pattern in citation_patterns)

        # Check if expected sources are mentioned
        sources_mentioned = []
        for source in expected_sources:
            # Extract key parts (e.g., "March 2025" from "UBS_House_View_March_2025.pdf")
            key_parts = re.findall(r"(March|June|November|April)\s*\d{4}", source)
            for part in key_parts:
                if part.lower() in response.lower():
                    sources_mentioned.append(source)
                    break

        # Scoring
        if has_citations and sources_mentioned:
            score = 1.0
            quality = "excellent"
        elif has_citations:
            score = 0.7
            quality = "good"
        elif sources_mentioned:
            score = 0.5
            quality = "partial"
        else:
            score = 0.0
            quality = "none"

        return {
            "score": score,
            "passed": score >= 0.5,
            "has_citation_format": has_citations,
            "sources_mentioned": sources_mentioned,
            "citation_quality": quality,
            "grader": "citation_quality",
        }

    def grade_compliance(self, response: str, question_category: str) -> Dict[str, Any]:
        """
        Grade compliance (disclaimers, acknowledgment of limitations).

        Args:
            response: Agent response
            question_category: Type of question

        Returns:
            Grading result
        """
        # Check for compliance keywords
        compliance_keywords = [
            "investment advice",
            "financial advisor",
            "licensed advisor",
            "consult",
            "personalized advice",
            "not covered",
            "not found",
            "not available",
            "cannot",
            "unable to",
        ]

        response_lower = response.lower()
        compliance_found = [kw for kw in compliance_keywords if kw in response_lower]

        # Expectations by category
        if question_category in ["comparative", "edge_cases"]:
            # These should have disclaimers or limitations
            required = any(kw in response_lower for kw in compliance_keywords)
            score = 1.0 if required else 0.5
        else:
            # For factual questions, compliance is good but not always required
            score = 1.0 if compliance_found else 0.8

        return {
            "score": score,
            "passed": score >= 0.7,
            "compliance_indicators": compliance_found,
            "grader": "compliance",
        }

    def evaluate_response(
        self,
        question_id: str,
        question: str,
        response: str,
        ground_truth: str,
        evaluation_criteria: Dict[str, Any],
        source_docs: List[str],
        category: str,
    ) -> Dict[str, Any]:
        """
        Evaluate a single response using multiple graders.

        Args:
            question_id: Question ID
            question: Original question
            response: Agent's response
            ground_truth: Expected answer
            evaluation_criteria: Criteria from test question
            source_docs: Expected source documents
            category: Question category

        Returns:
            Evaluation result
        """
        results = {
            "question_id": question_id,
            "question": question,
            "category": category,
            "timestamp": datetime.now().isoformat(),
        }

        # 1. Keyword inclusion (factual accuracy proxy)
        must_include = evaluation_criteria.get("must_include", [])
        if must_include:
            keyword_result = self.grade_keyword_inclusion(response, must_include)
            results["keyword_check"] = keyword_result
        else:
            results["keyword_check"] = {"score": 1.0, "passed": True, "grader": "skipped"}

        # 2. Citation quality
        should_cite = evaluation_criteria.get("should_cite", True)
        if should_cite and source_docs:
            citation_result = self.grade_citation_quality(response, source_docs)
            results["citation_check"] = citation_result
        else:
            results["citation_check"] = {"score": 1.0, "passed": True, "grader": "skipped"}

        # 3. Compliance
        compliance_result = self.grade_compliance(response, category)
        results["compliance_check"] = compliance_result

        # Calculate overall score (weighted average)
        weights = {
            "keyword_check": 0.5,  # Most important: factual accuracy
            "citation_check": 0.3,  # Important: source attribution
            "compliance_check": 0.2,  # Important: disclaimers
        }

        overall_score = sum(
            results[check]["score"] * weights[check]
            for check in weights
            if check in results
        )

        results["overall_score"] = overall_score
        results["passed"] = overall_score >= 0.7  # 70% threshold

        return results

    def run_evaluation(self, verbose: bool = True) -> Dict[str, Any]:
        """
        Run evaluation on all test questions.

        Args:
            verbose: If True, show progress

        Returns:
            Complete evaluation results
        """
        if verbose:
            print(f"\n🧪 Running OpenAI Evals-style evaluation...")
            print(f"   Test questions: {self.test_data['total_questions']}")
            print("=" * 80)

        # Initialize agent
        if not self.agent:
            self.agent = ResearchAgent()

        results = {
            "evaluator": "openai_evals",
            "timestamp": datetime.now().isoformat(),
            "total_questions": self.test_data["total_questions"],
            "evaluations": [],
            "summary": {},
        }

        questions = self.test_data["questions"]
        iterator = tqdm(questions, desc="Evaluating") if verbose else questions

        for test_q in iterator:
            # Clear agent history
            self.agent.clear_history(keep_system_prompt=True)

            # Get agent response
            start_time = time.time()
            try:
                response = self.agent.chat(test_q["question"])
                elapsed = time.time() - start_time
            except Exception as e:
                response = f"ERROR: {e}"
                elapsed = 0

            # Evaluate
            eval_result = self.evaluate_response(
                question_id=test_q["id"],
                question=test_q["question"],
                response=response,
                ground_truth=test_q["ground_truth"],
                evaluation_criteria=test_q.get("evaluation_criteria", {}),
                source_docs=test_q.get("source_documents", []),
                category=test_q["category"],
            )

            eval_result["agent_response"] = response
            eval_result["response_time_seconds"] = elapsed

            results["evaluations"].append(eval_result)

        # Calculate summary
        results["summary"] = self._calculate_summary(results["evaluations"])

        if verbose:
            print("\n" + "=" * 80)
            print("📊 Evaluation Summary:")
            print(f"   Overall Average: {results['summary']['overall_average']:.2f}")
            print(f"   Pass Rate: {results['summary']['pass_rate']*100:.1f}%")
            print(f"   Keyword Accuracy: {results['summary']['avg_keyword_score']:.2f}")
            print(f"   Citation Quality: {results['summary']['avg_citation_score']:.2f}")
            print(f"   Compliance Score: {results['summary']['avg_compliance_score']:.2f}")

        return results

    def _calculate_summary(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics."""
        if not evaluations:
            return {}

        # Overall scores
        overall_scores = [e["overall_score"] for e in evaluations]
        pass_count = sum(1 for e in evaluations if e.get("passed", False))

        # Component scores
        keyword_scores = [
            e["keyword_check"]["score"]
            for e in evaluations
            if "keyword_check" in e and e["keyword_check"]["grader"] != "skipped"
        ]
        citation_scores = [
            e["citation_check"]["score"]
            for e in evaluations
            if "citation_check" in e and e["citation_check"]["grader"] != "skipped"
        ]
        compliance_scores = [e["compliance_check"]["score"] for e in evaluations if "compliance_check" in e]

        # Category breakdown
        category_stats = {}
        for eval in evaluations:
            cat = eval["category"]
            if cat not in category_stats:
                category_stats[cat] = {"count": 0, "passed": 0, "scores": []}

            category_stats[cat]["count"] += 1
            if eval.get("passed", False):
                category_stats[cat]["passed"] += 1
            category_stats[cat]["scores"].append(eval["overall_score"])

        for cat in category_stats:
            scores = category_stats[cat]["scores"]
            category_stats[cat]["avg_score"] = sum(scores) / len(scores) if scores else 0

        return {
            "overall_average": sum(overall_scores) / len(overall_scores) if overall_scores else 0,
            "pass_rate": pass_count / len(evaluations) if evaluations else 0,
            "avg_keyword_score": sum(keyword_scores) / len(keyword_scores) if keyword_scores else 0,
            "avg_citation_score": sum(citation_scores) / len(citation_scores) if citation_scores else 0,
            "avg_compliance_score": sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0,
            "total_evaluated": len(evaluations),
            "category_breakdown": category_stats,
        }

    def save_results(self, results: Dict[str, Any], output_path: str):
        """Save results to JSON."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Results saved to: {output_path}")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Run OpenAI Evals-style evaluation")
    parser.add_argument(
        "--test-set",
        default="data/test_questions.json",
        help="Path to test questions",
    )
    parser.add_argument(
        "--output",
        default="data/eval_results/openai_evals_results.json",
        help="Output path",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress output")

    args = parser.parse_args()

    runner = OpenAIEvalsRunner(args.test_set)
    results = runner.run_evaluation(verbose=not args.quiet)
    runner.save_results(results, args.output)

    print(f"\n✅ Evaluation complete: {args.output}")


if __name__ == "__main__":
    main()

# ABOUTME: Test runner for evaluating the research agent
# ABOUTME: Runs agent on test questions and coordinates evaluation with LLM judge

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import time

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agent.research_agent import ResearchAgent
from src.eval.llm_judge import LLMJudge
from tqdm import tqdm


class TestRunner:
    """
    Coordinates running the research agent on test questions
    and evaluating the responses.
    """

    def __init__(self, test_questions_path: str):
        """
        Initialize test runner.

        Args:
            test_questions_path: Path to test questions JSON file
        """
        self.test_questions_path = test_questions_path
        self.test_data = self._load_test_questions()
        self.agent = None
        self.agent_responses = []

    def _load_test_questions(self) -> Dict[str, Any]:
        """Load test questions from JSON file."""
        with open(self.test_questions_path, "r") as f:
            return json.load(f)

    def run_agent_on_tests(self, verbose: bool = True) -> List[Dict[str, Any]]:
        """
        Run the research agent on all test questions.

        Args:
            verbose: If True, print progress

        Returns:
            List of dictionaries with question, response, and metadata
        """
        if verbose:
            print(f"\n🤖 Running agent on {self.test_data['total_questions']} test questions...")
            print("=" * 80)

        # Initialize agent once
        if not self.agent:
            self.agent = ResearchAgent()

        responses = []

        questions = self.test_data["questions"]
        iterator = tqdm(questions, desc="Testing agent") if verbose else questions

        for test_q in iterator:
            if verbose and not isinstance(iterator, tqdm):
                print(f"\n📝 {test_q['id']}: {test_q['question']}")

            # Record start time
            start_time = time.time()

            try:
                # Clear agent history for fresh context each question
                self.agent.clear_history(keep_system_prompt=True)

                # Get response
                response = self.agent.chat(test_q["question"])

                # Record end time
                elapsed_time = time.time() - start_time

                response_data = {
                    "question_id": test_q["id"],
                    "question": test_q["question"],
                    "category": test_q["category"],
                    "agent_response": response,
                    "ground_truth": test_q["ground_truth"],
                    "source_documents": test_q.get("source_documents", []),
                    "source_pages": test_q.get("source_pages", []),
                    "response_time_seconds": elapsed_time,
                    "timestamp": datetime.now().isoformat(),
                }

                if verbose and not isinstance(iterator, tqdm):
                    print(f"✅ Response ({elapsed_time:.2f}s): {response[:150]}...")

            except Exception as e:
                if verbose:
                    print(f"❌ Error: {e}")

                response_data = {
                    "question_id": test_q["id"],
                    "question": test_q["question"],
                    "category": test_q["category"],
                    "agent_response": "",
                    "error": str(e),
                    "ground_truth": test_q["ground_truth"],
                    "source_documents": test_q.get("source_documents", []),
                    "timestamp": datetime.now().isoformat(),
                }

            responses.append(response_data)

        self.agent_responses = responses

        if verbose:
            print("\n" + "=" * 80)
            print(f"✅ Agent testing complete: {len(responses)} responses collected")

        return responses

    def evaluate_with_llm_judge(self, verbose: bool = True) -> Dict[str, Any]:
        """
        Evaluate agent responses using LLM-as-judge.

        Args:
            verbose: If True, print progress

        Returns:
            Evaluation results dictionary
        """
        if not self.agent_responses:
            raise ValueError("No agent responses to evaluate. Run run_agent_on_tests() first.")

        if verbose:
            print(f"\n⚖️  Evaluating with LLM-as-judge...")
            print("=" * 80)

        judge = LLMJudge()

        # Evaluate each response
        results = judge.evaluate_test_set(
            test_questions=self.test_data["questions"],
            agent_responses=[r["agent_response"] for r in self.agent_responses],
        )

        # Merge agent metadata with evaluation results
        for i, eval_result in enumerate(results["evaluations"]):
            eval_result["response_time"] = self.agent_responses[i].get("response_time_seconds")
            if "error" in self.agent_responses[i]:
                eval_result["agent_error"] = self.agent_responses[i]["error"]

        if verbose:
            print("\n" + "=" * 80)
            print("📊 Evaluation Summary:")
            print(f"   Overall Average: {results['summary']['overall_average']:.2f}/5.0")
            print(f"   Pass Rate: {results['summary']['pass_rate']*100:.1f}%")
            print(f"   Total Evaluated: {results['summary']['total_evaluated']}")
            print("\n   By Category:")
            for cat, stats in results["summary"]["category_breakdown"].items():
                print(f"     {cat}: {stats['avg_score']:.2f}/5.0 ({stats['passed']}/{stats['count']} passed)")

        return results

    def save_results(self, results: Dict[str, Any], output_path: str):
        """
        Save evaluation results to JSON file.

        Args:
            results: Results dictionary
            output_path: Path to save JSON file
        """
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Results saved to: {output_path}")

    def run_full_evaluation(
        self,
        output_path: str = "data/eval_results/llm_judge_results.json",
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        Run complete evaluation pipeline: agent testing + LLM judge evaluation.

        Args:
            output_path: Path to save results
            verbose: If True, print progress

        Returns:
            Complete evaluation results
        """
        # Run agent on tests
        self.run_agent_on_tests(verbose=verbose)

        # Evaluate with LLM judge
        results = self.evaluate_with_llm_judge(verbose=verbose)

        # Save results
        self.save_results(results, output_path)

        return results


def main():
    """CLI entry point for test runner."""
    import argparse

    parser = argparse.ArgumentParser(description="Run research agent evaluation tests")
    parser.add_argument(
        "--test-set",
        default="data/test_questions.json",
        help="Path to test questions JSON file",
    )
    parser.add_argument(
        "--output",
        default="data/eval_results/llm_judge_results.json",
        help="Path to save evaluation results",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Investment Research Agent - Evaluation Test Runner")
    print("=" * 80)

    # Run evaluation
    runner = TestRunner(args.test_set)
    results = runner.run_full_evaluation(
        output_path=args.output,
        verbose=not args.quiet,
    )

    print("\n" + "=" * 80)
    print("✅ Evaluation complete!")
    print(f"   Results saved to: {args.output}")
    print("=" * 80)


if __name__ == "__main__":
    main()

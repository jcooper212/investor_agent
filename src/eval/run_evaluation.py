# ABOUTME: Command-line evaluation runner for testing the research agent
# ABOUTME: Supports both LLM-as-judge and OpenAI Evals, with comparison mode

import sys
from pathlib import Path
import argparse
import json
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.eval.test_runner import TestRunner
from src.eval.openai_evals_runner import OpenAIEvalsRunner


def run_llm_judge(test_set_path: str, output_path: str, verbose: bool = True) -> dict:
    """Run LLM-as-judge evaluation."""
    if verbose:
        print("\n" + "=" * 80)
        print("Running LLM-as-Judge Evaluation")
        print("=" * 80)

    runner = TestRunner(test_set_path)
    results = runner.run_full_evaluation(output_path=output_path, verbose=verbose)

    return results


def run_openai_evals(test_set_path: str, output_path: str, verbose: bool = True) -> dict:
    """Run OpenAI Evals-style evaluation."""
    if verbose:
        print("\n" + "=" * 80)
        print("Running OpenAI Evals-Style Evaluation")
        print("=" * 80)

    runner = OpenAIEvalsRunner(test_set_path)
    results = runner.run_evaluation(verbose=verbose)

    if output_path:
        runner.save_results(results, output_path)

    return results


def run_both_evaluators(
    test_set_path: str,
    llm_judge_output: str,
    evals_output: str,
    verbose: bool = True,
):
    """Run both evaluators sequentially."""
    if verbose:
        print("\n" + "=" * 80)
        print("Running Both Evaluators")
        print("=" * 80)

    # Run LLM judge
    llm_results = run_llm_judge(test_set_path, llm_judge_output, verbose)

    # Run OpenAI Evals
    evals_results = run_openai_evals(test_set_path, evals_output, verbose)

    # Quick comparison
    if verbose:
        print("\n" + "=" * 80)
        print("Quick Comparison")
        print("=" * 80)
        print(f"\nLLM-as-Judge:")
        print(f"  Overall Score: {llm_results['summary']['overall_average']:.2f}/5.0")
        print(f"  Pass Rate: {llm_results['summary']['pass_rate']*100:.1f}%")

        print(f"\nOpenAI Evals:")
        print(f"  Overall Score: {evals_results['summary']['overall_average']:.2f}")
        print(f"  Pass Rate: {evals_results['summary']['pass_rate']*100:.1f}%")

        print(f"\nFor detailed comparison, run:")
        print(f"  python src/eval/compare_evaluators.py \\")
        print(f"    --llm-judge {llm_judge_output} \\")
        print(f"    --evals {evals_output}")

    return llm_results, evals_results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run evaluation tests on the investment research agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run both evaluators
  python src/eval/run_evaluation.py --compare

  # Run only LLM-as-judge
  python src/eval/run_evaluation.py --evaluator llm-judge

  # Run only OpenAI Evals
  python src/eval/run_evaluation.py --evaluator openai-evals

  # Custom test set
  python src/eval/run_evaluation.py --test-set custom_tests.json --output results/custom.json
        """,
    )

    parser.add_argument(
        "--test-set",
        default="data/test_questions.json",
        help="Path to test questions JSON file (default: data/test_questions.json)",
    )

    parser.add_argument(
        "--evaluator",
        choices=["llm-judge", "openai-evals", "both"],
        default="both",
        help="Which evaluator to run (default: both)",
    )

    parser.add_argument(
        "--output",
        help="Custom output path for results (default: data/eval_results/<evaluator>_results.json)",
    )

    parser.add_argument(
        "--compare",
        action="store_true",
        help="Run both evaluators and compare (same as --evaluator both)",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )

    args = parser.parse_args()

    # Determine which evaluator(s) to run
    if args.compare:
        evaluator = "both"
    else:
        evaluator = args.evaluator

    # Determine output paths
    if args.output:
        if evaluator == "both":
            llm_output = args.output.replace(".json", "_llm_judge.json")
            evals_output = args.output.replace(".json", "_openai_evals.json")
        else:
            output_path = args.output
    else:
        llm_output = "data/eval_results/llm_judge_results.json"
        evals_output = "data/eval_results/openai_evals_results.json"
        output_path = llm_output if evaluator == "llm-judge" else evals_output

    # Print header
    if not args.quiet:
        print("=" * 80)
        print("Investment Research Agent - Evaluation Runner")
        print("=" * 80)
        print(f"\nTest Set: {args.test_set}")
        print(f"Evaluator: {evaluator}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run evaluation(s)
    try:
        if evaluator == "both":
            run_both_evaluators(
                args.test_set,
                llm_output,
                evals_output,
                verbose=not args.quiet,
            )

        elif evaluator == "llm-judge":
            run_llm_judge(args.test_set, output_path, verbose=not args.quiet)

        elif evaluator == "openai-evals":
            run_openai_evals(args.test_set, output_path, verbose=not args.quiet)

        if not args.quiet:
            print("\n" + "=" * 80)
            print("✅ Evaluation Complete!")
            if evaluator == "both":
                print(f"   LLM Judge Results: {llm_output}")
                print(f"   OpenAI Evals Results: {evals_output}")
            else:
                print(f"   Results: {output_path}")
            print("=" * 80)

    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

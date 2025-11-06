# ABOUTME: Comparison tool for analyzing LLM-as-judge vs OpenAI Evals results
# ABOUTME: Generates detailed recommendation report on which evaluator is better for what

import sys
from pathlib import Path
import argparse
import json
from typing import Dict, Any
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))


class EvaluatorComparison:
    """
    Compares LLM-as-judge and OpenAI Evals results across multiple dimensions.
    """

    def __init__(self, llm_judge_path: str, evals_path: str):
        """
        Initialize comparison.

        Args:
            llm_judge_path: Path to LLM judge results JSON
            evals_path: Path to OpenAI Evals results JSON
        """
        with open(llm_judge_path, "r") as f:
            self.llm_results = json.load(f)

        with open(evals_path, "r") as f:
            self.evals_results = json.load(f)

    def compare_overall_scores(self) -> Dict[str, Any]:
        """Compare overall evaluation scores."""
        llm_avg = self.llm_results["summary"]["overall_average"]
        evals_avg = self.evals_results["summary"]["overall_average"]

        return {
            "llm_judge_score": llm_avg,
            "openai_evals_score": evals_avg,
            "difference": abs(llm_avg - evals_avg),
            "winner": "llm-judge" if llm_avg > evals_avg else "openai-evals",
            "notes": "LLM judge uses 1-5 scale; OpenAI Evals uses 0-1 scale (normalized)",
        }

    def compare_by_category(self) -> Dict[str, Any]:
        """Compare performance across question categories."""
        llm_categories = self.llm_results["summary"]["category_breakdown"]
        evals_categories = self.evals_results["summary"]["category_breakdown"]

        comparison = {}
        for category in set(list(llm_categories.keys()) + list(evals_categories.keys())):
            llm_score = llm_categories.get(category, {}).get("avg_score", 0)
            evals_score = evals_categories.get(category, {}).get("avg_score", 0)

            # Normalize LLM score to 0-1 scale for comparison
            llm_normalized = llm_score / 5.0 if llm_score else 0

            comparison[category] = {
                "llm_judge": llm_normalized,
                "openai_evals": evals_score,
                "better_evaluator": "llm-judge" if llm_normalized > evals_score else "openai-evals",
            }

        return comparison

    def analyze_consistency(self) -> Dict[str, Any]:
        """
        Analyze consistency of evaluations.

        Note: True consistency testing requires multiple runs.
        This provides a proxy by looking at score variance.
        """
        # LLM judge variance (higher = less consistent)
        llm_evals = self.llm_results["evaluations"]
        llm_scores = [e["overall_score"] for e in llm_evals if "overall_score" in e]

        evals_evals = self.evals_results["evaluations"]
        evals_scores = [e["overall_score"] for e in evals_evals if "overall_score" in e]

        def calculate_variance(scores):
            if not scores:
                return 0
            mean = sum(scores) / len(scores)
            return sum((x - mean) ** 2 for x in scores) / len(scores)

        llm_variance = calculate_variance(llm_scores)
        evals_variance = calculate_variance(evals_scores)

        return {
            "llm_judge_variance": llm_variance,
            "openai_evals_variance": evals_variance,
            "more_consistent": "openai-evals" if evals_variance < llm_variance else "llm-judge",
            "note": "Lower variance suggests more consistent scoring. OpenAI Evals is expected to be more deterministic.",
        }

    def analyze_edge_cases(self) -> Dict[str, Any]:
        """Analyze how each evaluator handles edge cases."""
        # Get edge case evaluations
        llm_edge = [
            e for e in self.llm_results["evaluations"]
            if e.get("category") == "edge_cases"
        ]

        evals_edge = [
            e for e in self.evals_results["evaluations"]
            if e.get("category") == "edge_cases"
        ]

        llm_pass_rate = sum(1 for e in llm_edge if e.get("pass", False)) / len(llm_edge) if llm_edge else 0
        evals_pass_rate = sum(1 for e in evals_edge if e.get("passed", False)) / len(evals_edge) if evals_edge else 0

        return {
            "llm_judge_edge_pass_rate": llm_pass_rate,
            "openai_evals_edge_pass_rate": evals_pass_rate,
            "better_at_edges": "llm-judge" if llm_pass_rate > evals_pass_rate else "openai-evals",
            "interpretation": "Edge cases test out-of-scope handling and disclaimer compliance",
        }

    def generate_recommendations(self) -> Dict[str, str]:
        """
        Generate specific recommendations for when to use each evaluator.

        Returns:
            Dictionary mapping use cases to recommended evaluator
        """
        overall = self.compare_overall_scores()
        consistency = self.analyze_consistency()
        edge_cases = self.analyze_edge_cases()

        recommendations = {
            "factual_accuracy_testing": "openai-evals",
            "reasoning": "OpenAI Evals uses deterministic keyword matching for facts, reducing false positives",

            "citation_validation": "openai-evals",
            "reasoning": "Deterministic regex-based citation checking is more reliable than LLM judgment",

            "nuanced_evaluation": "llm-judge",
            "reasoning": "LLM judge can understand context and provide detailed reasoning for complex responses",

            "regression_testing": "openai-evals",
            "reasoning": f"More consistent (variance: {consistency['openai_evals_variance']:.3f} vs {consistency['llm_judge_variance']:.3f})",

            "edge_case_detection": edge_cases["better_at_edges"],
            "reasoning": f"Better pass rate on edge cases: {max(edge_cases['llm_judge_edge_pass_rate'], edge_cases['openai_evals_edge_pass_rate'])*100:.1f}%",

            "cost_efficiency": "openai-evals",
            "reasoning": "Single LLM call vs two calls (agent + judge) for LLM-as-judge",

            "debugging_failures": "llm-judge",
            "reasoning": "Provides detailed reasoning for each score, easier to understand why tests fail",

            "production_monitoring": "openai-evals",
            "reasoning": "Deterministic scoring better for tracking metrics over time",
        }

        return recommendations

    def generate_report(self, output_format: str = "markdown") -> str:
        """
        Generate comprehensive comparison report.

        Args:
            output_format: Format for report (markdown or json)

        Returns:
            Formatted report string
        """
        overall = self.compare_overall_scores()
        by_category = self.compare_by_category()
        consistency = self.analyze_consistency()
        edge_cases = self.analyze_edge_cases()
        recommendations = self.generate_recommendations()

        if output_format == "json":
            report = {
                "overall_comparison": overall,
                "category_comparison": by_category,
                "consistency_analysis": consistency,
                "edge_case_analysis": edge_cases,
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat(),
            }
            return json.dumps(report, indent=2)

        # Markdown format
        report = f"""# Evaluator Comparison Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This report compares LLM-as-judge and OpenAI Evals-style evaluation approaches for the Investment Research Agent.

### Overall Scores

| Evaluator | Score | Pass Rate |
|-----------|-------|-----------|
| **LLM-as-Judge** | {overall['llm_judge_score']:.2f}/5.0 | {self.llm_results['summary']['pass_rate']*100:.1f}% |
| **OpenAI Evals** | {overall['openai_evals_score']:.2f}/1.0 | {self.evals_results['summary']['pass_rate']*100:.1f}% |

**Winner**: {overall['winner']} (difference: {overall['difference']:.2f})

---

## Category-by-Category Comparison

| Category | LLM Judge | OpenAI Evals | Better |
|----------|-----------|--------------|--------|
"""

        for cat, scores in by_category.items():
            report += f"| {cat} | {scores['llm_judge']:.2f} | {scores['openai_evals']:.2f} | {scores['better_evaluator']} |\n"

        report += f"""
---

## Consistency Analysis

**Variance** (lower = more consistent):
- LLM-as-Judge: {consistency['llm_judge_variance']:.3f}
- OpenAI Evals: {consistency['openai_evals_variance']:.3f}

**More Consistent**: {consistency['more_consistent']}

{consistency['note']}

---

## Edge Case Handling

**Pass Rates on Edge Cases**:
- LLM-as-Judge: {edge_cases['llm_judge_edge_pass_rate']*100:.1f}%
- OpenAI Evals: {edge_cases['openai_evals_edge_pass_rate']*100:.1f}%

**Better at Edge Cases**: {edge_cases['better_at_edges']}

{edge_cases['interpretation']}

---

## Recommendations: Which Evaluator for What?

"""

        # Group recommendations by evaluator
        llm_judge_use_cases = []
        evals_use_cases = []

        for use_case, evaluator in recommendations.items():
            if use_case == "reasoning":
                continue
            reason = recommendations.get("reasoning", "")
            if evaluator == "llm-judge":
                llm_judge_use_cases.append((use_case.replace("_", " ").title(), reason))
            else:
                evals_use_cases.append((use_case.replace("_", " ").title(), reason))

        report += "### Use LLM-as-Judge For:\n\n"
        for use_case, reason in llm_judge_use_cases:
            report += f"- **{use_case}**: {reason}\n"

        report += "\n### Use OpenAI Evals For:\n\n"
        for use_case, reason in evals_use_cases:
            report += f"- **{use_case}**: {reason}\n"

        report += """
---

## Conclusion

Both evaluators have strengths:

- **LLM-as-Judge**: Better for nuanced evaluation, debugging, and understanding complex responses
- **OpenAI Evals**: Better for consistency, regression testing, and production monitoring

**Recommendation**: Use **both** in combination:
1. Use OpenAI Evals for continuous integration / regression testing
2. Use LLM-as-Judge for deep analysis of failures and edge cases
3. Consider **Arklex** for automated test generation and adversarial testing that neither approach provides

---

## Arklex Advantage

Both evaluators have limitations:
- Manual test creation required
- No adversarial probing
- Limited multi-turn state testing
- Cannot discover edge cases automatically

**Arklex addresses these gaps** with:
- Automated test case generation
- Adversarial scenario creation
- Multi-turn conversation testing
- Edge case discovery
- Objective metrics without LLM judgment bias

---

*This report was generated automatically. For questions, consult the evaluation documentation.*
"""

        return report


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Compare LLM-as-judge and OpenAI Evals results"
    )

    parser.add_argument(
        "--llm-judge",
        default="data/eval_results/llm_judge_results.json",
        help="Path to LLM judge results JSON",
    )

    parser.add_argument(
        "--evals",
        default="data/eval_results/openai_evals_results.json",
        help="Path to OpenAI Evals results JSON",
    )

    parser.add_argument(
        "--output",
        default="data/eval_results/comparison_report.md",
        help="Output path for comparison report",
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format",
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Evaluator Comparison Tool")
    print("=" * 80)
    print(f"\nLLM Judge Results: {args.llm_judge}")
    print(f"OpenAI Evals Results: {args.evals}")
    print(f"Output: {args.output}")
    print("\nGenerating comparison...")

    try:
        comparison = EvaluatorComparison(args.llm_judge, args.evals)
        report = comparison.generate_report(output_format=args.format)

        # Save report
        with open(args.output, "w") as f:
            f.write(report)

        print(f"\n✅ Comparison report saved to: {args.output}")
        print("\nPreview:")
        print("=" * 80)
        print(report[:1000] + "..." if len(report) > 1000 else report)

    except FileNotFoundError as e:
        print(f"\n❌ Error: Results file not found: {e}")
        print("Run evaluations first with: python src/eval/run_evaluation.py --compare")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Comparison failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

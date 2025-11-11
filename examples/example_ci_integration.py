"""Example of CI/CD integration."""

import sys
import json
from pathlib import Path
from src.agent import TestingAgent
from src.config import Config


def main():
    """Example CI/CD integration workflow."""
    print("Testing Agent - CI/CD Integration Example")
    print("=" * 70)
    print()

    # Load configuration from environment or use defaults
    config = Config.from_env()

    # Create agent
    agent = TestingAgent(config)

    # Run tests with coverage
    print("Running test suite with coverage...")
    result = agent.run_tests(coverage=True)
    print()

    # Generate multiple report formats
    print("Generating reports...")

    # Text report for console
    text_report = agent.generate_report(result, format="text")
    print(text_report)
    print()

    # JSON report for CI systems
    json_report = agent.generate_report(result, format="json")
    json_path = Path("reports/test-results.json")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w") as f:
        f.write(json_report)
    print(f"JSON report saved to {json_path}")

    # HTML report for artifacts
    html_report = agent.generate_report(result, format="html")
    html_path = Path("reports/test-results.html")
    with open(html_path, "w") as f:
        f.write(html_report)
    print(f"HTML report saved to {html_path}")
    print()

    # Check quality gates
    quality_gates = {
        "min_coverage": config.coverage_threshold,
        "max_failures": 0,
        "min_pass_rate": 90.0,
    }

    print("Checking quality gates...")
    gates_passed = True

    if result.coverage < quality_gates["min_coverage"]:
        print(f"  ✗ Coverage gate failed: {result.coverage:.1f}% < {quality_gates['min_coverage']}%")
        gates_passed = False
    else:
        print(f"  ✓ Coverage gate passed: {result.coverage:.1f}% >= {quality_gates['min_coverage']}%")

    if result.failed > quality_gates["max_failures"]:
        print(f"  ✗ Failure gate failed: {result.failed} failures (max: {quality_gates['max_failures']})")
        gates_passed = False
    else:
        print(f"  ✓ Failure gate passed: {result.failed} failures")

    pass_rate = result.success_rate()
    if pass_rate < quality_gates["min_pass_rate"]:
        print(f"  ✗ Pass rate gate failed: {pass_rate:.1f}% < {quality_gates['min_pass_rate']}%")
        gates_passed = False
    else:
        print(f"  ✓ Pass rate gate passed: {pass_rate:.1f}% >= {quality_gates['min_pass_rate']}%")

    print()

    if gates_passed:
        print("✓ All quality gates passed!")
        return 0
    else:
        print("✗ Quality gates failed!")

        # Provide analysis for failures
        if result.has_failures():
            analysis = agent.analyze_failures(result)
            print("\nFailure Analysis:")
            for suggestion in analysis.get("suggestions", []):
                print(f"  • {suggestion}")

        return 1


if __name__ == "__main__":
    sys.exit(main())

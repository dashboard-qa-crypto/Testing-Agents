#!/usr/bin/env python3
"""Interactive demonstration of the Testing Agent."""

import sys
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import TestingAgent
from src.config import Config


def print_banner(text, char="=", width=70):
    """Print a formatted banner."""
    print()
    print(char * width)
    print(f"  {text}")
    print(char * width)
    print()


def print_section(title):
    """Print a section header."""
    print()
    print(f"📋 {title}")
    print("-" * 70)


def demonstrate_basic_usage():
    """Demonstrate basic testing agent usage."""
    print_banner("🧪 TESTING AGENT - INTERACTIVE DEMONSTRATION", "=")

    print("Welcome to the Testing Agent!")
    print("This demonstration will show you all the features in action.")
    print()
    time.sleep(1)

    # Step 1: Create agent
    print_section("Step 1: Creating Testing Agent")
    print("Initializing agent with default configuration...")
    agent = TestingAgent()
    print(f"✓ Agent created successfully")
    print(f"  • Framework: {agent.config.test_framework}")
    print(f"  • Test Directory: {agent.config.test_directory}")
    print(f"  • Coverage Threshold: {agent.config.coverage_threshold}%")
    time.sleep(1)

    # Step 2: Run tests
    print_section("Step 2: Running Test Suite")
    print("Discovering and executing tests...")
    print()
    result = agent.run_tests(coverage=True)
    print(f"\n✓ Test execution completed in {result.duration:.2f} seconds")
    time.sleep(1)

    # Step 3: Generate report
    print_section("Step 3: Generating Test Report")
    report = agent.generate_report(result, format="text")
    print(report)
    time.sleep(1)

    # Step 4: Analyze results
    if result.has_failures():
        print_section("Step 4: Analyzing Failures")
        analysis = agent.analyze_failures(result)
        print("\n💡 Suggestions:")
        for i, suggestion in enumerate(analysis.get("suggestions", []), 1):
            print(f"  {i}. {suggestion}")
    else:
        print_section("Step 4: Test Analysis")
        print("✅ All tests passed! No failures to analyze.")
        analysis = agent.analyze_failures(result)
        for suggestion in analysis.get("suggestions", []):
            print(f"  • {suggestion}")

    time.sleep(1)

    # Step 5: Coverage analysis
    print_section("Step 5: Coverage Analysis")
    coverage_analysis = analysis.get("coverage_analysis", {})
    print(f"Coverage: {result.coverage:.1f}%")
    print(f"Status: {coverage_analysis.get('status', 'unknown').upper()}")
    print(f"Recommendation: {coverage_analysis.get('recommendation', 'N/A')}")
    time.sleep(1)

    # Step 6: Generate HTML report
    print_section("Step 6: Generating HTML Report")
    html_report = agent.generate_report(result, format="html")
    report_path = Path("reports/demo-report.html")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        f.write(html_report)
    print(f"✓ HTML report saved to: {report_path}")
    time.sleep(1)

    # Step 7: Generate JSON report
    print_section("Step 7: Generating JSON Report")
    json_report = agent.generate_report(result, format="json")
    json_path = Path("reports/demo-report.json")
    with open(json_path, "w") as f:
        f.write(json_report)
    print(f"✓ JSON report saved to: {json_path}")
    print()
    print("JSON Preview:")
    print(json_report[:500] + "...")
    time.sleep(1)

    # Final summary
    print_banner("✨ DEMONSTRATION COMPLETE", "=")
    print("The Testing Agent successfully:")
    print("  ✓ Discovered and ran all tests")
    print("  ✓ Collected code coverage metrics")
    print("  ✓ Analyzed test results")
    print("  ✓ Generated multiple report formats")
    print("  ✓ Provided intelligent suggestions")
    print()
    print("📂 Generated Files:")
    print(f"  • {report_path}")
    print(f"  • {json_path}")
    print()
    print("📊 Test Summary:")
    print(f"  • Total Tests: {result.total}")
    print(f"  • Passed: {result.passed}")
    print(f"  • Failed: {result.failed}")
    print(f"  • Skipped: {result.skipped}")
    print(f"  • Coverage: {result.coverage:.1f}%")
    print(f"  • Duration: {result.duration:.2f}s")
    print(f"  • Success Rate: {result.success_rate():.1f}%")
    print()

    return result.exit_code


def demonstrate_custom_config():
    """Demonstrate custom configuration."""
    print_banner("⚙️  CUSTOM CONFIGURATION DEMO", "=")

    config = Config(
        verbose=True,
        parallel=True,
        max_workers=2,
        coverage_threshold=70.0
    )

    print("Custom configuration created:")
    print(f"  • Verbose: {config.verbose}")
    print(f"  • Parallel: {config.parallel}")
    print(f"  • Max Workers: {config.max_workers}")
    print(f"  • Coverage Threshold: {config.coverage_threshold}%")
    print()

    agent = TestingAgent(config)
    print("Running tests with custom configuration...")
    result = agent.run_tests(coverage=True)

    report = agent.generate_report(result)
    print(report)

    if result.coverage >= config.coverage_threshold:
        print(f"✓ Coverage meets threshold ({config.coverage_threshold}%)")
    else:
        print(f"⚠ Coverage below threshold ({config.coverage_threshold}%)")

    return result.exit_code


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Testing Agent Demo")
    parser.add_argument(
        "--mode",
        choices=["basic", "custom", "both"],
        default="both",
        help="Demo mode to run"
    )

    args = parser.parse_args()

    try:
        if args.mode == "basic":
            sys.exit(demonstrate_basic_usage())
        elif args.mode == "custom":
            sys.exit(demonstrate_custom_config())
        else:
            exit_code1 = demonstrate_basic_usage()
            time.sleep(2)
            exit_code2 = demonstrate_custom_config()
            sys.exit(max(exit_code1, exit_code2))
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

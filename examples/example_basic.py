"""Basic example of using the testing agent."""

from src.agent import TestingAgent
from src.config import Config


def main():
    """Run a basic testing agent example."""
    print("=" * 70)
    print("Testing Agent - Basic Example")
    print("=" * 70)
    print()

    # Create a testing agent with default configuration
    print("Creating testing agent with default configuration...")
    agent = TestingAgent()
    print(f"  Test Framework: {agent.config.test_framework}")
    print(f"  Test Directory: {agent.config.test_directory}")
    print()

    # Run all tests
    print("Running all tests...")
    result = agent.run_tests(coverage=True)
    print()

    # Generate and display report
    print("Generating report...")
    report = agent.generate_report(result, format="text")
    print(report)
    print()

    # If there are failures, analyze them
    if result.has_failures():
        print("Analyzing failures...")
        analysis = agent.analyze_failures(result)

        print("\nSuggestions:")
        for suggestion in analysis.get("suggestions", []):
            print(f"  • {suggestion}")
    else:
        print("✓ All tests passed successfully!")

    print()
    print("=" * 70)
    return result.exit_code


if __name__ == "__main__":
    import sys
    sys.exit(main())

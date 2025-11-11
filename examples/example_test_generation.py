"""Example demonstrating test case generation functionality."""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import TestingAgent


def main():
    """Demonstrate test case generation features."""
    print("=" * 70)
    print("TESTING AGENT - TEST GENERATION DEMO")
    print("=" * 70)
    print()

    # Create agent
    agent = TestingAgent()

    # Step 1: Analyze test coverage gaps
    print("Step 1: Analyzing Test Coverage Gaps")
    print("-" * 70)
    report = agent.analyze_test_coverage_gaps()

    print(f"\n📊 Coverage Analysis Results:")
    print(f"  Total functions found: {report['total_functions']}")
    print(f"  Functions with tests: {report['tested_functions']}")
    print(f"  Functions without tests: {report['untested_functions']}")
    print(f"  Test coverage: {report['coverage_percentage']:.1f}%")

    print(f"\n📋 Breakdown by Complexity:")
    print(f"  Low complexity (1-2): {report['missing_by_complexity']['low']} functions")
    print(f"  Medium complexity (3-5): {report['missing_by_complexity']['medium']} functions")
    print(f"  High complexity (6+): {report['missing_by_complexity']['high']} functions")

    if report['missing_by_module']:
        print(f"\n📁 Missing Tests by Module:")
        for module, functions in list(report['missing_by_module'].items())[:5]:
            print(f"  {module}:")
            for func in functions[:3]:
                print(f"    - {func}")
            if len(functions) > 3:
                print(f"    ... and {len(functions) - 3} more")

    # Step 2: Generate test suggestions
    print("\n" + "=" * 70)
    print("Step 2: Generating Test Suggestions")
    print("-" * 70)

    suggestions = agent.generate_test_suggestions(
        save_to_file=True,
        output_file="test_suggestions.md"
    )

    print(f"\n✓ Generated {len(suggestions)} test suggestions")
    print(f"✓ Saved to test_suggestions.md")

    # Show some examples
    if suggestions:
        print(f"\n📝 Example Suggestions:")
        for i, suggestion in enumerate(suggestions[:5], 1):
            print(f"\n  {i}. {suggestion.test_name}")
            print(f"     Type: {suggestion.test_type}")
            print(f"     Priority: {suggestion.priority}/5")
            print(f"     Description: {suggestion.description}")

    # Step 3: Show breakdown by test type
    print("\n" + "=" * 70)
    print("Step 3: Test Suggestion Breakdown")
    print("-" * 70)

    by_type = {}
    for s in suggestions:
        by_type[s.test_type] = by_type.get(s.test_type, 0) + 1

    print(f"\n📊 Suggestions by Type:")
    for test_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        print(f"  {test_type}: {count} tests")

    # Step 4: Show priority distribution
    by_priority = {}
    for s in suggestions:
        by_priority[s.priority] = by_priority.get(s.priority, 0) + 1

    print(f"\n⭐ Suggestions by Priority:")
    for priority in sorted(by_priority.keys(), reverse=True):
        count = by_priority[priority]
        stars = "★" * priority + "☆" * (5 - priority)
        print(f"  {stars} Priority {priority}: {count} tests")

    # Step 5: Practical recommendations
    print("\n" + "=" * 70)
    print("Step 4: Recommendations")
    print("-" * 70)

    print("\n💡 What to do next:")
    print("\n  1. Review test_suggestions.md for detailed test templates")
    print("  2. Focus on high-priority tests first (Priority 4-5)")
    print("  3. Start with basic tests before edge cases")
    print("  4. Prioritize high-complexity functions for testing")
    print("\n  Example commands:")
    print("    # Generate tests via CLI")
    print("    python -m src.agent --generate-tests")
    print()
    print("    # Analyze coverage gaps")
    print("    python -m src.agent --analyze-gaps")
    print()
    print("    # Get suggestions for low coverage")
    print("    python -m src.agent --suggest-improvements")

    print("\n" + "=" * 70)
    print("Demo Complete! Check test_suggestions.md for details.")
    print("=" * 70)


if __name__ == "__main__":
    main()

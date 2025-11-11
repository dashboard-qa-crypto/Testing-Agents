#!/usr/bin/env python3
"""Interactive demonstration of test generation capabilities."""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import TestingAgent


def print_banner(text, char="="):
    """Print a formatted banner."""
    print()
    print(char * 70)
    print(f"  {text}")
    print(char * 70)
    print()


def main():
    """Run the test generation demonstration."""
    print_banner("🧪 TESTING AGENT - TEST GENERATION DEMO", "=")

    print("This demo will show you how the Testing Agent can:")
    print("  • Analyze your code to find functions without tests")
    print("  • Generate intelligent test case suggestions")
    print("  • Create test templates for untested code")
    print("  • Identify coverage gaps and prioritize testing efforts")
    print()

    input("Press Enter to start...")

    # Initialize agent
    print_banner("Step 1: Initialize Testing Agent", "-")
    print("Creating testing agent with test generation capabilities...")
    agent = TestingAgent()
    print("✓ Agent created with test generator enabled")

    input("\nPress Enter to continue...")

    # Analyze coverage gaps
    print_banner("Step 2: Analyze Test Coverage Gaps", "-")
    print("Scanning source code to find untested functions...")
    print()

    report = agent.analyze_test_coverage_gaps()

    print("✓ Analysis complete!")
    print()
    print("📊 Coverage Report:")
    print(f"  Total functions: {report['total_functions']}")
    print(f"  With tests: {report['tested_functions']}")
    print(f"  Without tests: {report['untested_functions']}")
    print(f"  Coverage: {report['coverage_percentage']:.1f}%")

    if report['untested_functions'] == 0:
        print("\n🎉 Perfect! All functions have tests!")
        return

    print()
    print("📋 Missing tests by complexity:")
    for level, count in report['missing_by_complexity'].items():
        if count > 0:
            emoji = "🟢" if level == "low" else "🟡" if level == "medium" else "🔴"
            print(f"  {emoji} {level.capitalize()}: {count} functions")

    if report['missing_by_module']:
        print()
        print("📁 Modules with missing tests:")
        for module, functions in list(report['missing_by_module'].items())[:3]:
            print(f"  • {module}: {len(functions)} functions")

    input("\nPress Enter to continue...")

    # Generate test suggestions
    print_banner("Step 3: Generate Test Suggestions", "-")
    print("Generating intelligent test case suggestions...")
    print()

    suggestions = agent.generate_test_suggestions(
        save_to_file=True,
        output_file="test_suggestions.md"
    )

    print(f"✓ Generated {len(suggestions)} test suggestions")
    print("✓ Saved detailed templates to test_suggestions.md")

    # Analyze suggestions
    by_type = {}
    by_priority = {}
    for s in suggestions:
        by_type[s.test_type] = by_type.get(s.test_type, 0) + 1
        by_priority[s.priority] = by_priority.get(s.priority, 0) + 1

    print()
    print("📊 Suggestion Breakdown:")
    print()
    print("  By Type:")
    for test_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        icon = {
            "basic": "🔵",
            "edge_case": "🟠",
            "error": "🔴",
            "parametrized": "🟣"
        }.get(test_type, "⚪")
        print(f"    {icon} {test_type}: {count}")

    print()
    print("  By Priority:")
    for priority in sorted(by_priority.keys(), reverse=True):
        count = by_priority[priority]
        stars = "⭐" * priority
        print(f"    {stars} Priority {priority}: {count} tests")

    input("\nPress Enter to see example suggestions...")

    # Show examples
    print_banner("Step 4: Example Test Suggestions", "-")

    # Group by priority
    high_priority = [s for s in suggestions if s.priority >= 4]

    if high_priority:
        print("🎯 High Priority Test Suggestions:")
        print()

        for i, suggestion in enumerate(high_priority[:3], 1):
            print(f"{i}. Test: {suggestion.test_name}")
            print(f"   Function: {suggestion.function_name}")
            print(f"   Type: {suggestion.test_type}")
            print(f"   Priority: {'⭐' * suggestion.priority}")
            print(f"   Description: {suggestion.description}")
            print()
            print("   Template Preview:")
            preview_lines = suggestion.template.split('\n')[:5]
            for line in preview_lines:
                print(f"   {line}")
            if len(suggestion.template.split('\n')) > 5:
                print("   ...")
            print()

    input("Press Enter to continue...")

    # Show what's in the generated file
    print_banner("Step 5: Generated Test File", "-")
    print("The detailed test suggestions have been saved to:")
    print("  📄 test_suggestions.md")
    print()
    print("This file contains:")
    print("  • Complete test templates ready to use")
    print("  • Organized by function")
    print("  • Sorted by priority")
    print("  • With helpful comments and TODOs")
    print()
    print("Example structure:")
    print("""
  ## function_name

  ### test_function_name_basic (Priority: 5)
  **Type:** basic
  **Description:** Basic functionality test

  ```python
  def test_function_name_basic():
      \"\"\"Test basic functionality.\"\"\"
      # Arrange
      # ...

      # Act
      result = function_name(args)

      # Assert
      assert result is not None
  ```
""")

    input("Press Enter to see recommendations...")

    # Final recommendations
    print_banner("Step 6: Recommendations", "-")

    print("💡 Next Steps:")
    print()
    print("1. Review test_suggestions.md")
    print("   • Start with Priority 5 tests")
    print("   • Focus on basic tests first")
    print()
    print("2. Copy templates to your test files")
    print("   • Fill in the TODOs with actual test logic")
    print("   • Add specific assertions")
    print()
    print("3. Run tests to verify they work")
    print("   python -m src.agent --verbose")
    print()
    print("4. Check improved coverage")
    print("   python -m src.agent --analyze-gaps")
    print()

    print("🔧 Useful Commands:")
    print()
    print("  # Generate test suggestions")
    print("  python -m src.agent --generate-tests")
    print()
    print("  # Analyze coverage gaps")
    print("  python -m src.agent --analyze-gaps")
    print()
    print("  # Get suggestions for improving coverage")
    print("  python -m src.agent --suggest-improvements --coverage-threshold 80")
    print()

    print_banner("✨ Demo Complete!", "=")
    print("The Testing Agent can now:")
    print("  ✓ Automatically find untested code")
    print("  ✓ Generate intelligent test suggestions")
    print("  ✓ Create ready-to-use test templates")
    print("  ✓ Prioritize testing efforts")
    print("  ✓ Help you reach your coverage goals")
    print()
    print("Happy testing! 🎉")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")
        sys.exit(0)

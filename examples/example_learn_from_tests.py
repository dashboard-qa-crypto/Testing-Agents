"""Example demonstrating learning from existing passing tests."""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import TestingAgent


def main():
    """Demonstrate learning from existing passing tests."""
    print("=" * 70)
    print("LEARNING FROM PASSING TESTS - DEMONSTRATION")
    print("=" * 70)
    print()

    print("This example shows how the Testing Agent can learn patterns from")
    print("your existing passing tests and use them to generate better test")
    print("suggestions for untested code.")
    print()

    # Create agent
    agent = TestingAgent()

    # Step 1: Learn from existing tests
    print("=" * 70)
    print("Step 1: Learning from Existing Tests")
    print("=" * 70)
    print()

    stats = agent.learn_from_passing_tests()

    print()
    print("📊 Learning Results:")
    print(f"  • Total patterns found: {stats['total_patterns']}")
    print(f"  • Test types learned: {dict(stats['by_type'])}")
    print()
    print("  Structure Analysis:")
    print(f"  • Arrange-Act-Assert pattern: {stats['by_structure']['arrange_act_assert']} tests")
    print(f"  • Using fixtures: {stats['by_structure']['uses_fixtures']} tests")
    print(f"  • Using mocks: {stats['by_structure']['uses_mocks']} tests")

    if stats['patterns']:
        print()
        print("  Example Learned Patterns:")
        for pattern in stats['patterns'][:3]:
            print(f"    • {pattern['name']} ({pattern['type']}) " +
                  f"{'✓ structured' if pattern['structured'] else ''}")

    # Step 2: Generate suggestions using learned patterns
    print()
    print("=" * 70)
    print("Step 2: Generating Tests with Learned Patterns")
    print("=" * 70)
    print()

    print("Now generating test suggestions using the learned patterns...")
    print()

    suggestions = agent.generate_test_suggestions(
        save_to_file=True,
        output_file="test_suggestions_with_learning.md",
        learn_from_existing=False  # Already learned above
    )

    print()
    print(f"✓ Generated {len(suggestions)} test suggestions")
    print()

    # Step 3: Show comparison
    print("=" * 70)
    print("Step 3: Benefits of Learning from Existing Tests")
    print("=" * 70)
    print()

    print("🎯 What the agent learned and applied:")
    print()

    # Count learned patterns
    basic_patterns = stats['by_type'].get('basic', 0)
    edge_patterns = stats['by_type'].get('edge_case', 0)
    error_patterns = stats['by_type'].get('error', 0)

    print(f"1. Test Structure & Style")
    print(f"   • Learned from {basic_patterns} basic test patterns")
    print(f"   • Matches your project's testing style")
    print(f"   • Uses similar assertion patterns")
    print()

    print(f"2. Test Organization")
    if stats['by_structure']['arrange_act_assert'] > 0:
        print(f"   • Uses Arrange-Act-Assert pattern")
    if stats['by_structure']['uses_fixtures']:
        print(f"   • Can suggest fixture usage")
    if stats['by_structure']['uses_mocks']:
        print(f"   • Understands mocking patterns")
    print()

    print(f"3. Test Types")
    print(f"   • Basic tests: Based on {basic_patterns} examples")
    if edge_patterns > 0:
        print(f"   • Edge cases: Based on {edge_patterns} examples")
    if error_patterns > 0:
        print(f"   • Error handling: Based on {error_patterns} examples")
    print()

    # Step 4: Example comparison
    print("=" * 70)
    print("Step 4: See the Difference")
    print("=" * 70)
    print()

    print("Compare the generated tests:")
    print()
    print("WITHOUT learning:")
    print("  def test_function_basic():")
    print("      assert result is not None")
    print("      # TODO: Add specific assertions")
    print()
    print("WITH learning (includes learned test name):")
    print("  def test_function_basic():")
    print("      # (learned from test_agent_initialization)")
    print("      assert result is not None")
    print("      # TODO: Add specific assertions for function")
    print()

    # Step 5: Next steps
    print("=" * 70)
    print("Step 5: Next Steps")
    print("=" * 70)
    print()

    print("✓ Learned patterns saved and will be used for future suggestions")
    print()
    print("To generate tests with learning enabled (default):")
    print("  python -m src.agent --generate-tests")
    print()
    print("To explicitly learn first, then generate:")
    print("  python -m src.agent --learn-from-tests")
    print("  python -m src.agent --generate-tests")
    print()
    print("The more tests you have, the better the learning!")
    print("The agent will:")
    print("  • Match your testing style")
    print("  • Use similar patterns")
    print("  • Create consistent test structures")
    print()

    print("=" * 70)
    print("✨ Demo Complete!")
    print("=" * 70)
    print()
    print("Check test_suggestions_with_learning.md to see the results!")
    print()


if __name__ == "__main__":
    main()

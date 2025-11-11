"""Example using custom configuration."""

from src.agent import TestingAgent
from src.config import Config


def main():
    """Run testing agent with custom configuration."""
    print("Testing Agent - Custom Configuration Example")
    print("=" * 70)
    print()

    # Create custom configuration
    config = Config(
        test_framework="pytest",
        test_directory="tests",
        verbose=True,
        parallel=True,
        max_workers=4,
        coverage_threshold=85.0,
        fail_fast=False,
    )

    print("Custom Configuration:")
    print(f"  Framework: {config.test_framework}")
    print(f"  Directory: {config.test_directory}")
    print(f"  Verbose: {config.verbose}")
    print(f"  Parallel: {config.parallel}")
    print(f"  Max Workers: {config.max_workers}")
    print(f"  Coverage Threshold: {config.coverage_threshold}%")
    print()

    # Save configuration to file
    config.save("config.json")
    print("Configuration saved to config.json")
    print()

    # Create agent with custom config
    agent = TestingAgent(config)

    # Run tests with specific pattern
    print("Running tests matching 'test_agent*'...")
    result = agent.run_tests(pattern="test_agent*", coverage=True)
    print()

    # Display results
    report = agent.generate_report(result)
    print(report)

    # Check coverage threshold
    if result.coverage < config.coverage_threshold:
        print(f"\n⚠ Warning: Coverage ({result.coverage:.1f}%) is below threshold ({config.coverage_threshold}%)")
    else:
        print(f"\n✓ Coverage ({result.coverage:.1f}%) meets threshold!")

    return result.exit_code


if __name__ == "__main__":
    import sys
    sys.exit(main())

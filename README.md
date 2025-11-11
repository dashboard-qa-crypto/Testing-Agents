# Testing Agent

An intelligent testing agent that can automatically run tests, analyze results, provide detailed feedback, and **generate new test cases** for untested code.

## Features

### Test Execution & Analysis
- **Automatic Test Discovery**: Finds and runs all tests in your project
- **Intelligent Analysis**: Uses AI to analyze test results and suggest fixes
- **Detailed Reporting**: Provides comprehensive test reports with statistics
- **Multiple Framework Support**: Works with pytest, unittest, and more
- **CI/CD Integration**: Easy integration with continuous integration pipelines

### 🆕 Test Generation (NEW!)
- **Smart Test Case Generation**: Automatically generates test suggestions for untested code
- **Coverage Gap Analysis**: Identifies functions and modules missing tests
- **Multiple Test Types**: Generates basic, edge case, error handling, and parametrized tests
- **Priority-Based Suggestions**: Ranks tests by importance and complexity
- **Ready-to-Use Templates**: Creates complete test templates with TODO markers

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from src.agent import TestingAgent

# Create a testing agent
agent = TestingAgent()

# Run all tests
results = agent.run_tests()

# Get a detailed report
report = agent.generate_report(results)
print(report)
```

### Running Specific Tests

```python
# Run tests in a specific directory
results = agent.run_tests(path="tests/unit")

# Run tests matching a pattern
results = agent.run_tests(pattern="test_auth*")
```

### Analyzing Failures

```python
# Analyze test failures and get suggestions
if results.has_failures():
    analysis = agent.analyze_failures(results)
    print(analysis.suggestions)
```

### 🆕 Generating Test Cases

```python
# Analyze coverage gaps
report = agent.analyze_test_coverage_gaps()
print(f"Functions without tests: {report['untested_functions']}")

# Generate test suggestions
suggestions = agent.generate_test_suggestions()
print(f"Generated {len(suggestions)} test suggestions")

# Get suggestions for low coverage modules
agent.suggest_tests_for_low_coverage(threshold=80.0)
```

## Configuration

Create a `config.json` file to customize the agent:

```json
{
  "test_framework": "pytest",
  "test_directory": "tests",
  "coverage_threshold": 80,
  "verbose": true,
  "parallel": true
}
```

## Command Line Interface

### Running Tests

```bash
# Run all tests
python -m src.agent

# Run with verbose output
python -m src.agent --verbose

# Run specific test file
python -m src.agent --path tests/test_example.py

# Run tests in parallel
python -m src.agent --parallel
```

### 🆕 Generating Tests

```bash
# Generate test suggestions for untested code
python -m src.agent --generate-tests

# Analyze coverage gaps
python -m src.agent --analyze-gaps

# Get suggestions for improving coverage
python -m src.agent --suggest-improvements --coverage-threshold 80

# Save suggestions to custom file
python -m src.agent --generate-tests --output my_tests.md
```

## Examples

Check the `examples/` directory for more usage examples:

- `example_basic.py` - Basic test execution
- `example_custom_config.py` - Custom configuration
- `example_ci_integration.py` - CI/CD integration
- `example_test_generation.py` - 🆕 Test case generation
- `demo.py` - Interactive demonstration
- `demo_test_generation.py` - 🆕 Test generation demo

## Development

### Running Tests

```bash
pytest tests/
```

### Code Coverage

```bash
pytest --cov=src tests/
```

### Code Formatting

```bash
black src/ tests/
```

## Project Structure

```
Testing-Agents/
├── src/
│   ├── agent.py          # Main testing agent
│   ├── config.py         # Configuration management
│   ├── analyzer.py       # Test result analyzer
│   ├── test_generator.py # 🆕 Test case generator
│   └── utils/
│       ├── reporter.py   # Report generation
│       └── helpers.py    # Utility functions
├── tests/
│   ├── test_agent.py
│   ├── test_analyzer.py
│   └── test_config.py
├── examples/
│   ├── example_basic.py
│   ├── example_custom_config.py
│   ├── example_ci_integration.py
│   └── example_test_generation.py  # 🆕
├── demo.py               # Interactive demo
├── demo_test_generation.py  # 🆕 Test generation demo
└── requirements.txt
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

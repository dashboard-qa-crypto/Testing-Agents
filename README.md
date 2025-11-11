# Testing Agent

An intelligent testing agent that can automatically run tests, analyze results, and provide detailed feedback.

## Features

- **Automatic Test Discovery**: Finds and runs all tests in your project
- **Intelligent Analysis**: Uses AI to analyze test results and suggest fixes
- **Detailed Reporting**: Provides comprehensive test reports with statistics
- **Multiple Framework Support**: Works with pytest, unittest, and more
- **CI/CD Integration**: Easy integration with continuous integration pipelines

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

Run tests from the command line:

```bash
# Run all tests
python -m src.agent

# Run with verbose output
python -m src.agent --verbose

# Run specific test file
python -m src.agent --path tests/test_example.py

# Generate coverage report
python -m src.agent --coverage
```

## Examples

Check the `examples/` directory for more usage examples:

- `example_basic.py` - Basic test execution
- `example_analysis.py` - Analyzing test results
- `example_integration.py` - CI/CD integration

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
│   └── utils/
│       ├── reporter.py   # Report generation
│       └── helpers.py    # Utility functions
├── tests/
│   ├── test_agent.py
│   ├── test_analyzer.py
│   └── test_utils.py
├── examples/
│   └── example_basic.py
└── requirements.txt
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

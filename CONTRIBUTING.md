# Contributing to Testing Agent

Thank you for your interest in contributing to Testing Agent! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/Testing-Agents.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Install development dependencies: `pip install -e ".[dev]"`

## Development Workflow

### Running Tests

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html tests/
```

### Code Style

We use Black for code formatting and flake8 for linting.

Format your code:
```bash
black src/ tests/ examples/
```

Check for linting issues:
```bash
flake8 src/ tests/ examples/
```

Sort imports:
```bash
isort src/ tests/ examples/
```

### Type Checking

We use mypy for type checking:
```bash
mypy src/
```

## Making Changes

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Add tests for your changes
4. Ensure all tests pass
5. Ensure code is formatted and passes linting
6. Commit your changes: `git commit -m "Description of changes"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Ensure all tests pass
- Maintain or improve code coverage
- Follow the existing code style
- Update documentation as needed

## Code Review Process

1. A maintainer will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged

## Reporting Issues

When reporting issues, please include:

- A clear description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Python version and OS
- Any relevant error messages or logs

## Feature Requests

We welcome feature requests! Please:

- Check if the feature has already been requested
- Provide a clear description of the feature
- Explain the use case and benefits
- Be open to discussion and feedback

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Assume good intentions

## Questions?

If you have questions, feel free to:

- Open an issue for discussion
- Reach out to the maintainers

Thank you for contributing!

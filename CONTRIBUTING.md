# Contributing to Klydo MCP Server

First off, thank you for considering contributing to Klydo MCP Server! 🎉

This project is part of [Klydo](https://klydo.in), a Gen-Z quick tech fashion commerce startup based in Bangalore. We welcome contributions from the community to make this project even better.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. We expect all contributors to:

- Be respectful and considerate in all interactions
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/klydo-mcp.git
   cd klydo-mcp
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/myselfshravan/klydo-mcp.git
   ```

## Development Setup

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setup with uv (Recommended)

```bash
# Install dependencies
uv sync --dev

# Run the server locally
uv run klydo

# Run tests
uv run pytest
```

### Setup with pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

### Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and configure as needed (API tokens, etc.)

## How to Contribute

### Reporting Bugs

- Check if the bug has already been reported in [Issues](https://github.com/myselfshravan/klydo-mcp/issues)
- If not, create a new issue with:
  - Clear, descriptive title
  - Steps to reproduce
  - Expected vs actual behavior
  - Python version and OS
  - Relevant logs/error messages

### Suggesting Features

- Open an issue with the `enhancement` label
- Describe the feature and its use case
- Explain why it would benefit users

### Contributing Code

1. **Find an issue** to work on or create one first
2. **Comment on the issue** to let others know you're working on it
3. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** following our coding standards
5. **Write/update tests** for your changes
6. **Run the test suite** to ensure everything passes
7. **Commit your changes** with clear messages
8. **Push to your fork** and create a Pull Request

## Pull Request Process

1. **Update documentation** if you've changed APIs or added features
2. **Add tests** for new functionality
3. **Ensure CI passes** - all tests and linting must pass
4. **Request review** from maintainers
5. **Address feedback** promptly and constructively

### PR Title Format

Use clear, descriptive titles:
- `feat: Add new search filter for colors`
- `fix: Handle empty API response gracefully`
- `docs: Update installation instructions`
- `test: Add tests for scraper cache`
- `refactor: Simplify product parsing logic`

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for all public functions
- Maximum line length: 100 characters
- Use descriptive variable and function names

### Code Quality Tools

```bash
# Format code with Ruff
uv run ruff format src/

# Lint code with Ruff
uv run ruff check src/

# Type checking (optional)
uv run mypy src/klydo
```

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Keep the first line under 72 characters
- Reference issues when relevant: "Fix #123"

### Documentation

- Add docstrings to all public modules, classes, and functions
- Use Google-style docstrings
- Update README if adding new features
- Update CHANGELOG for notable changes

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_models.py

# Run with coverage
uv run pytest --cov=klydo
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Use descriptive test function names
- Use fixtures for common test data
- Mock external API calls

### Test Categories

- **Unit tests**: Test individual functions/methods
- **Integration tests**: Test component interactions
- **Scraper tests**: Test with mocked HTTP responses

## Need Help?

- Create an issue with your question
- Check existing issues and discussions
- Review the documentation

Thank you for contributing! 🚀
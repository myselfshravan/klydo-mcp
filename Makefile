.PHONY: help install dev test lint format clean build publish-test publish run

# Default target
help:
	@echo "Klydo MCP Server - Development Commands"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Development:"
	@echo "  install      Install production dependencies"
	@echo "  dev          Install development dependencies"
	@echo "  run          Run the MCP server"
	@echo ""
	@echo "Testing:"
	@echo "  test         Run all tests"
	@echo "  test-cov     Run tests with coverage"
	@echo "  test-v       Run tests with verbose output"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         Run linter (ruff check)"
	@echo "  format       Format code (ruff format)"
	@echo "  check        Run all checks (lint + format check)"
	@echo ""
	@echo "Build & Release:"
	@echo "  build        Build package (wheel + sdist)"
	@echo "  publish-test Publish to TestPyPI"
	@echo "  publish      Publish to PyPI"
	@echo "  clean        Remove build artifacts"
	@echo ""

# Install production dependencies
install:
	uv sync

# Install development dependencies  
dev:
	uv sync --dev

# Run the MCP server
run:
	uv run klydo

# Run all tests
test:
	uv run pytest

# Run tests with coverage
test-cov:
	uv run pytest --cov=klydo --cov-report=term-missing

# Run tests with verbose output
test-v:
	uv run pytest -v --tb=short

# Run linter
lint:
	uv run ruff check src/ tests/

# Format code
format:
	uv run ruff format src/ tests/

# Check formatting (no changes)
format-check:
	uv run ruff format --check src/ tests/

# Run all checks
check: lint format-check
	@echo "All checks passed!"

# Build package
build: clean
	uv pip install build
	python -m build

# Publish to TestPyPI
publish-test: build
	uv pip install twine
	twine upload --repository testpypi dist/*

# Publish to PyPI
publish: build
	uv pip install twine
	twine upload dist/*

# Clean build artifacts
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Install pre-commit hooks
pre-commit-install:
	uv pip install pre-commit
	pre-commit install

# Run pre-commit on all files
pre-commit:
	pre-commit run --all-files

# Update dependencies
update:
	uv lock --upgrade
	uv sync --dev

# Show outdated dependencies
outdated:
	uv pip list --outdated
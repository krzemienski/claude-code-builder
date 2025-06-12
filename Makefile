.PHONY: help install dev-install format lint type-check test clean build publish docs

# Default target
help:
	@echo "Claude Code Builder - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install production dependencies"
	@echo "  make dev-install    Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make format         Format code with black and ruff"
	@echo "  make lint           Run linting checks"
	@echo "  make type-check     Run mypy type checking"
	@echo "  make test           Run functional tests"
	@echo "  make clean          Clean build artifacts"
	@echo ""
	@echo "Build & Release:"
	@echo "  make build          Build distribution packages"
	@echo "  make publish        Publish to PyPI"
	@echo "  make docs           Build documentation"
	@echo ""
	@echo "Shortcuts:"
	@echo "  make all            Run format, lint, type-check"
	@echo "  make check          Run lint and type-check"

# Installation
install:
	poetry install --only main

dev-install:
	poetry install
	pre-commit install

# Code quality
format:
	poetry run black src tests
	poetry run ruff check --fix src tests

lint:
	poetry run ruff check src tests
	poetry run black --check src tests

type-check:
	poetry run mypy src

# Testing
test:
	@echo "Running functional tests..."
	poetry build
	pip install dist/*.whl
	claude-code-builder --version
	@echo "Functional tests passed!"

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Building
build: clean
	poetry build

# Publishing
publish: build
	poetry publish

# Documentation
docs:
	cd docs && make html

# Combined commands
all: format lint type-check

check: lint type-check

# Development shortcuts
dev: dev-install
	@echo "Development environment ready!"

run:
	poetry run claude-code-builder

# Git shortcuts
commit-format:
	@echo "Commit format: type(scope): description"
	@echo ""
	@echo "Types: feat, fix, docs, style, refactor, test, chore"
	@echo "Example: feat(agents): implement spec analyzer"
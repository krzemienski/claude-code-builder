# Simple Calculator Project

## Overview
Build a simple command-line calculator application in Python.

## Features
- Basic arithmetic operations (add, subtract, multiply, divide)
- Command-line interface
- Error handling for invalid input
- Support for decimal numbers

## Requirements
- Python 3.11+
- Click for CLI
- Rich for output formatting

## Architecture
```
calculator/
├── src/
│   └── calculator/
│       ├── __init__.py
│       ├── operations.py  # Core arithmetic functions
│       └── cli.py         # CLI interface
├── tests/
│   └── test_operations.py # Functional tests
├── pyproject.toml
└── README.md
```

## Success Criteria
- All arithmetic operations work correctly
- CLI accepts user input and displays results
- Error handling for division by zero
- Tests pass for all operations

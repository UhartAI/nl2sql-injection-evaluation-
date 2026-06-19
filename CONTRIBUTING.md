# Contributing to NL2SQL Injection Evaluation Framework

We welcome contributions! Please follow these guidelines.

## Getting Started

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `make test`
5. Format code: `make format`
6. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone git@github.com:yourusername/nl2sql-injection-evaluation.git
cd nl2sql-injection-evaluation

# Install development dependencies
make setup
make install-dev

# Run tests
make test

# Run linters
make lint

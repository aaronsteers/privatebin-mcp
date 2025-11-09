# Contributing to PrivateBin MCP

Thank you for your interest in contributing to the PrivateBin MCP server!

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/aaronsteers/privatebin-mcp.git
cd privatebin-mcp

# Install dependencies
uv sync --extra dev
```

## Development Commands

### Code Quality

```bash
# Format code
uv run ruff format .

# Check formatting (without modifying files)
uv run ruff format --check .

# Run linting
uv run ruff check .

# Check dependencies
uv run deptry .
```

### Testing

```bash
# Run tests with coverage
uv run pytest --cov=privatebin_mcp --cov-report=xml --cov-report=term
```

### Run All Checks (what CI runs)

```bash
uv run ruff format --check . && \
uv run ruff check . && \
uv run deptry . && \
uv run pytest --cov=privatebin_mcp --cov-report=xml --cov-report=term
```

## Pull Request Process

1. Create a new branch for your changes
2. Make your changes and ensure all checks pass locally
3. Push your branch and create a pull request
4. The CI will automatically run all checks on your PR
5. Address any feedback from reviewers

## Code Style

This project uses:
- **ruff** for code formatting and linting
- **basedpyright** for type checking
- **deptry** for dependency analysis
- **pytest** for testing

Please ensure your code follows these standards before submitting a PR.

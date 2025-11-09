🎉 **Thanks for opening this pull request!**

Your contribution is appreciated. Here are some helpful commands you can use:

## Development Commands

### Setup
```bash
# Install dependencies
uv sync --extra dev
```

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

### All Checks (what CI runs)
```bash
uv run ruff format --check . && \
uv run ruff check . && \
uv run deptry . && \
uv run pytest --cov=privatebin_mcp --cov-report=xml --cov-report=term
```

The CI will automatically run all checks when you push commits. Happy coding! 🚀

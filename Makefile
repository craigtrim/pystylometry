.PHONY: help install install-dev test lint format clean all

help:
	@echo "Available targets:"
	@echo "  install      Install package with core dependencies"
	@echo "  install-dev  Install package with dev dependencies"
	@echo "  test         Run tests with coverage"
	@echo "  lint         Run linters (ruff, mypy)"
	@echo "  format       Format code with ruff"
	@echo "  clean        Remove build artifacts"
	@echo "  all          Format, lint, and test"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,all]"

test:
	pytest tests/ -v --cov=pystylometry --cov-report=term-missing

lint:
	ruff check .
	mypy pystylometry/

format:
	ruff format .

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov/ .mypy_cache/ .ruff_cache/

all: format lint test

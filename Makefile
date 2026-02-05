.PHONY: help install install-dev setup setup-spacy test lint format clean build dist publish-test publish all lock

help:
	@echo "Available targets:"
	@echo "  setup         First-time setup (install dev dependencies + spaCy model)"
	@echo "  setup-spacy   Download spaCy model for enhanced Gunning Fog mode"
	@echo "  install       Install package with core dependencies"
	@echo "  install-dev   Install package with dev dependencies"
	@echo "  test          Run tests with coverage"
	@echo "  lint          Run linters (ruff, mypy)"
	@echo "  format        Format code with ruff"
	@echo "  clean         Remove build artifacts"
	@echo "  build         Build package distribution"
	@echo "  dist          Alias for build"
	@echo "  publish-test  Publish to TestPyPI"
	@echo "  publish       Publish to PyPI (production)"
	@echo "  all           Complete build: clean, format, lint, test, build"
	@echo "  lock          Clear Poetry cache and regenerate lock file"
	@echo ""
	@echo "Quick start: make setup && make all"

setup-spacy:
	@echo "Downloading spaCy model for enhanced Gunning Fog Index..."
	python -m spacy download en_core_web_sm

setup:
	pip install -e ".[dev,all]"
	pip install build twine
	@$(MAKE) setup-spacy

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

build: clean
	python -m build

dist: build

publish-test: build
	python -m twine upload --repository testpypi dist/*

publish: build
	python -m twine upload dist/*

lock:
	poetry cache clear pypi --all -n
	poetry lock

all: clean format lint test build
	@echo ""
	@echo "✅ Build complete! Package is ready in dist/"
	@echo ""
	@echo "Next steps:"
	@echo "  - Review dist/ contents"
	@echo "  - Test locally: pip install dist/*.whl"
	@echo "  - Publish to TestPyPI: make publish-test"
	@echo "  - Publish to PyPI: make publish"

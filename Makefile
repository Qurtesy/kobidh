# Makefile for Kobidh development workflow

.PHONY: help install install-dev test test-cov lint format clean build release

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -e ".[dev]"
	pre-commit install

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=kobidh --cov-report=html --cov-report=term

lint:  ## Run linting checks
	flake8 kobidh tests
	mypy kobidh

format:  ## Format code with black
	black kobidh tests scripts

format-check:  ## Check code formatting
	black --check kobidh tests scripts

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	python -m build

release:  ## Release to PyPI (requires proper credentials)
	python -m build
	python -m twine upload dist/*

setup-dev:  ## Complete development setup
	python3 -m venv venv
	source venv/bin/activate && pip install --upgrade pip setuptools wheel
	source venv/bin/activate && pip install -e ".[dev]"
	source venv/bin/activate && pre-commit install
	@echo "Development environment ready! Activate with: source venv/bin/activate"

docker-build:  ## Build Docker image
	docker build -t kobidh:latest .

docker-run:  ## Run Docker container
	docker run -it --rm -v ~/.aws:/root/.aws kobidh:latest

# Quick development tasks
quick-test:  ## Run quick tests (excluding slow/integration tests)
	pytest -m "not slow and not integration"

quick-check:  ## Run quick quality checks
	black --check kobidh tests
	flake8 kobidh tests --select=E9,F63,F7,F82

# AWS-specific tasks
aws-check:  ## Check AWS credentials and connectivity
	aws sts get-caller-identity

aws-regions:  ## List available AWS regions
	aws ec2 describe-regions --output table

# Project tasks
todo:  ## Show TODO items in code
	@grep -r "TODO\|FIXME\|XXX" kobidh/ --include="*.py" || echo "No TODO items found"

lines:  ## Count lines of code
	@find kobidh -name "*.py" -exec wc -l {} + | tail -1

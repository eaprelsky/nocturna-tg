.PHONY: help setup install run test clean format lint

# Python version
PYTHON_VERSION := 3.11
ENV_NAME := nocturna-tg

help:
	@echo "Nocturna Telegram Bot - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup       - Create conda environment with Python $(PYTHON_VERSION)"
	@echo "  make install     - Install dependencies"
	@echo "  make env         - Generate .env file from .env.example"
	@echo ""
	@echo "Development:"
	@echo "  make run         - Run the bot"
	@echo "  make test        - Run tests"
	@echo "  make format      - Format code with black"
	@echo "  make lint        - Run linters"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean       - Remove temporary files"
	@echo ""

setup:
	@echo "Creating conda environment: $(ENV_NAME)"
	conda create -n $(ENV_NAME) python=$(PYTHON_VERSION) -y
	@echo "Environment created. Activate with: conda activate $(ENV_NAME)"

install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "Dependencies installed successfully"

env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo ".env file created from .env.example"; \
		echo "Please edit .env and add your credentials"; \
	else \
		echo ".env file already exists"; \
	fi

run:
	@echo "Starting Nocturna Telegram Bot..."
	python -m src.main

test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

format:
	@echo "Formatting code..."
	black src/ tests/
	@echo "Code formatted successfully"

lint:
	@echo "Running linters..."
	flake8 src/ tests/ --max-line-length=100 --exclude=__pycache__
	mypy src/ --ignore-missing-imports
	@echo "Linting completed"

clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache .coverage htmlcov/ .mypy_cache/
	@echo "Clean completed"


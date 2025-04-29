.PHONY: test.% test lint format install install-dev clean run help coverage

export PYTHONPATH := $(CURDIR):$(PYTHONPATH)
export DJANGO_SETTINGS_MODULE := content_management_service.settings.development

# Help command
help:
	@echo "Available commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make install-dev      - Install development dependencies"
	@echo "  make lint             - Run linter checks"
	@echo "  make format           - Format code"
	@echo "  make test             - Run all tests"
	@echo "  make test.app         - Run all tests for a specific app"
	@echo "  make test.app.module  - Run tests for a specific module"
	@echo "  make test.app.module.class       - Run tests for a specific class"
	@echo "  make test.app.module.class.method - Run a specific test method"
	@echo "  make coverage         - Generate test coverage report"
	@echo "  make run              - Start development server"
	@echo "  make run-prod         - Start production server"
	@echo "  make clean            - Remove build artifacts and cache files"
	@echo ""
	@echo "Example:"
	@echo "  make test.sale.api.test_discount_api"

# Installation targets
install:
	@echo "Installing dependencies..."
	@uv pip install -e .

install-dev:
	@echo "Installing development dependencies..."
	@uv pip install -e ".[dev]"

# Code quality targets
lint:
	@echo "Running linter..."
	@ruff check .

format:
	@echo "Formatting code..."
	@ruff format .

# Test targets
test:
	@echo "Running all tests"
	@export DJANGO_SETTINGS_MODULE=content_management_service.settings.test && coverage run manage.py test

# Special pattern rule for running tests with dot notation
test.%:
	$(eval export DJANGO_SETTINGS_MODULE=content_management_service.settings.test)
	$(eval PARTS := $(subst ., ,$*))
	$(eval APP := $(word 1,$(PARTS)))
	$(eval MODULE := $(word 2,$(PARTS)))
	$(eval CLASS := $(word 3,$(PARTS)))
	$(eval METHOD := $(word 4,$(PARTS)))

	@if [ -n "$(APP)" ]; then \
		if [ -n "$(METHOD)" ]; then \
			echo "Running test: apps.$(APP).tests.$(MODULE).$(CLASS).$(METHOD)"; \
			coverage run manage.py test apps.$(APP).tests.$(MODULE).$(CLASS).$(METHOD); \
		elif [ -n "$(CLASS)" ]; then \
			echo "Running tests in class: apps.$(APP).tests.$(MODULE).$(CLASS)"; \
			coverage run manage.py test apps.$(APP).tests.$(MODULE).$(CLASS); \
		elif [ -n "$(MODULE)" ]; then \
			echo "Running tests in module: apps.$(APP).tests.$(MODULE)"; \
			coverage run manage.py test apps.$(APP).tests.$(MODULE); \
		else \
			echo "Running tests in app: apps.$(APP).tests"; \
			coverage run manage.py test apps.$(APP).tests; \
		fi; \
	fi

# Coverage report
coverage:
	@echo "Generating coverage report..."
	@coverage report -m
	@coverage html
	@echo "HTML report generated in htmlcov/ directory"

# Run targets
run:
	@echo "Starting development server..."
	@python manage.py runserver

run-prod:
	@echo "Starting production server..."
	@export DJANGO_SETTINGS_MODULE=content_management_service.settings.production && python manage.py runserver

# Cleanup
clean:
	@echo "Cleaning up..."
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".coverage" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name "*.egg" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".coverage" -exec rm -rf {} +
	@find . -type d -name "htmlcov" -exec rm -rf {} +
	@find . -type d -name ".ruff_cache" -exec rm -rf {} +
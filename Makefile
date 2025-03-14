.PHONY: test.% test lint format install install-dev clean run

export PYTHONPATH := $(CURDIR):$(PYTHONPATH)
export DJANGO_SETTINGS_MODULE := content_management_service.settings.development

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

test.%:
	$(eval export DJANGO_SETTINGS_MODULE=content_management_service.settings.test)
	$(eval PARTS := $(subst ., ,$*))
	$(eval APP := $(word 1,$(PARTS)))
	$(eval CLASS := $(word 2,$(PARTS)))
	$(eval METHOD := $(word 3,$(PARTS)))

	@if [ -n "$(APP)" ]; then \
		if [ -n "$(CLASS)" ]; then \
			if [ -n "$(METHOD)" ]; then \
				echo "Running test: apps.$(APP).tests.test_views.$(CLASS).$(METHOD)"; \
				coverage run manage.py test apps.$(APP).tests.test_views.$(CLASS).$(METHOD); \
			else \
				echo "Running tests in class: apps.$(APP).tests.test_views.$(CLASS)"; \
				coverage run manage.py test apps.$(APP).tests.test_views.$(CLASS); \
			fi; \
		else \
			echo "Running tests in app: apps.$(APP).tests"; \
			coverage run manage.py test apps.$(APP).tests; \
		fi; \
	fi

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

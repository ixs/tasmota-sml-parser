BRANCH := $(shell git branch --show-current)
PYTHON_VERSION := $(shell python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)

check-python:
	@echo "Current Python version: $(PYTHON_VERSION)"
	@if [ "$(PYTHON_VERSION)" != "3.9" ] && [ "$(BRANCH)" = "master" ]; then \
		echo "Warning: Master branch only supports Python 3.9. Current version: $(PYTHON_VERSION)"; \
		echo "For Python 3.10+ support, checkout branch: 10-update-to-python-313"; \
	fi

venv: check-python
	pyenv exec python3 -mvenv venv
	./venv/bin/pip install -r requirements.txt

# Test targets
test-deps: check-python
	pip install -r requirements-test.txt

test: test-deps
	python run_tests.py --all

test-unit: test-deps
	python run_tests.py --unit

test-integration: test-deps
	python run_tests.py --integration

test-functional: test-deps
	python run_tests.py --functional

test-performance: test-deps
	python run_tests.py --performance

test-coverage: test-deps
	python run_tests.py --coverage --html-report

test-lint: test-deps
	python run_tests.py --lint

test-quick:
	python -m unittest discover -s tests -v

# Development targets
install-dev: venv test-deps

clean-test:
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Deployment targets
dev-deploy:
	git push azure-dev $(BRANCH):master

prod-deploy:
	git push azure-prod $(BRANCH):master

.PHONY: venv check-python test test-deps test-unit test-integration test-functional test-performance test-coverage test-lint test-quick install-dev clean-test dev-deploy prod-deploy

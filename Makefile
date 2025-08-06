BRANCH := $(shell git branch --show-current)

venv:
	rm -rf venv
	pyenv exec python -mvenv venv
	./venv/bin/pip install -r requirements.txt

# Test targets
test-deps:
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

.PHONY: venv test test-deps test-unit test-integration test-functional test-performance test-coverage test-lint test-quick install-dev clean-test dev-deploy prod-deploy

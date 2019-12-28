.PHONY: test test-coverage flake8

WORK_DIR=./schemadiff

test:
	pytest

test-coverage:
	pytest --cov $(WORK_DIR)

test-coverage-html:
	pytest --cov $(WORK_DIR) --cov-report html

flake8:
	flake8 --count --exit-zero $(WORK_DIR) --output-file flake8_issues.txt

clean:
	find . -name "*.py[co]" -o -name __pycache__ -exec rm -rf {} +
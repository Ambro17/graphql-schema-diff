.PHONY: test test-coverage test-coverage-html flake8 clean docs

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

docs:
	pdoc3 schemadiff/ --html -o docs --force  && \
	# Remove nested dir as github pages expects an index.html on docs folder \
	cp -r docs/schemadiff/* docs && rm -rf docs/schemadiff && echo "📚 Docs updated successfully ✨"

publish:
    pip install --upgrade setuptools wheel && \
    python3 setup.py sdist bdist_wheel && \
    python3 -m pip install --upgrade twine && \
    python3 -m twine upload dist/*


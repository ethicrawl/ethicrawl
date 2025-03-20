.PHONY: test test-fast lint check-types check-docs

test:
	coverage run -m pytest
	coverage report > coverage.txt
	coverage html

test-fast:
	coverage run -m pytest -x -v

lint:
	pylint ethicrawl

check-types:
	mypy ethicrawl

check-docs:
	interrogate -v ethicrawl

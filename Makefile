.PHONY: test test-fast

test:
	coverage run -m pytest
	coverage report > coverage.txt
	coverage html

test-fast:
	coverage run -m pytest -x -v
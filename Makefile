<<<<<<< HEAD
.PHONY: test test-fast lint check-types check-docs
=======
.PHONY: test test-fast
>>>>>>> main

test:
	coverage run -m pytest
	coverage report > coverage.txt
	coverage html

test-fast:
<<<<<<< HEAD
	coverage run -m pytest -x -v

lint:
	pylint ethicrawl

check-types:
	mypy ethicrawl

check-docs:
	interrogate -v ethicrawl
=======
	coverage run -m pytest -x -v
>>>>>>> main

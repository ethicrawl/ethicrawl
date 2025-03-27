.PHONY: build release docs clean test coverage information lint security test docker-build docker-build-all docker-audit docker-bandit docker-semgrep docker-test docker-black docker-pyright docker-mypy docker-docs-build docker-docs-serve build-check publish-test publish verify-testpypi

docker-test: docker-build-all
	@echo "\n🧪 Running tests..."
	@echo "==================="
	@docker run --rm -v $(PWD):/app ethicrawl:coverage

docker-build-base:
	@echo "Building base image..."
	@docker build -q -t ethicrawl-base -f docker/Dockerfile.base . > /dev/null

docker-build-all: docker-build-base
	@echo "Building tool images..."
	@docker build -q -t ethicrawl:audit -f docker/Dockerfile.audit . > /dev/null
	@docker build -q -t ethicrawl:bandit -f docker/Dockerfile.bandit . > /dev/null
	@docker build -q -t ethicrawl:black -f docker/Dockerfile.black . > /dev/null
	@docker build -q -t ethicrawl:coverage -f docker/Dockerfile.coverage . > /dev/null
	@docker build -q -t ethicrawl:mkdocs -f docker/Dockerfile.mkdocs . > /dev/null
	@docker build -q -t ethicrawl:mypy -f docker/Dockerfile.mypy . > /dev/null
	@docker build -q -t ethicrawl:publish -f docker/Dockerfile.publish . > /dev/null
	@docker build -q -t ethicrawl:pyright -f docker/Dockerfile.pyright . > /dev/null
	@docker build -q -t ethicrawl:semgrep -f docker/Dockerfile.semgrep . > /dev/null
	@echo "✅ All images built successfully"

docker-audit: docker-build-all
	@echo "\n\n📦 Running dependency audit with pip-audit..."
	@echo "==============================================="
	@docker run --rm ethicrawl:audit

docker-bandit: docker-build-all
	@echo "\n\n🔍 Running code security scan with bandit..."
	@echo "============================================="
	@docker run --rm -v $(PWD):/app ethicrawl:bandit

docker-semgrep: docker-build-all
	@echo "\n\n🔎 Running pattern matching with semgrep..."
	@echo "============================================"
	@docker run --rm -v $(PWD):/app ethicrawl:semgrep

docker-black: docker-build-all
	@echo "\n🔠 Checking code formatting with black..."
	@echo "========================================"
	@docker run --rm -v $(PWD):/app ethicrawl:black

docker-pyright: docker-build-all
	@echo "\n📝 Checking types with pyright..."
	@echo "==============================="
	docker run --rm -v $(PWD):/app ethicrawl:pyright

docker-mypy: docker-build-all
	@echo "\n📝 Checking types with mypy..."
	@echo "============================="
	@docker run --rm \
		--user $(shell id -u):$(shell id -g) \
		-v $(PWD):/app ethicrawl:mypy

docker-docs-build: docker-build-all
	@echo "\n📚 Building documentation..."
	@echo "=========================="
	@mkdir -p site
	@docker run --rm \
		--user $(shell id -u):$(shell id -g) \
		-v $(PWD)/docs:/app/docs \
		-v $(PWD)/ethicrawl:/app/ethicrawl \
		-v $(PWD)/site:/app/site \
		-v $(PWD)/mkdocs.yml:/app/mkdocs.yml \
		-v $(PWD)/README.md:/app/README.md \
		ethicrawl:mkdocs build

docker-docs-serve: docker-build-all
	@echo "\n📚 Serving documentation at http://localhost:8000"
	@echo "==========================================="
	@docker run --rm -p 8000:8000 \
				-v $(PWD)/docs:/app/docs \
		-v $(PWD)/ethicrawl:/app/ethicrawl \
		-v $(PWD)/mkdocs.yml:/app/mkdocs.yml \
		-v $(PWD)/README.md:/app/README.md \
		ethicrawl:mkdocs

build: docker-build-all clean
	@echo "\n📦 Building distribution packages..."
	@echo "================================="
	@mkdir -p dist
	@docker run --user $(shell id -u):$(shell id -g) \
			--rm -v $(PWD):/app --entrypoint python ethicrawl:publish -m build
	@echo "\n✅ Distribution packages built in dist/ directory"

build-check: build
	@echo "\n🔍 Checking distribution packages..."
	@echo "=================================="
	@docker run --rm -v $(PWD):/app --entrypoint check-wheel-contents ethicrawl:publish dist/*.whl
	@docker run --rm -v $(PWD):/app --entrypoint twine ethicrawl:publish check dist/*
	@echo "\n✅ Distribution packages verified"

publish-test: build-check
	@echo "\n🚀 Publishing to TestPyPI..."
	@echo "=========================="
	@if [ -n "$(PYPI_TEST_TOKEN)" ]; then \
		echo "Using provided TestPyPI token"; \
		docker run --rm \
			-v $(PWD):/app \
			-e TWINE_USERNAME=__token__ \
			-e TWINE_PASSWORD=$(PYPI_TEST_TOKEN) \
			--entrypoint twine \
			ethicrawl:publish upload --repository testpypi dist/*; \
	else \
		echo "No token provided, using interactive mode"; \
		docker run --rm -it \
			-v $(PWD):/app \
			--entrypoint twine \
			ethicrawl:publish upload --repository testpypi dist/*; \
	fi
	@echo "\n✅ Published to TestPyPI: https://test.pypi.org/project/ethicrawl/"
	@$(MAKE) verify-testpypi

verify-testpypi:
	@echo "\n🔍 Verifying package on TestPyPI..."
	@echo "================================"
	@version=$$(grep "^version =" pyproject.toml | sed -E 's/version = "([^"]+)"/\1/'); \
	echo "Checking for ethicrawl v$$version on TestPyPI..."; \
	sleep 5; \
	if curl -s https://test.pypi.org/pypi/ethicrawl/$$version/json > /dev/null; then \
		echo "✅ Package ethicrawl v$$version found on TestPyPI!"; \
		echo "   View at: https://test.pypi.org/project/ethicrawl/$$version/"; \
	else \
		echo "❌ Package ethicrawl v$$version not found on TestPyPI"; \
		echo "   This could be due to processing delay. Check manually at:"; \
		echo "   https://test.pypi.org/project/ethicrawl/"; \
		exit 1; \
	fi

publish: build-check
	@echo "\n🚀 Publishing to PyPI..."
	@echo "======================"
	@if [ -n "$(PYPI_TOKEN)" ]; then \
		echo "Using provided PyPI token"; \
		docker run --rm \
			-v $(PWD):/app \
			-e TWINE_USERNAME=__token__ \
			-e TWINE_PASSWORD=$(PYPI_TOKEN) \
			--entrypoint twine \
			ethicrawl:publish upload dist/*; \
	else \
		echo "No token provided, using interactive mode"; \
		docker run --rm -it \
			-v $(PWD):/app \
			--entrypoint twine \
			ethicrawl:publish upload dist/*; \
	fi
	@echo "\n✅ Published to PyPI: https://pypi.org/project/ethicrawl/"

coverage: docker-build-all
	@echo "\n📊 Running tests with coverage..."
	@echo "==============================="
	@mkdir -p reports/htmlcov
	@docker run --rm \
		--user $(shell id -u):$(shell id -g) \
		-v $(PWD):/app \
		ethicrawl:coverage && \
	docker run --rm \
		-v $(PWD):/app \
		--user $(shell id -u):$(shell id -g) \
		--entrypoint coverage \
		ethicrawl:coverage report -m > reports/coverage.txt && \
	docker run --rm \
		-v $(PWD):/app \
		--user $(shell id -u):$(shell id -g) \
		--entrypoint coverage \
		ethicrawl:coverage html --directory=reports/htmlcov && \
	echo "\n✅ Coverage report generated in reports/htmlcov/ directory" || \
	(echo "\n❌ Coverage generation failed" && exit 1)

information:
	@echo "📊 Code Quality Information Summary 📊"
	@echo "===================================="
	@echo "\n🔍 Pylint Score:"
	@pylint --exit-zero -r n --score=y ethicrawl | grep "Your code has been rated" || echo "Pylint failed to run"

	@echo "\n📝 Documentation Coverage:"
	@interrogate -s ethicrawl > /tmp/interrogate_output.txt 2>&1; \
	INTERROGATE_EXIT=$$?; \
	if [ $$INTERROGATE_EXIT -ne 0 ]; then \
		FAIL_MSG=$$(grep "RESULT: FAILED" /tmp/interrogate_output.txt); \
		cat /tmp/interrogate_output.txt | grep -A 2 "SUMMARY"; \
		echo "❌ Documentation coverage requirement not met: $$FAIL_MSG"; \
	elif [ $$INTERROGATE_EXIT -eq 127 ]; then \
		echo "❌ Interrogate command not found"; \
	else \
		cat /tmp/interrogate_output.txt | grep -A 2 "SUMMARY"; \
	fi; \
	rm -f /tmp/interrogate_output.txt

	@echo "\n🔢 Line Counts:"
	@find ethicrawl -name "*.py" -type f -exec wc -l {} \; | sort -nr | head -n 10
	@echo "  (showing top 10 files by line count)"

	@echo "\n📦 Package Information:"
	@grep "^version =" pyproject.toml || echo "Version not found"
	@echo "Python support: $(shell grep "requires-python" pyproject.toml | cut -d'"' -f2)"

	@echo "\n✅ Information gathering complete"

lint:
	@echo "🧹 RUNNING LINTING CHECKS 🧹"
	@echo "==========================="
	@make -s docker-black; BLACK_STATUS=$$?; \
	make -s docker-pyright; PYRIGHT_STATUS=$$?; \
	make -s docker-mypy; MYPY_STATUS=$$?; \
	if [ $$BLACK_STATUS -eq 0 ] && [ $$PYRIGHT_STATUS -eq 0 ] && [ $$MYPY_STATUS -eq 0 ]; then \
		echo "\n✅ All linting checks passed!"; \
	else \
		echo "\n❌ Linting checks failed!"; \
		[ $$BLACK_STATUS -ne 0 ] && echo "  - Black code formatting failed"; \
		[ $$PYRIGHT_STATUS -ne 0 ] && echo "  - Pyright type checking failed"; \
		[ $$MYPY_STATUS -ne 0 ] && echo "  - Mypy type checking failed"; \
		exit 1; \
	fi

security:
	@echo "🛡️  RUNNING SECURITY CHECKS 🛡️"
	@echo "============================="
	@make -s docker-audit; AUDIT_STATUS=$$?; \
	make -s docker-bandit; BANDIT_STATUS=$$?; \
	make -s docker-semgrep; SEMGREP_STATUS=$$?; \
	if [ $$AUDIT_STATUS -eq 0 ] && [ $$BANDIT_STATUS -eq 0 ] && [ $$SEMGREP_STATUS -eq 0 ]; then \
		echo "\n✅ All security checks passed!"; \
	else \
		echo "\n❌ Security checks failed!"; \
		[ $$AUDIT_STATUS -ne 0 ] && echo "  - Dependency audit failed"; \
		[ $$BANDIT_STATUS -ne 0 ] && echo "  - Bandit code scan failed"; \
		[ $$SEMGREP_STATUS -ne 0 ] && echo "  - Semgrep pattern matching failed"; \
		exit 1; \
	fi

test: coverage lint security

clean:
	@echo "🧹 Cleaning up generated files..."
	@echo "==============================="
	@# Remove coverage reports
	@rm -rf reports/htmlcov
	@rm -f reports/coverage.txt
	@rm -f .coverage
	@rm -f .coverage.*

	@# Remove Python bytecode files
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete

	@# Remove distribution artifacts
	@rm -rf dist/
	@rm -rf build/
	@rm -rf *.egg-info/
	@rm -rf *.egg/

	@# Remove generated documentation
	@rm -rf site/

	@# Remove test and type checking caches
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@rm -rf .tox/

	@# Remove temporary files
	@find . -type f -name ".DS_Store" -delete
	@find . -type f -name "*.swp" -delete
	@find . -type f -name "*.swo" -delete

	@echo "\n✅ Clean up complete"

docs: docker-docs-build

release: test
	@echo "\n🎉 Creating a new release..."
	@echo "=========================="
	@if [ -n "$(VERSION)" ]; then \
		sed -i "s/^version = \"[^\"]*\"/version = \"$(VERSION)\"/" pyproject.toml; \
		echo "✅ Version set to $(VERSION)"; \
	else \
		echo "⚠️  No VERSION specified, using existing version"; \
	fi
	@version=$$(grep "^version =" pyproject.toml | sed -E 's/version = "([^"]+)"/\1/'); \
	echo "🔶 Preparing release for version $$version"; \
	git add pyproject.toml; \
	git commit -m "Release v$$version"; \
	git tag -a "v$$version" -m "Release v$$version"; \
	git push origin main; \
	git push origin "v$$version"; \
	echo "✅ Git tag v$$version created and pushed"; \
	make publish
	@echo "\n🎉 Release process completed!"
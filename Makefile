.PHONY: docs clean test coverage information lint security test docker-build docker-build-all docker-audit docker-bandit docker-semgrep docker-test docker-black docker-pyright docker-mypy docker-docs-build docker-docs-serve

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
	@docker run --rm -v $(PWD):/app ethicrawl:mypy

docker-docs-build: docker-build-all
	@echo "\n📚 Building documentation..."
	@echo "=========================="
	@mkdir -p site
	@docker run --rm \
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
coverage: docker-build-all
	@echo "\n📊 Running tests with coverage..."
	@echo "==============================="
	@mkdir -p reports/htmlcov
	@docker run --rm \
		-v $(PWD):/app \
		ethicrawl:coverage && \
	docker run --rm \
		-v $(PWD):/app \
		--entrypoint coverage \
		ethicrawl:coverage report -m > reports/coverage.txt && \
	docker run --rm \
		-v $(PWD):/app \
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
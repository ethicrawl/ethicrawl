.PHONY: clean docker docs info test \
		coverage lint security \
		docker-build-base docker-build-tools docker-clean docker-validate docker-if-needed

DOCKER_TOOLS = audit bandit black coverage mkdocs mypy publish pyright semgrep

clean: docker-clean
docker: docker-build-base docker-build-tools
test: coverage lint security

# tests
coverage: docker-if-needed
	@echo "\n📊 Running tests with coverage..."
	@echo "==============================="
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
	docker run --rm \
		-v $(PWD):/app \
		--entrypoint bash \
		ethicrawl:coverage -c "\
		chown -R $(shell id -u):$(shell id -g) reports && \
		chown $(shell id -u):$(shell id -g) .coverage" && \
	echo "\n✅ Coverage report generated in reports/htmlcov/ directory" || \
	(echo "\n❌ Coverage generation failed" && exit 1)

lint: docker-if-needed
	@echo "\n🧹 Running linting checks... 🧹"
	@echo "==========================="
	@echo "\n📝 Running black formatter check..."
	@docker run --rm -v $(PWD):/app ethicrawl:black && \
	echo "✅ Black checks passed" || (echo "❌ Black checks failed" && exit 1)

	@echo "\n🔍 Running mypy type checking..."
	@docker run --rm -v $(PWD):/app ethicrawl:mypy && \
	echo "✅ Type checking passed" || (echo "❌ Type checking failed" && exit 1)

	@echo "\n🔎 Running pyright analysis..."
	@docker run --rm -v $(PWD):/app ethicrawl:pyright && \
	echo "✅ Pyright checks passed" || (echo "❌ Pyright checks failed" && exit 1)

	@echo "\n✅ All linting checks passed"

security: docker-if-needed
	@echo "\n🛡️  Running security checks... 🛡️"
	@echo "============================="
	@echo "\n🔒 Running pip-audit vulnerability scan..."
	@docker run --rm -v $(PWD):/app ethicrawl:audit && \
	echo "✅ No vulnerabilities found" || (echo "⚠️  Vulnerabilities detected" && exit 1)

	@echo "\n🔍 Running bandit security scan..."
	@docker run --rm -v $(PWD):/app --entrypoint bash ethicrawl:bandit -c "\
		bandit -r /app/ethicrawl -q -ll || exit 1; \
		echo 'Summary: No security issues found'" && \
	echo "✅ Bandit scan passed" || (echo "❌ Security issues found" && exit 1)


	@echo "\n🔎 Running semgrep pattern analysis..."
	@docker run --rm -v $(PWD):/app --entrypoint bash ethicrawl:semgrep -c "\
		cd /app && semgrep --config=auto --quiet ethicrawl && \
		echo 'Summary: No semgrep issues found'" && \
	echo "✅ Semgrep checks passed" || (echo "❌ Semgrep found issues" && exit 1)

	@echo "\n✅ All security checks passed"

# documentation
docs: docker-if-needed
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

docs-dev: docker-if-needed
	@echo "\n📚 Serving documentation at http://localhost:8000"
	@echo "==========================================="
	@docker run --rm -p 8000:8000 \
				-v $(PWD)/docs:/app/docs \
		-v $(PWD)/ethicrawl:/app/ethicrawl \
		-v $(PWD)/mkdocs.yml:/app/mkdocs.yml \
		-v $(PWD)/README.md:/app/README.md \
		ethicrawl:mkdocs

# addtional details for information only
info:
	@echo "\n📦 Package Information:"
	@grep "^version =" pyproject.toml || echo "Version not found"
	@echo "Python support: $(shell grep "requires-python" pyproject.toml | cut -d'"' -f2)"

# Build and manage docker images
docker-build-base:
	@echo "Building base image..."
	@docker build -q -t ethicrawl-base -f docker/Dockerfile.base . > /dev/null

docker-build-tools: docker-build-base
	@echo "Building tool images..."
	@for tool in $(DOCKER_TOOLS); do \
		echo "  Building ethicrawl:$$tool..."; \
		docker build -q -t ethicrawl:$$tool -f docker/Dockerfile.$$tool . > /dev/null; \
	done
	@echo "✅ All images built successfully"

docker-clean:
	@echo "Cleaning Docker images..."
	@removed=0; \
	for tool in $(DOCKER_TOOLS); do \
		if [ -n "$$(docker images -q ethicrawl:$$tool 2>/dev/null)" ]; then \
			echo "  Removing ethicrawl:$$tool"; \
			docker rmi ethicrawl:$$tool > /dev/null 2>&1 && removed=$$((removed+1)) || echo "	⚠️ Failed to remove ethicrawl:$$tool"; \
		fi; \
	done; \
	if [ -n "$$(docker images -q ethicrawl-base 2>/dev/null)" ]; then \
		echo "  Removing ethicrawl-base"; \
		docker rmi ethicrawl-base > /dev/null 2>&1 && removed=$$((removed+1)) || echo "	⚠️ Failed to remove ethicrawl-base"; \
	fi; \
	if [ $$removed -gt 0 ]; then \
		echo "✅ Removed $$removed Docker images"; \
	else \
		echo "✅ No Docker images to remove"; \
	fi

docker-validate:
	@echo "Validating Docker images..."
	@missing_images=0; \
	if [ -z "$$(docker images -q ethicrawl-base 2>/dev/null)" ]; then \
		echo "❌ Missing Docker image: ethicrawl-base"; \
		missing_images=1; \
	fi; \
	for tool in $(DOCKER_TOOLS); do \
		if [ -z "$$(docker images -q ethicrawl:$$tool 2>/dev/null)" ]; then \
			echo "❌ Missing Docker image: ethicrawl:$$tool"; \
			missing_images=1; \
		fi; \
	done; \
	if [ $$missing_images -eq 0 ]; then \
		echo "✅ All required Docker images exist"; \
	else \
		echo "❌ Some Docker images are missing. Run 'make docker' to build them."; \
		exit 1; \
	fi

docker-if-needed:
	@if ! make -s docker-validate >/dev/null 2>&1; then \
		make docker; \
	else \
		echo "✅ Using existing Docker images"; \
	fi
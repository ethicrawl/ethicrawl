.PHONY: test coverage information lint security test docker-build docker-build-all docker-audit docker-bandit docker-semgrep docker-test docker-black docker-pyright docker-mypy

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

# make test
# Building base image...
# Building tool images...
# ✅ All images built successfully

# 📊 Running tests with coverage...
# ===============================
# ============================= test session starts ==============================
# platform linux -- Python 3.10.16, pytest-8.3.5, pluggy-1.5.0
# rootdir: /app
# configfile: pyproject.toml
# plugins: cov-6.0.0
# collected 166 items

# tests/code_cover/client/http/test_chrome_transport.py ............       [  7%]
# tests/code_cover/client/http/test_http_client.py .....                   [ 10%]
# tests/code_cover/client/http/test_http_request.py ...                    [ 12%]
# tests/code_cover/client/http/test_http_response.py ...                   [ 13%]
# tests/code_cover/client/http/test_requests_transport.py ...              [ 15%]
# tests/code_cover/client/test_client.py .                                 [ 16%]
# tests/code_cover/client/test_transport.py .                              [ 16%]
# tests/code_cover/config/test_base_config.py .                            [ 17%]
# tests/code_cover/config/test_config.py ......                            [ 21%]
# tests/code_cover/config/test_http_config.py .......                      [ 25%]
# tests/code_cover/config/test_http_proxy_config.py ....                   [ 27%]
# tests/code_cover/config/test_logger_config.py .....                      [ 30%]
# tests/code_cover/config/test_sitemap_config.py .                         [ 31%]
# tests/code_cover/context/test_context.py ........                        [ 36%]
# tests/code_cover/core/test_headers.py ......                             [ 39%]
# tests/code_cover/core/test_resource.py ......                            [ 43%]
# tests/code_cover/core/test_resource_list.py .........                    [ 48%]
# tests/code_cover/core/test_url.py ..................                     [ 59%]
# tests/code_cover/logger/test_formatter.py ....                           [ 62%]
# tests/code_cover/logger/test_logger.py ..                                [ 63%]
# tests/code_cover/robots/test_robot.py .............                      [ 71%]
# tests/code_cover/robots/test_robot_factory.py ..                         [ 72%]
# tests/code_cover/sitemaps/test_index_entry.py .                          [ 72%]
# tests/code_cover/sitemaps/test_sitemap_entry.py .                        [ 73%]
# tests/code_cover/sitemaps/test_sitemap_nodes.py ...............          [ 82%]
# tests/code_cover/sitemaps/test_sitemap_parser.py ...........             [ 89%]
# tests/code_cover/sitemaps/test_urlset_entry.py .....                     [ 92%]
# tests/code_cover/test_ethicrawl.py .............                         [100%]

# ============================= 166 passed in 15.09s =============================
# Wrote HTML report to reports/htmlcov/index.html

# ✅ Coverage report generated in reports/htmlcov/ directory
# 🧹 RUNNING LINTING CHECKS 🧹
# ===========================
# Building base image...
# Building tool images...
# ✅ All images built successfully

# 🔠 Checking code formatting with black...
# ========================================
# All done! ✨ 🍰 ✨
# 50 files would be left unchanged.
# Building base image...
# Building tool images...
# ✅ All images built successfully

# 📝 Checking types with pyright...
# ===============================
# 0 errors, 0 warnings, 0 informations
# Building base image...
# Building tool images...
# ✅ All images built successfully

# 📝 Checking types with mypy...
# =============================
# Success: no issues found in 50 source files

# ✅ All linting checks passed!
# 🛡️  RUNNING SECURITY CHECKS 🛡️
# =============================
# Building base image...
# Building tool images...
# ✅ All images built successfully


# 📦 Running dependency audit with pip-audit...
# ===============================================
# No known vulnerabilities found
# Building base image...
# Building tool images...
# ✅ All images built successfully


# 🔍 Running code security scan with bandit...
# =============================================
# [main]  INFO    profile include tests: None
# [main]  INFO    profile exclude tests: None
# [main]  INFO    cli include tests: None
# [main]  INFO    cli exclude tests: None
# [main]  INFO    running on Python 3.10.16
# Run started:2025-03-27 10:24:18.526427

# Test results:
#         No issues identified.

# Code scanned:
#         Total lines of code: 3931
#         Total lines skipped (#nosec): 1
#         Total potential issues skipped due to specifically being disabled (e.g., #nosec BXXX): 0

# Run metrics:
#         Total issues (by severity):
#                 Undefined: 0
#                 Low: 0
#                 Medium: 0
#                 High: 0
#         Total issues (by confidence):
#                 Undefined: 0
#                 Low: 0
#                 Medium: 0
#                 High: 0
# Files skipped (0):
# Building base image...
# Building tool images...
# ✅ All images built successfully


# 🔎 Running pattern matching with semgrep...
# ============================================
# METRICS: Using configs from the Registry (like --config=p/ci) reports pseudonymous rule metrics to semgrep.dev.
# To disable Registry rule metrics, use "--metrics=off".
# Using configs only from local files (like --config=xyz.yml) does not enable metrics.

# More information: https://semgrep.dev/docs/metrics



# ┌─────────────┐
# │ Scan Status │
# └─────────────┘
#   Scanning 162 files tracked by git with 1060 Code rules:

#   Language      Rules   Files          Origin      Rules
#  ─────────────────────────────        ───────────────────
#   <multilang>      48     162          Community    1060
#   python          242      50



# ┌──────────────┐
# │ Scan Summary │
# └──────────────┘
# ✅ Scan completed successfully.
#  • Findings: 0 (0 blocking)
#  • Rules run: 290
#  • Targets scanned: 162
#  • Parsed lines: ~100.0%
#  • No ignore information available
# Ran 290 rules on 162 files: 0 findings.
# (need more rules? `semgrep login` for additional free Semgrep Registry rules)

# If Semgrep missed a finding, please send us feedback to let us know!
# See https://semgrep.dev/docs/reporting-false-negatives/

# ✅ All security checks passed!
.PHONY: test test-units lint compliance clean install help

# Default to help
help:
	@echo "BlackBox Testing Monorepo"
	@echo ""
	@echo "Targets:"
	@echo "  make install      - Install dependencies for all adapters"
	@echo "  make test         - Run demo tests for all adapters (expecting failures)"
	@echo "  make test-units   - Run unit tests for all adapters (must pass)"
	@echo "  make lint         - Run lint gates (ruff/black, eslint, shellcheck)"
	@echo "  make compliance   - Run the full compliance suite (includes unit tests)"
	@echo "  make clean        - Remove build artifacts and bundles"

install:
	@echo "Installing Tools dependencies..."
	python3 -m pip install -r tools/requirements.txt
	@echo "Installing Python dependencies..."
	cd adapters/python-pytest && python3 -m pip install -e .
	@echo "Installing Node dependencies..."
	cd adapters/node-playwright && npm install
	@echo "Installing Java dependencies (Verify Maven)..."
	mvn -v >/dev/null 2>&1 || echo "WARNING: Maven not found on path"

test:
	@echo "Running Python Adapter Tests..."
	cd adapters/python-pytest && python3 -m pytest || true
	@echo "Running Node Adapter Tests..."
	cd adapters/node-playwright && npm test || true
	@echo "Running Java Adapter Tests..."
	cd adapters/java-junit5 && mvn test -Dtest=SampleFailingTest -DfailIfNoTests=false || true

test-units:
	@echo "Running Validator Unit Tests..."
	cd spec/compliance && python3 -m pytest tests/ -v
	@echo "Running Python Adapter Unit Tests..."
	cd adapters/python-pytest && python3 -m pytest tests/test_plugin_units.py -v
	@echo "Running Java Adapter Unit Tests..."
	cd adapters/java-junit5 && mvn test
	@echo "Running Node Adapter Unit Tests..."
	cd adapters/node-playwright && npm run test:unit

lint:
	@echo "Running Lint Gates..."
	./tools/scripts/run_lint.sh

compliance:
	@echo "Running Compliance Suite..."
	./tools/scripts/run_compliance.sh

clean:
	rm -rf blackbox-reports
	find . -name "blackbox-reports" -type d -exec rm -rf {} +
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name ".pytest_cache" -type d -exec rm -rf {} +
	find . -name "node_modules" -type d -exec rm -rf {} +

.PHONY: test compliance clean install help

# Default to help
help:
	@echo "BlackBox Testing Monorepo"
	@echo ""
	@echo "Targets:"
	@echo "  make install      - Install dependencies for all adapters"
	@echo "  make test         - Run tests for all adapters (expecting failures)"
	@echo "  make compliance   - Run the compliance suite"
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
	cd adapters/java-junit5 && mvn test || true

compliance:
	@echo "Running Compliance Suite..."
	./tools/scripts/run_compliance.sh

clean:
	rm -rf blackbox-reports
	find . -name "blackbox-reports" -type d -exec rm -rf {} +
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name ".pytest_cache" -type d -exec rm -rf {} +
	find . -name "node_modules" -type d -exec rm -rf {} +

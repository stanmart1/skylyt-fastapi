.PHONY: test test-unit test-integration test-performance test-coverage install-deps clean

# Install dependencies
install-deps:
	pip install -r requirements.txt

# Run all tests
test:
	python run_tests.py all

# Run unit tests only
test-unit:
	python run_tests.py unit

# Run integration tests only
test-integration:
	python run_tests.py integration

# Run performance tests only
test-performance:
	python run_tests.py performance

# Run tests with coverage report
test-coverage:
	python run_tests.py coverage

# Run specific test file
test-file:
	pytest $(FILE) -v

# Run tests with specific marker
test-marker:
	pytest -m $(MARKER) -v

# Clean test artifacts
clean:
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Setup test database
setup-test-db:
	python -c "from tests.conftest import engine, Base; Base.metadata.create_all(bind=engine)"

# Lint code
lint:
	flake8 app/ tests/
	black --check app/ tests/

# Format code
format:
	black app/ tests/
	isort app/ tests/

# Run security checks
security:
	bandit -r app/

# Generate test report
report:
	pytest tests/ --cov=app --cov-report=html --cov-report=xml --junitxml=test-results.xml

# Database optimization
optimize-db:
	python scripts/optimize_database_performance.py

# Fix database timeouts
fix-timeouts:
	python fix_database_timeouts.py

# Run all performance fixes
run-all-fixes:
	python run_performance_fixes.py

# Performance monitoring
monitor:
	python scripts/performance_monitor.py

# Check performance metrics
performance-check:
	curl -s http://localhost:8000/api/v1/performance/summary | python -m json.tool

# Reset database connection pool
reset-pool:
	curl -X POST http://localhost:8000/api/v1/performance/reset-pool

# Health check
health-check:
	curl -s http://localhost:8000/api/v1/health | python -m json.tool

# Test database connection
test-db:
	python test_database_connection.py

# Run database migrations
migrate:
	alembic upgrade head

# Create new migration
migration:
	alembic revision --autogenerate -m "$(MESSAGE)"

# Validate implementation
validate:
	python3 scripts/validate_implementation.py

# Help
help:
	@echo "Available commands:"
	@echo "  install-deps     - Install Python dependencies"
	@echo "  test            - Run all tests"
	@echo "  test-unit       - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-performance - Run performance tests only"
	@echo "  test-coverage   - Run tests with coverage report"
	@echo "  test-file FILE=path - Run specific test file"
	@echo "  test-marker MARKER=name - Run tests with specific marker"
	@echo "  clean           - Clean test artifacts"
	@echo "  setup-test-db   - Setup test database"
	@echo "  lint            - Run code linting"
	@echo "  format          - Format code"
	@echo "  security        - Run security checks"
	@echo "  report          - Generate comprehensive test report"
	@echo "  optimize-db     - Optimize database performance"
	@echo "  fix-timeouts    - Fix database timeout issues"
	@echo "  run-all-fixes   - Run all performance fixes"
	@echo "  monitor         - Run performance monitoring"
	@echo "  performance-check - Check performance metrics"
	@echo "  reset-pool      - Reset database connection pool"
	@echo "  health-check    - Check application health"
	@echo "  test-db         - Test database connection"
	@echo "  migrate         - Run database migrations"
	@echo "  migration MESSAGE=name - Create new migration"
	@echo "  validate        - Validate complete implementation"
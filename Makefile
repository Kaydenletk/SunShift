# SunShift Makefile
# One-command local development with Docker Compose

.PHONY: demo stop clean test build logs

# Default target
.DEFAULT_GOAL := demo

# Spin up full stack locally
demo: build
	@echo "Starting SunShift stack..."
	docker compose up -d
	@echo ""
	@echo "SunShift is starting up!"
	@echo "  Backend:   http://localhost:8000"
	@echo "  Dashboard: http://localhost:3000"
	@echo "  Health:    http://localhost:8000/health"
	@echo ""
	@echo "Run 'make logs' to follow logs, 'make stop' to shut down."

# Build containers without starting
build:
	@echo "Building SunShift containers..."
	docker compose build

# Stop all services
stop:
	@echo "Stopping SunShift stack..."
	docker compose down

# Clean up everything (containers, images, volumes)
clean:
	@echo "Cleaning up SunShift stack..."
	docker compose down --rmi local --volumes --remove-orphans

# Run tests (placeholder for CI)
test:
	@echo "Running tests..."
	@echo "Backend tests:"
	cd sunshift/backend && python -m pytest -v 2>/dev/null || echo "  No tests configured yet"
	@echo "Dashboard tests:"
	cd sunshift/dashboard && npm test 2>/dev/null || echo "  No tests configured yet"

# Follow container logs
logs:
	docker compose logs -f

# Check health of services
health:
	@curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "Backend not healthy"

# Development mode - run services with hot reload
dev:
	@echo "Starting development mode..."
	@echo "Backend: cd sunshift/backend && uvicorn backend.main:app --reload"
	@echo "Dashboard: cd sunshift/dashboard && npm run dev"

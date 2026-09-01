.PHONY: setup dev clean

# Paths
BACKEND_DIR := backend
ML_DIR := ml-engine
VENV := $(ML_DIR)/venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn

# PID files for clean shutdown
BACKEND_PID := .backend.pid
ML_PID := .ml.pid

## setup: Create Python venv, install requirements, and tidy Go modules
setup:
	@echo "==> Setting up Python virtual environment..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r $(ML_DIR)/requirements.txt
	@echo "==> Tidying Go modules..."
	cd $(BACKEND_DIR) && go mod tidy
	@echo "==> Setup complete."

## dev: Run Go backend and Python ML engine concurrently
dev:
	@echo "==> Starting ML engine on :8000..."
	cd $(ML_DIR) && ../$(UVICORN) main:app --reload --port 8000 & echo $$! > ../$(ML_PID)
	@echo "==> Starting Go backend on :3000..."
	cd $(BACKEND_DIR) && go run main.go & echo $$! > ../$(BACKEND_PID)
	@echo "==> Services running. Press Ctrl+C or run 'make clean' to stop."
	@wait

## clean: Kill background processes started by 'make dev'
clean:
	@if [ -f $(BACKEND_PID) ]; then \
		echo "==> Stopping Go backend (PID $$(cat $(BACKEND_PID)))..."; \
		kill $$(cat $(BACKEND_PID)) 2>/dev/null || true; \
		rm -f $(BACKEND_PID); \
	fi
	@if [ -f $(ML_PID) ]; then \
		echo "==> Stopping ML engine (PID $$(cat $(ML_PID)))..."; \
		kill $$(cat $(ML_PID)) 2>/dev/null || true; \
		rm -f $(ML_PID); \
	fi
	@echo "==> Clean complete."

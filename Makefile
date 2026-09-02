.PHONY: setup dev dev-frontend clean

# Paths
BACKEND_DIR := backend
ML_DIR := ml-engine
FRONTEND_DIR := frontend
VENV := $(ML_DIR)/venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn
NPM := npm

# PID files for clean shutdown
BACKEND_PID := .backend.pid
ML_PID := .ml.pid
FRONTEND_PID := .frontend.pid

## setup: Create Python venv, install requirements, Go modules, and frontend deps
setup:
	@echo "==> Setting up Python virtual environment..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	@echo "==> Installing CPU-only PyTorch (saves ~2 GB vs CUDA build)..."
	$(PIP) install torch torchvision --index-url https://download.pytorch.org/whl/cpu
	$(PIP) install -r $(ML_DIR)/requirements.txt
	@echo "==> Tidying Go modules..."
	cd $(BACKEND_DIR) && go mod tidy
	@echo "==> Installing frontend dependencies..."
	cd $(FRONTEND_DIR) && $(NPM) install
	@echo "==> Setup complete."

## dev: Run ML engine + Go backend
dev: clean
	@test -f $(UVICORN) || (echo "ERROR: uvicorn not found. Run 'make setup' first." && exit 1)
	@echo "==> Starting ML engine on :8000..."
	cd $(ML_DIR) && ./venv/bin/uvicorn main:app --reload --port 8000 & echo $$! > ../$(ML_PID)
	@echo "==> Starting Go backend on :3000..."
	cd $(BACKEND_DIR) && go run main.go & echo $$! > ../$(BACKEND_PID)
	@echo "==> API services running."
	@echo "    Backend : http://localhost:3000"
	@echo "    ML      : http://localhost:8000"
	@echo "    Run 'make dev-frontend' in another terminal for the UI (:5173)"
	@wait

## dev-frontend: Run SvelteKit dev server (requires 'make dev' in another terminal)
dev-frontend:
	@test -d $(FRONTEND_DIR)/node_modules || (echo "ERROR: Run 'make setup' first." && exit 1)
	@echo "==> Starting SvelteKit frontend on :5173..."
	cd $(FRONTEND_DIR) && $(NPM) run dev

## dev-all: Run all services including frontend (background API + foreground UI)
dev-all: clean
	@test -f $(UVICORN) || (echo "ERROR: uvicorn not found. Run 'make setup' first." && exit 1)
	@test -d $(FRONTEND_DIR)/node_modules || (echo "ERROR: Run 'make setup' first." && exit 1)
	@echo "==> Starting ML engine on :8000..."
	cd $(ML_DIR) && ./venv/bin/uvicorn main:app --reload --port 8000 & echo $$! > ../$(ML_PID)
	@echo "==> Starting Go backend on :3000..."
	cd $(BACKEND_DIR) && go run main.go & echo $$! > ../$(BACKEND_PID)
	@sleep 2
	@echo "==> Starting SvelteKit frontend on :5173..."
	cd $(FRONTEND_DIR) && $(NPM) run dev & echo $$! > ../$(FRONTEND_PID)
	@echo "==> All services running. Press Ctrl+C or run 'make clean' to stop."
	@echo "    Frontend: http://localhost:5173"
	@echo "    Backend : http://localhost:3000"
	@echo "    ML      : http://localhost:8000"
	@wait

## clean: Kill background processes
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
	@if [ -f $(FRONTEND_PID) ]; then \
		echo "==> Stopping frontend (PID $$(cat $(FRONTEND_PID)))..."; \
		kill $$(cat $(FRONTEND_PID)) 2>/dev/null || true; \
		rm -f $(FRONTEND_PID); \
	fi
	@fuser -k 3000/tcp 2>/dev/null || true
	@fuser -k 8000/tcp 2>/dev/null || true
	@fuser -k 5173/tcp 2>/dev/null || true
	@echo "==> Clean complete."

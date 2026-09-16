.PHONY: help install dev test lint docker-build run

help:
	@echo "PD3board Financial Workstation Commands:"
	@echo "  make install      Install Python dependencies"
	@echo "  make dev          Run local development server with auto-reload"
	@echo "  make test         Execute test suite"
	@echo "  make docker-build Build container image"
	@echo "  make run          Start server on port 8000"

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest tests/ -v

docker-build:
	docker build -t pd3board:latest .

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

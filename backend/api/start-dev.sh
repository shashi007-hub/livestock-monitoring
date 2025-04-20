#!/bin/bash
echo "Running FastAPI in dev mode with auto-reload..."
export PYTHONPATH=./app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

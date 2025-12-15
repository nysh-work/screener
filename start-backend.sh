#!/bin/bash
#
# Start the FastAPI backend server
#

echo "Starting FastAPI backend server..."
echo "API will be available at: http://localhost:8000"
echo "API docs will be available at: http://localhost:8000/docs"
echo ""

python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

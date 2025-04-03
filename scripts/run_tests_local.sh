#!/bin/bash
set -e

# Start the server in the background
echo "Starting server..."
uvicorn main:app --host 0.0.0.0 --port 8088 &
SERVER_PID=$!

# Wait for the server to start
echo "Waiting for server to start..."
sleep 2

# Run the tests
echo "Running tests..."
uv run python tests/test_server.py
echo "Running Python execution tests..."
uv run pytest tests/test_python_execution.py -v

# Cleanup - kill the server
echo "Stopping server..."
kill $SERVER_PID

echo "Done."

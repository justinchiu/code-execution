#!/bin/bash
set -e

# Start the server in the background
echo "Starting server..."
uvicorn main:app --host 0.0.0.0 --port 8080 &
SERVER_PID=$!

# Wait for the server to start
echo "Waiting for server to start..."
sleep 2

# Run the tests
echo "Running tests..."
python test_cpp.py

# Cleanup - kill the server
echo "Stopping server..."
kill $SERVER_PID

echo "Done."

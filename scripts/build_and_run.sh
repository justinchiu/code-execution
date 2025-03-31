#!/bin/bash
set -e

echo "Building Docker image..."
docker build -t code-execution-server .

echo "Running Docker container..."
docker run -p 8080:8080 --rm code-execution-server

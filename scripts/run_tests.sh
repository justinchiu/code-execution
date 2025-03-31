#!/bin/bash
set -e

# Server should be running in docker container
# Run the tests
echo "Running tests..."
uv run python tests/test_server.py
uv run python tests/test_codecontests.py
echo "Done."

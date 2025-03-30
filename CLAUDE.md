# Claude Code Execution Project Guide

This document provides important information for Claude when working on this code execution server project.

## Project Overview

This is a FastAPI-based code execution server that:
- Accepts code submissions in various languages (starting with C++)
- Executes the code against provided test cases
- Returns test results and performance metrics
- Runs in a Docker container deployable to Google Cloud Run

## Commands to Run

### Adding packages

```bash
uv add {library}
```

### Linting

```bash
uv run ruff check .
```

### Type Checking 

```bash
uv run pyright .
```

### Run Local Server

```bash
uvicorn main:app --reload
```

## Development Guidelines

1. Always maintain strict security measures when handling code execution
2. Use temporary files that are properly cleaned up
3. Set execution time limits to prevent infinite loops
4. Track performance metrics for both compilation and execution
5. Ensure thorough validation of all inputs

## Project Structure

- `main.py` - FastAPI server and endpoints
- `Dockerfile` - Container configuration
- `scripts/` - Utility scripts

## API Structure

Request format includes:
- Code string
- List of stdin/stdout test cases
- Language identifier

Response includes:
- Test results (pass/fail) for each test case
- Performance metrics (compilation time, execution time)

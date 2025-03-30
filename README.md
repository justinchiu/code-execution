# Code Execution Server

A fast code execution server that runs on Google Cloud Run.

## Overview

This server accepts code submissions in C++, compiles and executes them against provided test cases, and returns the results with performance metrics.

## Running the Server

### Local Development

1. Install dependencies:
   ```bash
   uv add fastapi pydantic uvicorn requests
   ```

2. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

3. Test the server:
   ```bash
   # Simple test with basic C++ code
   python test_server.py
   
   # Code contests test suite with various algorithms
   ./scripts/run_tests.sh
   ```

### Using Docker

1. Build and run the Docker container:
   ```bash
   ./scripts/build_and_run.sh
   ```

2. The server will be accessible at: http://localhost:8080

### Deploying to Google Cloud Run

1. Update the configuration in `scripts/deploy_to_cloud_run.sh`:
   - Set your Google Cloud project ID
   - Configure region if needed

2. Run the deployment script:
   ```bash
   ./scripts/deploy_to_cloud_run.sh
   ```

3. The script will output the deployed service URL

## API

### Request Format

```json
{
  "code": "string",
  "stdin_stdout": [
    {
      "stdin": "string",
      "stdout": "string"
    }
  ],
  "language": "string"
}
```

### Response Format

```json
{
  "results": [
    {
      "stdin": "string",
      "expected_stdout": "string",
      "actual_stdout": "string",
      "passed": boolean
    }
  ],
  "metrics": {
    "compilation_time_ms": number,
    "execution_time_ms": number
  }
}
```
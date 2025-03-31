# Code Execution Server

A (maybe) fast code execution server that runs on Google Cloud Run.

## Overview

This server accepts code submissions in C++, compiles and executes them against provided test cases, and returns the results with performance metrics.

## Running the Server

### Local Development (Avoid)
This will not work for CodeContests, unless you have setup your environment for it.
Not easy on OSX.

1. Install dependencies:
   ```bash
   uv add fastapi pydantic uvicorn requests
   ```
   GCC and boost are also needed.

2. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

3. Test the server:
   ```bash
   # Simple test with basic C++ code
   bash scripts/run_tests_local.sh
   
   # Code contests test suite...if your computer can handle it
   bash scripts/run_tests.sh
   ```

### Using Docker (Preferred)

1. Build and run the Docker container:
   ```bash
   bash scripts/build_and_run.sh
   ```

2. The server will be accessible at: http://localhost:8080
You can check the server with
```bash
bash scripts/run_tests.sh
```

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

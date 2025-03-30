# Code Execution Server

A fast code execution server that runs on Google Cloud Run.

## Architecture

- FastAPI server that accepts and executes code
- Docker container for deployment to Google Cloud Run
- Supports multiple programming languages (starting with C++, Python later)

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
    "compilation_time_seconds": number,
    "execution_time_seconds": number
  }
}
```

## Implementation Plan

1. Create FastAPI server
   - Define request/response models
   - Set up endpoints

2. Implement C++ execution
   - Save code to temporary directory
   - Compile via subprocess
   - Execute with provided stdin
   - Check output against expected stdout
   - Measure execution metrics

3. Containerize the application
   - Create Dockerfile with all necessary dependencies
   - Add security measures to prevent malicious code execution

4. Deploy to Google Cloud Run
   - Set up Google Cloud project
   - Configure Cloud Run service

## Security Considerations

- Impose time and memory limits
- Restrict network access
- Run code in isolated sandbox
- Sanitize inputs


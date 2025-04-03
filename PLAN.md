# Python Execution Support Plan

## Overview
This plan outlines the steps to add Python code execution support to the existing FastAPI-based code execution server that currently only supports C++, with proper abstraction to easily support additional languages in the future.

## Current Architecture
- The server accepts code submissions in C++
- Compiles and executes the code against provided test cases
- Returns test results and performance metrics

## Implementation Plan

### 1. Package Structure Reorganization

```
code-execution/
├── main.py                             # FastAPI entry point
├── src/                                # Source directory
│   └── code_execution/                 # Package directory 
│       ├── __init__.py                 # Package initialization
│       ├── languages/                  # Language handlers
│       │   ├── __init__.py             # Exports language handlers
│       │   ├── base.py                 # Base language handler class
│       │   ├── cpp.py                  # C++ implementation
│       │   └── python.py               # Python implementation
│       ├── types.py                    # Pydantic model definitions
│       └── execution.py                # Common execution utilities
```

### 2. Class Abstraction

Create a base language handler class:

```python
# src/code_execution/languages/base.py
from abc import ABC, abstractmethod
from typing import List
from code_execution.types import StdinStdout, Output

class LanguageHandler(ABC):
    """Base class for language handlers"""
    
    @property
    @abstractmethod
    def language_id(self) -> str:
        """Return the language identifier"""
        pass
    
    @abstractmethod
    def compile(self, code: str, output_path: str) -> Output:
        """Compile the code (if needed) and return compilation output"""
        pass
    
    @abstractmethod
    def execute(self, code_path: str, test: StdinStdout) -> Output:
        """Execute the code with the given input and return execution output"""
        pass
```

### 3. Language-Specific Implementations

#### C++ Implementation
```python
# src/code_execution/languages/cpp.py
import os
import tempfile
import subprocess
import time
from typing import List
from code_execution.types import StdinStdout, Output
from code_execution.languages.base import LanguageHandler

class CppHandler(LanguageHandler):
    @property
    def language_id(self) -> str:
        return "cpp"
    
    def compile(self, code: str, output_path: str) -> Output:
        # Moved from current compile_cpp function
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(
            suffix=".cpp", delete=False, mode="w"
        ) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code)

        start_time = time.time()
        try:
            # Compile the code
            compile_process = subprocess.run(
                ["g++", "-std=c++20", "-o", output_path, temp_file_path],
                capture_output=True,
                text=True,
                timeout=60,  # 60 seconds timeout for compilation
            )
            compilation_time = time.time() - start_time  # seconds

            if compile_process.returncode != 0:
                return Output(
                    passed=False,
                    stdout="",
                    stderr=compile_process.stderr,
                    time_seconds=compilation_time,
                    timed_out=False,
                )
            return Output(
                passed=True,
                stdout="",
                stderr="",
                time_seconds=compilation_time,
                timed_out=False,
            )
        except subprocess.TimeoutExpired:
            return Output(
                passed=False,
                stdout="",
                stderr="Compilation timed out",
                time_seconds=(time.time() - start_time),
                timed_out=True,
            )
        finally:
            # Clean up the temporary CPP file
            os.unlink(temp_file_path)
        
    def execute(self, executable_path: str, test: StdinStdout) -> Output:
        # Moved from current execute_program function
        start_time = time.time()
        try:
            # Run the compiled program
            process = subprocess.run(
                [executable_path],
                input=test.stdin,
                capture_output=True,
                text=True,
                timeout=120,  # 120 seconds timeout for execution
            )
            execution_time = time.time() - start_time  # seconds

            return Output(
                passed=process.stdout.strip() == test.stdout.strip(),
                stdout=process.stdout,
                stderr=process.stderr,
                time_seconds=execution_time,
                timed_out=False,
            )
        except subprocess.TimeoutExpired:
            return Output(
                passed=False,
                stdout="Error: Timed out",
                stderr="Error: Timed out",
                time_seconds=(time.time() - start_time),
                timed_out=True,
            )
```

#### Python Implementation
```python
# src/code_execution/languages/python.py
import os
import tempfile
import subprocess
import time
from typing import List
from code_execution.types import StdinStdout, Output
from code_execution.languages.base import LanguageHandler

class PythonHandler(LanguageHandler):
    @property
    def language_id(self) -> str:
        return "python"
    
    def compile(self, code: str, output_path: str) -> Output:
        # Python doesn't need compilation, write code to file
        with open(output_path, 'w') as f:
            f.write(code)
        
        return Output(
            passed=True,
            stdout="",
            stderr="",
            time_seconds=0,  # No compilation time for Python
            timed_out=False,
        )
        
    def execute(self, code_path: str, test: StdinStdout) -> Output:
        # Execute Python script
        start_time = time.time()
        try:
            # Run the Python script
            process = subprocess.run(
                ["python3", code_path],
                input=test.stdin,
                capture_output=True,
                text=True,
                timeout=120,  # 120 seconds timeout for execution
            )
            execution_time = time.time() - start_time  # seconds

            return Output(
                passed=process.stdout.strip() == test.stdout.strip(),
                stdout=process.stdout,
                stderr=process.stderr,
                time_seconds=execution_time,
                timed_out=False,
            )
        except subprocess.TimeoutExpired:
            return Output(
                passed=False,
                stdout="Error: Timed out",
                stderr="Error: Timed out",
                time_seconds=(time.time() - start_time),
                timed_out=True,
            )
```

### 4. Language Factory

```python
# src/code_execution/languages/__init__.py
from typing import Dict, Type
from code_execution.languages.base import LanguageHandler
from code_execution.languages.cpp import CppHandler
from code_execution.languages.python import PythonHandler

_HANDLERS: Dict[str, Type[LanguageHandler]] = {
    "cpp": CppHandler,
    "python": PythonHandler,
}

def get_language_handler(language: str) -> LanguageHandler:
    """Get a language handler instance for the specified language"""
    language = language.lower()
    if language not in _HANDLERS:
        supported = ", ".join(f"'{lang}'" for lang in _HANDLERS.keys())
        raise ValueError(
            f"Language '{language}' is not supported. Supported languages: {supported}"
        )
    return _HANDLERS[language]()
```

### 5. Refactored Main.py

```python
# main.py
from fastapi import FastAPI, HTTPException
from src.code_execution.types import CodeExecutionRequest, CodeExecutionResponse
from src.code_execution.languages import get_language_handler
import tempfile
import os
import shutil

app = FastAPI(title="Code Execution API")

@app.post("/execute", response_model=CodeExecutionResponse)
def execute_code(request: CodeExecutionRequest) -> CodeExecutionResponse:
    try:
        handler = get_language_handler(request.language)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    code_path = os.path.join(temp_dir, f"program{'.py' if handler.language_id == 'python' else ''}")
    
    try:
        # Compile/prepare the code
        compile_output = handler.compile(request.code, code_path)
        
        if not compile_output.passed:
            return CodeExecutionResponse(
                compile_output=compile_output,
                exec_outputs=[],
                all_passed=False,
            )
        
        # Execute tests
        results = []
        
        for test_case in request.stdin_stdout:
            exec_output = handler.execute(code_path, test_case)
            results.append(exec_output)
        
        return CodeExecutionResponse(
            compile_output=compile_output,
            exec_outputs=results,
            all_passed=all([r.passed for r in results])
        )
    
    finally:
        # Clean up
        shutil.rmtree(temp_dir)
```

### 6. Types Definition

```python
# src/code_execution/types.py
from typing import List
from pydantic import BaseModel

class StdinStdout(BaseModel):
    stdin: str
    stdout: str

class CodeExecutionRequest(BaseModel):
    code: str
    stdin_stdout: List[StdinStdout]
    language: str

class Output(BaseModel):
    passed: bool
    stdout: str
    stderr: str
    time_seconds: float
    timed_out: bool

class CodeExecutionResponse(BaseModel):
    compile_output: Output
    exec_outputs: List[Output]
    all_passed: bool
```

### 7. Security Considerations
- Set execution time limits (similar to C++)
- Run in a sandboxed environment
- Implement resource limitations (CPU, memory)
- Consider restricting imports or using a sandboxed Python interpreter

### 8. Testing

Create a dedicated test file for Python code execution:

```python
# tests/test_python_execution.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test cases for Python execution
def test_hello_world_python():
    """Test a simple hello world program in Python"""
    payload = {
        "code": """
name = input()
print(f"Hello, {name}!")
        """,
        "stdin_stdout": [
            {"stdin": "World", "stdout": "Hello, World!"},
            {"stdin": "CodeContests", "stdout": "Hello, CodeContests!"},
        ],
        "language": "python",
    }
    response = client.post("/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["all_passed"] == True
    assert len(data["exec_outputs"]) == 2
    for output in data["exec_outputs"]:
        assert output["passed"] == True

def test_sum_two_numbers_python():
    """Test addition of two numbers in Python"""
    payload = {
        "code": """
a, b = map(int, input().split())
print(a + b)
        """,
        "stdin_stdout": [
            {"stdin": "5 7", "stdout": "12"},
            {"stdin": "10 -3", "stdout": "7"},
            {"stdin": "0 0", "stdout": "0"},
        ],
        "language": "python",
    }
    response = client.post("/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["all_passed"] == True
    assert len(data["exec_outputs"]) == 3
    for output in data["exec_outputs"]:
        assert output["passed"] == True

def test_prime_check_python():
    """Test prime number checker in Python"""
    payload = {
        "code": """
def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

n = int(input())
if is_prime(n):
    print("YES")
else:
    print("NO")
        """,
        "stdin_stdout": [
            {"stdin": "7", "stdout": "YES"},
            {"stdin": "15", "stdout": "NO"},
            {"stdin": "23", "stdout": "YES"},
            {"stdin": "4", "stdout": "NO"},
        ],
        "language": "python",
    }
    response = client.post("/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["all_passed"] == True
    assert len(data["exec_outputs"]) == 4
    for output in data["exec_outputs"]:
        assert output["passed"] == True

def test_fibonacci_python():
    """Test Fibonacci sequence calculation in Python"""
    payload = {
        "code": """
n = int(input())

if n <= 0:
    print("0")
else:
    fib = [0] * (n + 1)
    fib[0] = 0
    
    if n >= 1:
        fib[1] = 1
    
    for i in range(2, n + 1):
        fib[i] = fib[i-1] + fib[i-2]
    
    print(fib[n])
        """,
        "stdin_stdout": [
            {"stdin": "5", "stdout": "5"},
            {"stdin": "10", "stdout": "55"},
            {"stdin": "1", "stdout": "1"},
            {"stdin": "0", "stdout": "0"},
        ],
        "language": "python",
    }
    response = client.post("/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["all_passed"] == True
    assert len(data["exec_outputs"]) == 4
    for output in data["exec_outputs"]:
        assert output["passed"] == True

def test_syntax_error_python():
    """Test handling of Python syntax errors"""
    payload = {
        "code": """
print("Missing closing parenthesis"
        """,
        "stdin_stdout": [
            {"stdin": "", "stdout": ""},
        ],
        "language": "python",
    }
    response = client.post("/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["all_passed"] == False
    assert data["compile_output"]["passed"] == False
    assert "SyntaxError" in data["compile_output"]["stderr"]

def test_timeout_python():
    """Test handling of infinite loops in Python"""
    payload = {
        "code": """
while True:
    pass  # Infinite loop
        """,
        "stdin_stdout": [
            {"stdin": "", "stdout": ""},
        ],
        "language": "python",
    }
    response = client.post("/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["all_passed"] == False
    assert data["exec_outputs"][0]["timed_out"] == True

def test_complex_data_structures_python():
    """Test Python code working with complex data structures"""
    payload = {
        "code": """
import json

# Parse JSON input
data = json.loads(input())
# Process data
result = {
    "sum": sum(data["numbers"]),
    "product": 1,
    "has_negative": False
}

for num in data["numbers"]:
    result["product"] *= num
    if num < 0:
        result["has_negative"] = True

# Output JSON result
print(json.dumps(result))
        """,
        "stdin_stdout": [
            {
                "stdin": '{"numbers": [1, 2, 3, 4, 5]}',
                "stdout": '{"sum": 15, "product": 120, "has_negative": false}'
            },
            {
                "stdin": '{"numbers": [-1, 2, -3, 4]}',
                "stdout": '{"sum": 2, "product": 24, "has_negative": true}'
            }
        ],
        "language": "python",
    }
    response = client.post("/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["all_passed"] == True
    assert len(data["exec_outputs"]) == 2
    for output in data["exec_outputs"]:
        assert output["passed"] == True
```

Additional tests to consider:
- Resource intensive calculations
- Memory usage limits
- Input/output with large data volumes
- Edge cases (empty inputs, Unicode handling)

### 9. Docker Configuration

The Dockerfile already has Python 3.11 installed:
```dockerfile
# From the Dockerfile
RUN apt-get install -yqq python3.11 python3-pip
```

No changes needed to the Dockerfile since Python is already installed.

### 10. Update Package Definition

Update `pyproject.toml` to reflect the new package structure:

```toml
[project]
name = "code-execution"
version = "0.1.0"
description = "Code execution service for multiple programming languages"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "datasets>=3.5.0",
    "fastapi>=0.115.12",
    "gunicorn>=23.0.0",
    "morphcloud>=0.1.32",
    "pre-commit>=4.2.0",
    "pydantic>=2.11.1",
    "pyright>=1.1.398",
    "requests>=2.32.3",
    "ruff>=0.11.2",
    "uvicorn>=0.34.0",
    "google-auth>=2.28.0",
    "google-auth-oauthlib>=1.1.0",
    "google-cloud-run>=0.10.17",
]

[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = []

[tool.ruff.lint.isort]
known-first-party = ["src", "code_execution"]

[tool.pyright]
include = ["**/*.py"]
exclude = ["**/__pycache__"]
venv = "env"
```

## Implementation Priority

1. Package restructuring
2. Base class and language implementations
3. Core Python execution functionality
4. Security hardening
5. Testing
6. Documentation updates

## Future Considerations

- Language-specific optimizations
- Additional language support (JavaScript, Java, etc.)
- More detailed performance metrics
- Code analysis and feedback

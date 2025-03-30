import os
import tempfile
import subprocess
import time
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import shutil

app = FastAPI(title="Code Execution API")


class StdinStdout(BaseModel):
    stdin: str
    stdout: str


class CodeExecutionRequest(BaseModel):
    code: str
    stdin_stdout: List[StdinStdout]
    language: str


class TestResult(BaseModel):
    stdin: str
    expected_stdout: str
    actual_stdout: str
    passed: bool


class ExecutionMetrics(BaseModel):
    compilation_time_ms: float
    execution_time_ms: float


class CodeExecutionResponse(BaseModel):
    results: List[TestResult]
    metrics: ExecutionMetrics


def compile_cpp(code: str, output_path: str) -> tuple[bool, str, float]:
    """Compile C++ code and return success status, error message if any, and compilation time"""
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
            ["g++", "-std=c++17", "-o", output_path, temp_file_path],
            capture_output=True,
            text=True,
            timeout=60,  # 60 seconds timeout for compilation
        )
        compilation_time = time.time() - start_time  # seconds

        if compile_process.returncode != 0:
            return False, compile_process.stderr, compilation_time
        return True, "", compilation_time
    except subprocess.TimeoutExpired:
        return False, "Compilation timed out", (time.time() - start_time) * 1000
    finally:
        # Clean up the temporary CPP file
        os.unlink(temp_file_path)


def execute_program(executable_path: str, stdin: str) -> tuple[str, float]:
    """Execute the compiled program with the given stdin and return stdout and execution time"""
    start_time = time.time()
    try:
        # Run the compiled program
        process = subprocess.run(
            [executable_path],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=120,  # 120 seconds timeout for execution
        )
        execution_time = time.time() - start_time  # seconds

        return process.stdout.strip(), execution_time
    except subprocess.TimeoutExpired:
        return "Execution timed out", (time.time() - start_time) * 1000


@app.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest) -> CodeExecutionResponse:
    if request.language.lower() != "cpp":
        raise HTTPException(
            status_code=400,
            detail=f"Language '{request.language}' is not supported. Currently only 'cpp' is supported.",
        )

    # Create a temporary directory for the executable
    temp_dir = tempfile.mkdtemp()
    executable_path = os.path.join(temp_dir, "program")

    try:
        # Compile the code
        compile_success, compile_error, compilation_time = compile_cpp(
            request.code, executable_path
        )

        if not compile_success:
            raise HTTPException(
                status_code=400, detail=f"Compilation error: {compile_error}"
            )

        # Execute tests
        results = []
        total_execution_time = 0

        for test_case in request.stdin_stdout:
            actual_stdout, execution_time = execute_program(
                executable_path, test_case.stdin
            )
            total_execution_time += execution_time

            results.append(
                TestResult(
                    stdin=test_case.stdin,
                    expected_stdout=test_case.stdout,
                    actual_stdout=actual_stdout,
                    passed=actual_stdout == test_case.stdout,
                )
            )

        # Calculate average execution time
        avg_execution_time = (
            total_execution_time / len(request.stdin_stdout)
            if request.stdin_stdout
            else 0
        )

        return CodeExecutionResponse(
            results=results,
            metrics=ExecutionMetrics(
                compilation_time_ms=compilation_time,
                execution_time_ms=avg_execution_time,
            ),
        )

    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)

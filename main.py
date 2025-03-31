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


def compile_cpp(code: str, output_path: str) -> Output:
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


def execute_program(executable_path: str, test: StdinStdout) -> Output:
    """Execute the compiled program with the given stdin and return stdout and execution time"""
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
            #passed=process.stdout == test.stdout,
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
        compile_output = compile_cpp(request.code, executable_path)

        if not compile_output.passed:
            return CodeExecutionResponse(
                compile_output=compile_output,
                exec_outputs=[],
                all_passed=False,
            )

        # Execute tests
        results = []
        total_execution_time = 0

        for test_case in request.stdin_stdout:
            exec_output = execute_program(executable_path, test_case)
            results.append(exec_output)
            total_execution_time += exec_output.time_seconds

        return CodeExecutionResponse(
            compile_output=compile_output,
            exec_outputs=results,
            all_passed=all([r.passed for r in results])
        )

    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)

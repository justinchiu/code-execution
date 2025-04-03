import os
import tempfile
import subprocess
import time
from code_execution.types import StdinStdout, Output
from code_execution.languages.base import LanguageHandler

class CppHandler(LanguageHandler):
    @property
    def language_id(self) -> str:
        return "cpp"
    
    def compile(self, code: str, output_path: str) -> Output:
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
        
    def execute(self, code_path: str, test: StdinStdout) -> Output:
        start_time = time.time()
        try:
            # Run the compiled program
            process = subprocess.run(
                [code_path],
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
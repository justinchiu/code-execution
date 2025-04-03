import subprocess
import time
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
                timeout=30,  # 30 seconds timeout for execution (reduced for testing)
                check=False,
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

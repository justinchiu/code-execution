import os
import tempfile
import shutil

from fastapi import FastAPI, HTTPException
from code_execution.types import CodeExecutionRequest, CodeExecutionResponse
from code_execution.languages import get_language_handler

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
        print("BLAH")
        print(compile_output)
        
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
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)

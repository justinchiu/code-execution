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
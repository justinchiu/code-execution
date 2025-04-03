from abc import ABC, abstractmethod
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
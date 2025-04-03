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
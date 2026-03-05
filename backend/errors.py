"""
Custom exception classes for the Smart Recipe Analyzer API.
These exceptions are caught by FastAPI exception handlers and returned as Pydantic error responses.
"""
from models import ValidationError, ErrorDetail, MalformedLLMResponse, ExternalServiceError


class RecipeAnalyzerError(Exception):
    """Base exception for all application errors."""
    pass


class InvalidIngredientsError(RecipeAnalyzerError):
    """Raised when ingredients input is invalid or empty."""
    def __init__(self, details: list[str] | None = None):
        self.details = details or ["Ingredients input is invalid"]
        super().__init__(f"Invalid ingredients: {self.details}")

    def to_pydantic(self) -> ValidationError:
        """Convert to Pydantic error model."""
        return ValidationError(
            details=[ErrorDetail(code="invalid_input", message=msg) for msg in self.details]
        )


class MalformedLLMResponseError(RecipeAnalyzerError):
    """Raised when LLM returns invalid JSON or doesn't match schema."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

    def to_pydantic(self) -> MalformedLLMResponse:
        """Convert to Pydantic error model."""
        return MalformedLLMResponse(message=self.message)


class ExternalServiceUnavailableError(RecipeAnalyzerError):
    """Raised when OpenRouter or external service is unreachable."""
    def __init__(self, service: str = "OpenRouter", message: str | None = None):
        self.message = message or f"{service} is currently unavailable"
        super().__init__(self.message)

    def to_pydantic(self) -> ExternalServiceError:
        """Convert to Pydantic error model."""
        return ExternalServiceError(message=self.message)

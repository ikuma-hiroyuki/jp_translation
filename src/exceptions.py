"""Custom exceptions for the Markdown Translator application."""


class TranslatorError(Exception):
    """Base exception for the translator application."""
    pass


class TranslationError(TranslatorError):
    """Exception raised during translation processing."""
    pass


class APIError(TranslatorError):
    """Exception raised during API communication."""
    pass


class RateLimitError(APIError):
    """Exception raised when API rate limit is reached."""
    pass


class FileSystemError(TranslatorError):
    """Exception raised during file system operations."""
    pass

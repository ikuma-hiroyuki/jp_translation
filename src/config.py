"""Configuration data classes for the Markdown Translator."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TranslationConfig:
    """Configuration for translation operations."""
    source_directory: Path
    output_directory_name: str = "jp"
    target_language: str = "Japanese"
    model_name: str = "gemini-3-flash-preview"
    max_retries: int = 3
    retry_delay: float = 1.0  # Initial retry delay in seconds (exponential backoff)
    rate_limit_wait: float = 60.0  # Wait time for rate limit errors in seconds

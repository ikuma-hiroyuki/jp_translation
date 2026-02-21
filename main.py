"""Main entry point for the Markdown Translator application."""

import argparse
import sys
from pathlib import Path

from src.api_client import GeminiAPIClient
from src.file_service import FileSystemService
from src.translation_service import TranslationService
from src.orchestrator import TranslationOrchestrator
from src.config import TranslationConfig
from src.exceptions import TranslatorError


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Translate Markdown files to Japanese using GCP Gemini API"
    )
    parser.add_argument(
        "directory",
        type=str,
        help="Directory containing Markdown files to translate"
    )
    return parser.parse_args()


def validate_directory(path: str) -> Path:
    """
    Validate directory path.

    Args:
        path: Directory path to validate

    Returns:
        Path: Validated Path object

    Raises:
        ValueError: If directory does not exist or is not a directory
    """
    directory = Path(path)

    if not directory.exists():
        raise ValueError(f"Directory does not exist: {path}")

    if not directory.is_dir():
        raise ValueError(f"Path is not a directory: {path}")

    return directory


def main() -> int:
    """
    Application entry point.

    Returns:
        int: Exit code (0=success, 1=error)
    """
    try:
        # Parse command-line arguments
        args = parse_arguments()

        # Validate directory
        try:
            source_dir = validate_directory(args.directory)
        except ValueError as e:
            print(f"[ERROR] {e}")
            return 1

        print(f"[INFO] Source directory: {source_dir}")

        # Load API key from .env file
        try:
            api_key = GeminiAPIClient.load_api_key_from_env()
        except FileNotFoundError as e:
            print(f"[ERROR] {e}")
            return 1
        except ValueError as e:
            print(f"[ERROR] {e}")
            return 1

        # Initialize components
        try:
            # Create translation configuration
            config = TranslationConfig(
                source_directory=source_dir,
                output_directory_name="jp",
                target_language="Japanese",
                model_name="gemini-3-flash-preview",
                max_retries=3,
                retry_delay=1.0,
                rate_limit_wait=60.0
            )

            # Initialize API client with retry configuration
            api_client = GeminiAPIClient(
                api_key,
                model_name=config.model_name,
                max_retries=config.max_retries,
                retry_delay=config.retry_delay,
                rate_limit_wait=config.rate_limit_wait
            )
            file_service = FileSystemService()
            translation_service = TranslationService(api_client)
            orchestrator = TranslationOrchestrator(file_service, translation_service)
        except Exception as e:
            print(f"[ERROR] Failed to initialize application: {e}")
            return 1

        # Execute translation
        print("[INFO] Starting translation process...")
        results = orchestrator.translate_directory(source_dir, output_dir_name=config.output_directory_name)

        # Print summary
        orchestrator.print_summary(results)

        # Determine exit code based on results
        if not results:
            # No files processed
            return 0

        failed_count = sum(1 for r in results if not r.success)
        if failed_count > 0:
            return 1

        return 0

    except KeyboardInterrupt:
        print("\n[INFO] Translation interrupted by user")
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

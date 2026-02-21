"""Orchestrator for coordinating the translation process."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .file_service import FileSystemService
from .translation_service import TranslationService
from .exceptions import TranslationError


@dataclass
class TranslationResult:
    """Data class representing the result of a file translation."""
    source_file: Path
    success: bool
    error_message: Optional[str] = None


class TranslationOrchestrator:
    """Orchestrator for coordinating the entire translation process."""

    def __init__(
        self,
        file_service: FileSystemService,
        translation_service: TranslationService
    ):
        """
        Initialize the orchestrator.

        Args:
            file_service: FileSystemService instance for file operations
            translation_service: TranslationService instance for translation
        """
        self.file_service = file_service
        self.translation_service = translation_service

    def translate_directory(self, source_dir: Path, output_dir_name: str = "jp") -> list[TranslationResult]:
        """
        Translate all Markdown files in a directory.

        This method coordinates the entire translation process:
        1. Find all Markdown files in the source directory
        2. For each file, read, translate, and write the output
        3. Continue processing even if individual files fail
        4. Return results for all files

        Args:
            source_dir: Source directory containing Markdown files
            output_dir_name: Name of the output directory (default: "jp")

        Returns:
            list[TranslationResult]: Results for each file translation
        """
        results = []

        # Find all Markdown files
        try:
            markdown_files = self.file_service.find_markdown_files(source_dir)
        except Exception as e:
            # If we can't even find files, return empty results
            print(f"[ERROR] Failed to find Markdown files: {e}")
            return results

        if not markdown_files:
            print("[INFO] No Markdown files found in directory")
            return results

        print(f"[INFO] Found {len(markdown_files)} Markdown file(s) to translate")

        # Process each file
        for source_file in markdown_files:
            result = self._translate_single_file(source_file, source_dir, output_dir_name)
            results.append(result)

        return results

    def _translate_single_file(
        self,
        source_file: Path,
        source_dir: Path,
        output_dir_name: str = "jp"
    ) -> TranslationResult:
        """
        Translate a single Markdown file.

        Args:
            source_file: Path to the source file
            source_dir: Source directory (for creating output path)
            output_dir_name: Name of the output directory (default: "jp")

        Returns:
            TranslationResult: Result of the translation
        """
        print(f"[INFO] Processing: {source_file.relative_to(source_dir)}")

        try:
            # Read the source file
            content = self.file_service.read_file(source_file)

            # Translate the content
            translated_content = self.translation_service.translate_markdown(content)

            # Translate the filename (without extension)
            original_stem = source_file.stem
            try:
                # Translate filename using the translation service's API client
                translated_stem = self.translation_service.api_client.translate_text(
                    original_stem,
                    target_language="Japanese"
                )
                # Clean up the translated filename (remove special characters that are invalid in filenames)
                translated_stem = translated_stem.replace('/', '_').replace('\\', '_').replace(':', '_')
            except Exception as e:
                # If filename translation fails, use original filename
                print(f"[WARNING] Failed to translate filename, using original: {e}")
                translated_stem = original_stem

            # Create output path with translated filename
            output_path = self.file_service.create_output_path(
                source_file,
                source_dir,
                output_dir_name=output_dir_name
            )

            # Replace the filename with translated version
            output_path = output_path.parent / f"{translated_stem}.md"

            # Write the translated content
            self.file_service.write_file(output_path, translated_content)

            print(f"[INFO] Successfully translated: {source_file.relative_to(source_dir)} -> {output_path.relative_to(source_dir)}")
            return TranslationResult(
                source_file=source_file,
                success=True
            )

        except Exception as e:
            # Log the error and continue processing
            error_msg = str(e)
            print(f"[ERROR] Failed to translate file: {source_file.relative_to(source_dir)}")
            print(f"Reason: {error_msg}")

            return TranslationResult(
                source_file=source_file,
                success=False,
                error_message=error_msg
            )

    def print_summary(self, results: list[TranslationResult]) -> None:
        """
        Print a summary of translation results.

        Args:
            results: List of translation results
        """
        if not results:
            print("\n[SUMMARY] No files were processed")
            return

        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        print("\n" + "=" * 60)
        print("TRANSLATION SUMMARY")
        print("=" * 60)
        print(f"Total files: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")

        if failed:
            print("\nFailed files:")
            for result in failed:
                print(f"  - {result.source_file}")
                if result.error_message:
                    print(f"    Error: {result.error_message}")

        print("=" * 60)

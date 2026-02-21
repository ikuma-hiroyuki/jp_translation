"""Integration tests for all components working together."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.api_client import GeminiAPIClient
from src.file_service import FileSystemService
from src.translation_service import TranslationService
from src.orchestrator import TranslationOrchestrator, TranslationResult
from src.exceptions import APIError, RateLimitError, TranslationError


class TestComponentIntegration:
    """Test all components working together with actual directory structures."""

    def test_end_to_end_translation_with_directory_structure(self, tmp_path):
        """
        Test complete translation workflow with actual directory structure.

        Validates: Requirements 1.1, 2.1, 4.1, 5.3, 6.1
        """
        # Create a realistic directory structure
        source_dir = tmp_path / "docs"
        source_dir.mkdir()

        # Create nested directories with markdown files
        (source_dir / "guide").mkdir()
        (source_dir / "api").mkdir()
        (source_dir / "api" / "v1").mkdir()

        # Create markdown files
        readme_content = "# README\n\nThis is a test document."
        guide_content = "# User Guide\n\n## Installation\n\nFollow these steps."
        api_content = "# API Reference\n\n### Endpoints\n\n- GET /users"
        v1_content = "# API v1\n\nVersion 1 documentation."

        (source_dir / "README.md").write_text(readme_content)
        (source_dir / "guide" / "user-guide.md").write_text(guide_content)
        (source_dir / "api" / "reference.md").write_text(api_content)
        (source_dir / "api" / "v1" / "spec.md").write_text(v1_content)

        # Mock API client
        mock_api_client = Mock(spec=GeminiAPIClient)
        mock_api_client.translate_text.side_effect = lambda text, **kwargs: f"[翻訳済み] {text}"

        # Initialize components
        file_service = FileSystemService()
        translation_service = TranslationService(mock_api_client)
        orchestrator = TranslationOrchestrator(file_service, translation_service)

        # Execute translation
        results = orchestrator.translate_directory(source_dir, output_dir_name="jp")

        # Verify all files were processed
        assert len(results) == 4
        assert all(r.success for r in results)

        # Verify directory structure is preserved
        output_dir = source_dir / "jp"
        assert output_dir.exists()
        assert (output_dir / "README.md").exists()
        assert (output_dir / "guide" / "user-guide.md").exists()
        assert (output_dir / "api" / "reference.md").exists()
        assert (output_dir / "api" / "v1" / "spec.md").exists()

        # Verify content was translated
        translated_readme = (output_dir / "README.md").read_text()
        assert "[翻訳済み]" in translated_readme
        assert "README" in translated_readme

        # Verify API was called for each file
        assert mock_api_client.translate_text.call_count == 4

    def test_integration_with_footnotes_preservation(self, tmp_path):
        """
        Test that footnotes are preserved during end-to-end translation.

        Validates: Requirements 4.1, 4.3
        """
        source_dir = tmp_path / "docs"
        source_dir.mkdir()

        # Create markdown with footnotes
        content_with_footnotes = """# Document Title

This is a paragraph with a footnote[^1].

Another paragraph with another footnote[^note].

[^1]: This is the first footnote.
[^note]: This is a named footnote.
"""

        (source_dir / "doc.md").write_text(content_with_footnotes)

        # Mock API client - should not receive footnotes
        mock_api_client = Mock(spec=GeminiAPIClient)

        def mock_translate(text, **kwargs):
            # Verify footnotes are not in the text sent to API
            assert "[^1]:" not in text
            assert "[^note]:" not in text
            return f"[翻訳済み] {text}"

        mock_api_client.translate_text.side_effect = mock_translate

        # Initialize and execute
        file_service = FileSystemService()
        translation_service = TranslationService(mock_api_client)
        orchestrator = TranslationOrchestrator(file_service, translation_service)

        results = orchestrator.translate_directory(source_dir)

        # Verify success
        assert len(results) == 1
        assert results[0].success

        # Verify footnotes are in the output
        output_file = source_dir / "jp" / "doc.md"
        translated_content = output_file.read_text()
        assert "[^1]:" in translated_content
        assert "[^note]:" in translated_content

    def test_integration_error_handling_continues_processing(self, tmp_path):
        """
        Test that errors in one file don't stop processing of other files.

        Validates: Requirements 4.4, 6.1, 6.2
        """
        source_dir = tmp_path / "docs"
        source_dir.mkdir()

        # Create multiple files
        (source_dir / "file1.md").write_text("# File 1")
        (source_dir / "file2.md").write_text("# File 2")
        (source_dir / "file3.md").write_text("# File 3")

        # Mock API client that fails on second file
        mock_api_client = Mock(spec=GeminiAPIClient)
        call_count = 0

        def mock_translate(text, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise APIError("API failed for file 2")
            return f"[翻訳済み] {text}"

        mock_api_client.translate_text.side_effect = mock_translate

        # Initialize and execute
        file_service = FileSystemService()
        translation_service = TranslationService(mock_api_client)
        orchestrator = TranslationOrchestrator(file_service, translation_service)

        results = orchestrator.translate_directory(source_dir)

        # Verify all files were attempted
        assert len(results) == 3

        # Verify one failed and two succeeded
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        assert len(successful) == 2
        assert len(failed) == 1

        # Verify error message is captured
        assert failed[0].error_message is not None
        assert "API failed" in failed[0].error_message

        # Verify successful files were written
        output_dir = source_dir / "jp"
        assert (output_dir / "file1.md").exists()
        assert (output_dir / "file3.md").exists()

    def test_integration_with_empty_directory(self, tmp_path):
        """
        Test handling of directory with no markdown files.

        Validates: Requirements 2.1, 2.3
        """
        source_dir = tmp_path / "empty"
        source_dir.mkdir()

        # Create some non-markdown files
        (source_dir / "readme.txt").write_text("Not a markdown file")
        (source_dir / "data.json").write_text("{}")

        # Mock API client (should not be called)
        mock_api_client = Mock(spec=GeminiAPIClient)

        # Initialize and execute
        file_service = FileSystemService()
        translation_service = TranslationService(mock_api_client)
        orchestrator = TranslationOrchestrator(file_service, translation_service)

        results = orchestrator.translate_directory(source_dir)

        # Verify no files were processed
        assert len(results) == 0

        # Verify API was never called
        mock_api_client.translate_text.assert_not_called()

    def test_integration_with_nested_directory_structure(self, tmp_path):
        """
        Test deeply nested directory structure preservation.

        Validates: Requirements 5.3
        """
        source_dir = tmp_path / "project"
        source_dir.mkdir()

        # Create deeply nested structure
        deep_path = source_dir / "docs" / "en" / "guides" / "advanced"
        deep_path.mkdir(parents=True)

        (deep_path / "tutorial.md").write_text("# Advanced Tutorial")

        # Mock API client
        mock_api_client = Mock(spec=GeminiAPIClient)
        mock_api_client.translate_text.return_value = "[翻訳済み] # Advanced Tutorial"

        # Initialize and execute
        file_service = FileSystemService()
        translation_service = TranslationService(mock_api_client)
        orchestrator = TranslationOrchestrator(file_service, translation_service)

        results = orchestrator.translate_directory(source_dir)

        # Verify file was processed
        assert len(results) == 1
        assert results[0].success

        # Verify deep structure is preserved
        output_file = source_dir / "jp" / "docs" / "en" / "guides" / "advanced" / "tutorial.md"
        assert output_file.exists()
        assert "[翻訳済み]" in output_file.read_text()

    def test_integration_file_read_error_handling(self, tmp_path):
        """
        Test handling of file read errors during integration.

        Validates: Requirements 6.1, 6.2
        """
        source_dir = tmp_path / "docs"
        source_dir.mkdir()

        (source_dir / "good.md").write_text("# Good File")
        (source_dir / "bad.md").write_text("# Bad File")

        # Mock API client
        mock_api_client = Mock(spec=GeminiAPIClient)
        mock_api_client.translate_text.return_value = "[翻訳済み] content"

        # Mock file service to fail on specific file
        file_service = FileSystemService()
        original_read = file_service.read_file

        def mock_read(file_path):
            if "bad.md" in str(file_path):
                raise IOError("Permission denied")
            return original_read(file_path)

        file_service.read_file = mock_read

        # Initialize and execute
        translation_service = TranslationService(mock_api_client)
        orchestrator = TranslationOrchestrator(file_service, translation_service)

        results = orchestrator.translate_directory(source_dir)

        # Verify both files were attempted
        assert len(results) == 2

        # Verify one succeeded and one failed
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        assert len(successful) == 1
        assert len(failed) == 1
        assert "Permission denied" in failed[0].error_message

    def test_integration_file_write_error_handling(self, tmp_path):
        """
        Test handling of file write errors during integration.

        Validates: Requirements 6.1, 6.2
        """
        source_dir = tmp_path / "docs"
        source_dir.mkdir()

        (source_dir / "test.md").write_text("# Test")

        # Mock API client
        mock_api_client = Mock(spec=GeminiAPIClient)
        mock_api_client.translate_text.return_value = "[翻訳済み] # Test"

        # Mock file service to fail on write
        file_service = FileSystemService()
        original_write = file_service.write_file

        def mock_write(file_path, content):
            raise IOError("Disk full")

        file_service.write_file = mock_write

        # Initialize and execute
        translation_service = TranslationService(mock_api_client)
        orchestrator = TranslationOrchestrator(file_service, translation_service)

        results = orchestrator.translate_directory(source_dir)

        # Verify file was attempted but failed
        assert len(results) == 1
        assert not results[0].success
        assert "Disk full" in results[0].error_message


class TestErrorScenarios:
    """Test various error scenarios in integration."""

    def test_api_rate_limit_error_propagation(self, tmp_path):
        """
        Test that rate limit errors are properly handled in integration.

        Validates: Requirements 4.5, 6.2
        """
        source_dir = tmp_path / "docs"
        source_dir.mkdir()

        (source_dir / "test.md").write_text("# Test")

        # Mock API client that raises rate limit error
        mock_api_client = Mock(spec=GeminiAPIClient)
        mock_api_client.translate_text.side_effect = RateLimitError("Rate limit exceeded")

        # Initialize and execute
        file_service = FileSystemService()
        translation_service = TranslationService(mock_api_client)
        orchestrator = TranslationOrchestrator(file_service, translation_service)

        results = orchestrator.translate_directory(source_dir)

        # Verify error was captured
        assert len(results) == 1
        assert not results[0].success
        assert "Rate limit" in results[0].error_message

    def test_translation_error_propagation(self, tmp_path):
        """
        Test that translation errors are properly handled in integration.

        Validates: Requirements 6.2
        """
        source_dir = tmp_path / "docs"
        source_dir.mkdir()

        (source_dir / "test.md").write_text("# Test")

        # Mock API client that raises generic error
        mock_api_client = Mock(spec=GeminiAPIClient)
        mock_api_client.translate_text.side_effect = Exception("Unexpected error")

        # Initialize and execute
        file_service = FileSystemService()
        translation_service = TranslationService(mock_api_client)
        orchestrator = TranslationOrchestrator(file_service, translation_service)

        results = orchestrator.translate_directory(source_dir)

        # Verify error was captured
        assert len(results) == 1
        assert not results[0].success
        assert results[0].error_message is not None

    def test_multiple_files_with_mixed_errors(self, tmp_path):
        """
        Test handling of multiple files with different error types.

        Validates: Requirements 4.4, 6.1, 6.2
        """
        source_dir = tmp_path / "docs"
        source_dir.mkdir()

        (source_dir / "success.md").write_text("# Success")
        (source_dir / "rate_limit.md").write_text("# Rate Limit")
        (source_dir / "api_error.md").write_text("# API Error")
        (source_dir / "another_success.md").write_text("# Another Success")

        # Mock API client with different errors for different files
        mock_api_client = Mock(spec=GeminiAPIClient)
        call_count = 0

        def mock_translate(text, **kwargs):
            nonlocal call_count
            call_count += 1

            if "Rate Limit" in text:
                raise RateLimitError("Rate limit exceeded")
            elif "API Error" in text:
                raise APIError("API connection failed")
            else:
                return f"[翻訳済み] {text}"

        mock_api_client.translate_text.side_effect = mock_translate

        # Initialize and execute
        file_service = FileSystemService()
        translation_service = TranslationService(mock_api_client)
        orchestrator = TranslationOrchestrator(file_service, translation_service)

        results = orchestrator.translate_directory(source_dir)

        # Verify all files were attempted
        assert len(results) == 4

        # Verify correct success/failure counts
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        assert len(successful) == 2
        assert len(failed) == 2

        # Verify error messages are captured
        error_messages = [r.error_message for r in failed]
        assert any("Rate limit" in msg for msg in error_messages)
        assert any("API connection" in msg for msg in error_messages)

    def test_invalid_directory_structure_handling(self, tmp_path):
        """
        Test handling of invalid directory structures.

        Validates: Requirements 1.2, 1.3
        """
        # Test with non-existent directory
        non_existent = tmp_path / "does_not_exist"

        mock_api_client = Mock(spec=GeminiAPIClient)
        file_service = FileSystemService()
        translation_service = TranslationService(mock_api_client)
        orchestrator = TranslationOrchestrator(file_service, translation_service)

        # Should handle gracefully and return empty results
        results = orchestrator.translate_directory(non_existent)
        assert len(results) == 0

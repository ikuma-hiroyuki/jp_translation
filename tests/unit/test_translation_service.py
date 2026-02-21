"""Unit tests for TranslationService."""

import pytest
from unittest.mock import Mock, MagicMock
from src.translation_service import TranslationService
from src.exceptions import TranslationError


class TestTranslationService:
    """Test suite for TranslationService."""

    @pytest.fixture
    def mock_api_client(self):
        """Create a mock API client."""
        mock = Mock()
        mock.translate_text = Mock(return_value="翻訳されたテキスト")
        return mock

    @pytest.fixture
    def translation_service(self, mock_api_client):
        """Create a TranslationService instance with mock API client."""
        return TranslationService(mock_api_client)

    def test_init(self, mock_api_client):
        """Test TranslationService initialization."""
        service = TranslationService(mock_api_client)
        assert service.api_client == mock_api_client

    def test_translate_markdown_empty_content(self, translation_service):
        """Test translating empty content returns empty string."""
        assert translation_service.translate_markdown("") == ""
        assert translation_service.translate_markdown("   ") == "   "

    def test_translate_markdown_simple_content(self, translation_service, mock_api_client):
        """Test translating simple markdown content."""
        content = "# Hello World\n\nThis is a test."
        mock_api_client.translate_text.return_value = "# こんにちは世界\n\nこれはテストです。"

        result = translation_service.translate_markdown(content)

        assert result == "# こんにちは世界\n\nこれはテストです。"
        mock_api_client.translate_text.assert_called_once_with(
            content,
            target_language="Japanese"
        )

    def test_translate_markdown_with_footnotes(self, translation_service, mock_api_client):
        """Test translating markdown with footnotes preserves footnotes."""
        content = """# Title

Some text with a footnote[^1].

[^1]: This is a footnote."""

        # Mock the API to return translated content (without the footnote definition)
        mock_api_client.translate_text.return_value = """# タイトル

脚注付きのテキスト[^1]。

__FOOTNOTE_0__"""

        result = translation_service.translate_markdown(content)

        # The footnote should be preserved in the original language
        assert "[^1]: This is a footnote." in result
        assert "タイトル" in result

    def test_translate_markdown_api_error(self, translation_service, mock_api_client):
        """Test that API errors are wrapped in TranslationError."""
        mock_api_client.translate_text.side_effect = Exception("API error")

        with pytest.raises(TranslationError) as exc_info:
            translation_service.translate_markdown("# Test")

        assert "Failed to translate markdown" in str(exc_info.value)

    def test_preprocess_markdown_no_footnotes(self, translation_service):
        """Test preprocessing markdown without footnotes."""
        content = "# Title\n\nSome text."
        processed, footnotes = translation_service.preprocess_markdown(content)

        assert processed == content
        assert footnotes == []

    def test_preprocess_markdown_single_footnote(self, translation_service):
        """Test preprocessing markdown with a single footnote."""
        content = """# Title

Text with footnote[^1].

[^1]: Footnote text."""

        processed, footnotes = translation_service.preprocess_markdown(content)

        assert len(footnotes) == 1
        assert footnotes[0] == "[^1]: Footnote text."
        assert "__FOOTNOTE_0__" in processed
        assert "[^1]: Footnote text." not in processed

    def test_preprocess_markdown_multiple_footnotes(self, translation_service):
        """Test preprocessing markdown with multiple footnotes."""
        content = """# Title

Text with footnote[^1] and another[^note].

[^1]: First footnote.
[^note]: Second footnote."""

        processed, footnotes = translation_service.preprocess_markdown(content)

        assert len(footnotes) == 2
        assert footnotes[0] == "[^1]: First footnote."
        assert footnotes[1] == "[^note]: Second footnote."
        assert "__FOOTNOTE_0__" in processed
        assert "__FOOTNOTE_1__" in processed

    def test_preprocess_markdown_multiline_footnote(self, translation_service):
        """Test preprocessing markdown with multiline footnote."""
        content = """# Title

Text[^1].

[^1]: First line.
    Second line indented."""

        processed, footnotes = translation_service.preprocess_markdown(content)

        assert len(footnotes) == 1
        assert "First line.\n    Second line indented." in footnotes[0]
        assert "__FOOTNOTE_0__" in processed

    def test_postprocess_markdown_no_footnotes(self, translation_service):
        """Test postprocessing without footnotes."""
        content = "# Translated Title"
        result = translation_service.postprocess_markdown(content, [])

        assert result == content

    def test_postprocess_markdown_restore_footnotes(self, translation_service):
        """Test postprocessing restores footnotes."""
        translated = """# タイトル

テキスト[^1]。

__FOOTNOTE_0__"""
        footnotes = ["[^1]: Original footnote."]

        result = translation_service.postprocess_markdown(translated, footnotes)

        assert "[^1]: Original footnote." in result
        assert "__FOOTNOTE_0__" not in result

    def test_postprocess_markdown_multiple_footnotes(self, translation_service):
        """Test postprocessing restores multiple footnotes."""
        translated = """# タイトル

__FOOTNOTE_0__
__FOOTNOTE_1__"""
        footnotes = ["[^1]: First.", "[^2]: Second."]

        result = translation_service.postprocess_markdown(translated, footnotes)

        assert "[^1]: First." in result
        assert "[^2]: Second." in result
        assert "__FOOTNOTE_0__" not in result
        assert "__FOOTNOTE_1__" not in result

    def test_translate_markdown_empty_content_only(self, translation_service):
        """Test translating content with only footnotes."""
        content = "[^1]: Just a footnote."

        processed, footnotes = translation_service.preprocess_markdown(content)

        assert len(footnotes) == 1
        assert footnotes[0] == "[^1]: Just a footnote."

"""Unit tests for GeminiAPIClient."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.api_client import GeminiAPIClient
from src.exceptions import APIError, RateLimitError


class TestGeminiAPIClientInit:
    """Tests for GeminiAPIClient initialization."""

    def test_init_with_valid_api_key(self):
        """Test initialization with a valid API key."""
        with patch('src.api_client.genai.Client') as mock_client:
            client = GeminiAPIClient("valid_api_key_123")
            mock_client.assert_called_once_with(api_key="valid_api_key_123")

    def test_init_with_custom_retry_params(self):
        """Test initialization with custom retry parameters."""
        with patch('src.api_client.genai.Client'):
            client = GeminiAPIClient(
                "test_key",
                max_retries=5,
                retry_delay=2.0,
                rate_limit_wait=120.0
            )
            assert client.max_retries == 5
            assert client.retry_delay == 2.0
            assert client.rate_limit_wait == 120.0

    def test_init_with_empty_string(self):
        """Test initialization with empty string raises ValueError."""
        with pytest.raises(ValueError, match="API key must be a non-empty string"):
            GeminiAPIClient("")

    def test_init_with_whitespace_only(self):
        """Test initialization with whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="API key must be a non-empty string"):
            GeminiAPIClient("   ")

    def test_init_with_none(self):
        """Test initialization with None raises ValueError."""
        with pytest.raises(ValueError, match="API key must be a non-empty string"):
            GeminiAPIClient(None)

    def test_init_strips_whitespace(self):
        """Test that API key whitespace is stripped."""
        with patch('src.api_client.genai.Client') as mock_client:
            GeminiAPIClient("  api_key_with_spaces  ")
            mock_client.assert_called_once_with(api_key="api_key_with_spaces")


class TestTranslateText:
    """Tests for translate_text method."""

    def test_translate_text_success(self):
        """Test successful text translation."""
        with patch('src.api_client.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = "翻訳されたテキスト"
            mock_client.models.generate_content.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = GeminiAPIClient("test_key")
            result = client.translate_text("Hello world")

            assert result == "翻訳されたテキスト"
            mock_client.models.generate_content.assert_called_once()

    def test_translate_empty_text(self):
        """Test translating empty text returns empty text."""
        with patch('src.api_client.genai.Client'):
            client = GeminiAPIClient("test_key")
            result = client.translate_text("")
            assert result == ""

    def test_translate_whitespace_only(self):
        """Test translating whitespace-only text returns original."""
        with patch('src.api_client.genai.Client'):
            client = GeminiAPIClient("test_key")
            result = client.translate_text("   ")
            assert result == "   "

    def test_translate_text_api_error(self):
        """Test API error handling."""
        with patch('src.api_client.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_client.models.generate_content.side_effect = Exception("API connection failed")
            mock_client_class.return_value = mock_client

            client = GeminiAPIClient("test_key")

            with pytest.raises(APIError, match="API call failed"):
                client.translate_text("Hello")

    def test_translate_text_rate_limit_error_quota(self):
        """Test rate limit error with 'quota' in message."""
        with patch('src.api_client.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_client.models.generate_content.side_effect = Exception("Quota exceeded")
            mock_client_class.return_value = mock_client

            client = GeminiAPIClient("test_key")

            with pytest.raises(RateLimitError, match="API rate limit reached"):
                client.translate_text("Hello")

    def test_translate_text_rate_limit_error_429(self):
        """Test rate limit error with '429' in message."""
        with patch('src.api_client.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_client.models.generate_content.side_effect = Exception("HTTP 429 error")
            mock_client_class.return_value = mock_client

            client = GeminiAPIClient("test_key")

            with pytest.raises(RateLimitError, match="API rate limit reached"):
                client.translate_text("Hello")

    def test_translate_text_rate_limit_resource_exhausted(self):
        """Test rate limit error with 'resource exhausted' in message."""
        with patch('src.api_client.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_client.models.generate_content.side_effect = Exception("Resource exhausted")
            mock_client_class.return_value = mock_client

            client = GeminiAPIClient("test_key")

            with pytest.raises(RateLimitError, match="API rate limit reached"):
                client.translate_text("Hello")

    def test_translate_text_empty_response(self):
        """Test handling of empty API response."""
        with patch('src.api_client.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = ""
            mock_client.models.generate_content.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = GeminiAPIClient("test_key")

            with pytest.raises(APIError, match="API returned empty response"):
                client.translate_text("Hello")

    def test_translate_text_retry_on_api_error(self):
        """Test retry logic on API error."""
        with patch('src.api_client.genai.Client') as mock_client_class:
            mock_client = Mock()
            # Fail twice, then succeed
            mock_response = Mock()
            mock_response.text = "Success"
            mock_client.models.generate_content.side_effect = [
                Exception("Temporary error"),
                Exception("Temporary error"),
                mock_response
            ]
            mock_client_class.return_value = mock_client

            client = GeminiAPIClient("test_key", retry_delay=0.01)
            result = client.translate_text("Hello")

            assert result == "Success"
            assert mock_client.models.generate_content.call_count == 3

    def test_translate_text_retry_exhausted(self):
        """Test that retries are exhausted after max attempts."""
        with patch('src.api_client.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_client.models.generate_content.side_effect = Exception("Persistent error")
            mock_client_class.return_value = mock_client

            client = GeminiAPIClient("test_key", max_retries=3, retry_delay=0.01)

            with pytest.raises(APIError):
                client.translate_text("Hello")

            assert mock_client.models.generate_content.call_count == 3

    def test_translate_text_rate_limit_retry(self):
        """Test retry logic on rate limit error."""
        with patch('src.api_client.genai.Client') as mock_client_class:
            mock_client = Mock()
            # Fail with rate limit, then succeed
            mock_response = Mock()
            mock_response.text = "Success"
            mock_client.models.generate_content.side_effect = [
                Exception("Quota exceeded"),
                mock_response
            ]
            mock_client_class.return_value = mock_client

            client = GeminiAPIClient("test_key", rate_limit_wait=0.01)
            result = client.translate_text("Hello")

            assert result == "Success"
            assert mock_client.models.generate_content.call_count == 2

    def test_translate_text_rate_limit_exhausted(self):
        """Test that rate limit retries are exhausted."""
        with patch('src.api_client.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_client.models.generate_content.side_effect = Exception("Quota exceeded")
            mock_client_class.return_value = mock_client

            client = GeminiAPIClient("test_key", max_retries=2, rate_limit_wait=0.01)

            with pytest.raises(RateLimitError):
                client.translate_text("Hello")

            assert mock_client.models.generate_content.call_count == 2


class TestLoadApiKeyFromEnv:
    """Tests for load_api_key_from_env static method."""

    def test_load_api_key_success(self, tmp_path):
        """Test successful API key loading."""
        env_file = tmp_path / ".env"
        env_file.write_text("key=my_secret_api_key_123")

        api_key = GeminiAPIClient.load_api_key_from_env(env_file)
        assert api_key == "my_secret_api_key_123"

    def test_load_api_key_with_double_quotes(self, tmp_path):
        """Test loading API key with double quotes."""
        env_file = tmp_path / ".env"
        env_file.write_text('key="my_api_key"')

        api_key = GeminiAPIClient.load_api_key_from_env(env_file)
        assert api_key == "my_api_key"

    def test_load_api_key_with_single_quotes(self, tmp_path):
        """Test loading API key with single quotes."""
        env_file = tmp_path / ".env"
        env_file.write_text("key='my_api_key'")

        api_key = GeminiAPIClient.load_api_key_from_env(env_file)
        assert api_key == "my_api_key"

    def test_load_api_key_with_comments(self, tmp_path):
        """Test loading API key from file with comments."""
        env_file = tmp_path / ".env"
        env_file.write_text("# This is a comment\nkey=my_api_key\n# Another comment")

        api_key = GeminiAPIClient.load_api_key_from_env(env_file)
        assert api_key == "my_api_key"

    def test_load_api_key_with_empty_lines(self, tmp_path):
        """Test loading API key from file with empty lines."""
        env_file = tmp_path / ".env"
        env_file.write_text("\n\nkey=my_api_key\n\n")

        api_key = GeminiAPIClient.load_api_key_from_env(env_file)
        assert api_key == "my_api_key"

    def test_load_api_key_file_not_found(self, tmp_path):
        """Test FileNotFoundError when .env file doesn't exist."""
        env_file = tmp_path / "nonexistent.env"

        with pytest.raises(FileNotFoundError, match=".env file not found"):
            GeminiAPIClient.load_api_key_from_env(env_file)

    def test_load_api_key_not_found_in_file(self, tmp_path):
        """Test ValueError when API key is not in .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("OTHER_VAR=value\nANOTHER_VAR=value2")

        with pytest.raises(ValueError, match="API key not found in .env file"):
            GeminiAPIClient.load_api_key_from_env(env_file)

    def test_load_api_key_empty_value(self, tmp_path):
        """Test ValueError when API key value is empty."""
        env_file = tmp_path / ".env"
        env_file.write_text("key=")

        with pytest.raises(ValueError, match="API key value is empty"):
            GeminiAPIClient.load_api_key_from_env(env_file)

    def test_load_api_key_empty_quotes(self, tmp_path):
        """Test ValueError when API key is empty quotes."""
        env_file = tmp_path / ".env"
        env_file.write_text('key=""')

        with pytest.raises(ValueError, match="API key value is empty"):
            GeminiAPIClient.load_api_key_from_env(env_file)

    def test_load_api_key_path_is_directory(self, tmp_path):
        """Test ValueError when path is a directory."""
        with pytest.raises(ValueError, match="Path is not a file"):
            GeminiAPIClient.load_api_key_from_env(tmp_path)

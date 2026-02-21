"""GCP Gemini API client for text translation."""

from pathlib import Path
import time
import os
from google import genai
from .exceptions import APIError, RateLimitError


class GeminiAPIClient:
    """GCP Gemini API client for translating text."""

    def __init__(
        self,
        api_key: str,
        model_name: str = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        rate_limit_wait: float = 60.0
    ):
        """
        Initialize the API client.

        Args:
            api_key: GCP API key
            model_name: Model name to use (default: from GEMINI_MODEL env var or "gemini-3-flash-preview")
            max_retries: Maximum number of retries for transient errors (default: 3)
            retry_delay: Initial retry delay in seconds for exponential backoff (default: 1.0)
            rate_limit_wait: Wait time in seconds for rate limit errors (default: 60.0)

        Raises:
            ValueError: If API key is invalid or empty
        """
        if not api_key or not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("API key must be a non-empty string")

        try:
            self.client = genai.Client(api_key=api_key.strip())
            # Allow model name override via parameter, env var, or default
            self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
            self.max_retries = max_retries
            self.retry_delay = retry_delay
            self.rate_limit_wait = rate_limit_wait
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini API client: {e}")

    def translate_text(
        self,
        text: str,
        target_language: str = "Japanese"
    ) -> str:
        """
        Translate text to the target language with retry logic.

        Args:
            text: Text to translate
            target_language: Target language (default: Japanese)

        Returns:
            str: Translated text

        Raises:
            APIError: If API call fails after all retries
            RateLimitError: If rate limit is reached after all retries
        """
        if not text or not text.strip():
            return text

        prompt = f"Translate the following text to {target_language}. Preserve all Markdown formatting exactly as it appears. Only return the translated text without any additional explanation:\n\n{text}"

        last_exception = None

        for attempt in range(self.max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )

                if not response or not response.text:
                    raise APIError("API returned empty response")

                return response.text.strip()

            except RateLimitError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    print(f"[WARNING] Rate limit reached. Waiting {self.rate_limit_wait} seconds before retry (attempt {attempt + 1}/{self.max_retries})...")
                    time.sleep(self.rate_limit_wait)
                else:
                    print(f"[ERROR] Rate limit reached. Max retries ({self.max_retries}) exceeded.")
                    raise

            except APIError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = self.retry_delay * (2 ** attempt)
                    print(f"[WARNING] API error occurred. Retrying in {wait_time} seconds (attempt {attempt + 1}/{self.max_retries})...")
                    time.sleep(wait_time)
                else:
                    print(f"[ERROR] API error occurred. Max retries ({self.max_retries}) exceeded.")
                    raise

            except Exception as e:
                error_message = str(e).lower()

                # Check for rate limit errors
                if "quota" in error_message or "rate limit" in error_message or "429" in error_message:
                    last_exception = RateLimitError(f"API rate limit reached: {e}")
                    if attempt < self.max_retries - 1:
                        print(f"[WARNING] Rate limit reached. Waiting {self.rate_limit_wait} seconds before retry (attempt {attempt + 1}/{self.max_retries})...")
                        time.sleep(self.rate_limit_wait)
                    else:
                        print(f"[ERROR] Rate limit reached. Max retries ({self.max_retries}) exceeded.")
                        raise last_exception

                # Check for resource exhausted errors (also rate limiting)
                elif "resource exhausted" in error_message or "resource_exhausted" in error_message:
                    last_exception = RateLimitError(f"API rate limit reached: {e}")
                    if attempt < self.max_retries - 1:
                        print(f"[WARNING] Rate limit reached. Waiting {self.rate_limit_wait} seconds before retry (attempt {attempt + 1}/{self.max_retries})...")
                        time.sleep(self.rate_limit_wait)
                    else:
                        print(f"[ERROR] Rate limit reached. Max retries ({self.max_retries}) exceeded.")
                        raise last_exception

                # All other errors are generic API errors with exponential backoff
                else:
                    last_exception = APIError(f"API call failed: {e}")
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)
                        print(f"[WARNING] API error occurred. Retrying in {wait_time} seconds (attempt {attempt + 1}/{self.max_retries})...")
                        time.sleep(wait_time)
                    else:
                        print(f"[ERROR] API error occurred. Max retries ({self.max_retries}) exceeded.")
                        raise last_exception

        # This should not be reached, but just in case
        if last_exception:
            raise last_exception
        raise APIError("Translation failed after all retries")

    @staticmethod
    def load_api_key_from_env(env_file: Path = Path(".env")) -> str:
        """
        Load API key from .env file.

        Args:
            env_file: Path to .env file (default: .env in current directory)

        Returns:
            str: API key

        Raises:
            FileNotFoundError: If .env file does not exist
            ValueError: If API key is not found in .env file
        """
        if not env_file.exists():
            raise FileNotFoundError(f".env file not found: {env_file}")

        if not env_file.is_file():
            raise ValueError(f"Path is not a file: {env_file}")

        try:
            content = env_file.read_text(encoding="utf-8")
        except Exception as e:
            raise ValueError(f"Failed to read .env file: {e}")

        # Parse the .env file looking for "key=" format
        for line in content.splitlines():
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Look for "key=" format
            if line.startswith("key="):
                api_key = line[4:].strip()  # Extract everything after "key="

                # Remove quotes if present
                if api_key.startswith('"') and api_key.endswith('"'):
                    api_key = api_key[1:-1]
                elif api_key.startswith("'") and api_key.endswith("'"):
                    api_key = api_key[1:-1]

                if api_key:
                    return api_key
                else:
                    raise ValueError("API key value is empty in .env file")

        raise ValueError("API key not found in .env file (expected format: key=<your_api_key>)")

"""Translation service for Markdown content."""

import re
from .api_client import GeminiAPIClient
from .exceptions import TranslationError


class TranslationService:
    """Service for translating Markdown content while preserving formatting."""

    def __init__(self, api_client: GeminiAPIClient):
        """
        Initialize the translation service.

        Args:
            api_client: GeminiAPIClient instance for translation
        """
        self.api_client = api_client

    def translate_markdown(self, content: str) -> str:
        """
        Translate Markdown content to Japanese.

        Args:
            content: Markdown content to translate

        Returns:
            str: Translated Markdown content

        Raises:
            TranslationError: If translation fails
        """
        if not content or not content.strip():
            return content

        try:
            # Step 1: Preprocess - extract footnotes
            processed_content, footnotes = self.preprocess_markdown(content)

            # Step 2: Translate the processed content
            translated_content = self.api_client.translate_text(
                processed_content,
                target_language="Japanese"
            )

            # Step 3: Postprocess - restore footnotes
            final_content = self.postprocess_markdown(translated_content, footnotes)

            return final_content

        except Exception as e:
            raise TranslationError(f"Failed to translate markdown: {e}")

    def preprocess_markdown(self, content: str) -> tuple[str, list[str]]:
        """
        Preprocess Markdown content by extracting footnotes.

        Footnotes are identified by patterns like [^1], [^note], etc.
        and their definitions like [^1]: footnote text.

        Args:
            content: Markdown content to preprocess

        Returns:
            tuple[str, list[str]]: (processed content, extracted footnotes)
        """
        footnotes = []

        # Pattern to match footnote definitions: [^id]: text
        # This matches from [^...]: to the end of the line or until a blank line
        footnote_def_pattern = r'^\[\^[^\]]+\]:\s*.+$'

        lines = content.split('\n')
        processed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check if this line is a footnote definition
            if re.match(footnote_def_pattern, line.strip()):
                # Collect the footnote definition (may span multiple lines)
                footnote_lines = [line]
                i += 1

                # Continue collecting lines that are part of the footnote
                # (indented lines or lines that continue the definition)
                while i < len(lines):
                    next_line = lines[i]

                    # If the next line is empty, it marks the end of the footnote
                    if not next_line.strip():
                        break

                    # If the next line starts with a new footnote definition, stop
                    if re.match(footnote_def_pattern, next_line.strip()):
                        break

                    # If the line is indented (part of the footnote), include it
                    if next_line.startswith('    ') or next_line.startswith('\t'):
                        footnote_lines.append(next_line)
                        i += 1
                    else:
                        # Not part of the footnote anymore
                        break

                # Store the complete footnote
                footnote_text = '\n'.join(footnote_lines)
                footnotes.append(footnote_text)

                # Replace with a placeholder
                placeholder = f"__FOOTNOTE_{len(footnotes) - 1}__"
                processed_lines.append(placeholder)
            else:
                processed_lines.append(line)
                i += 1

        processed_content = '\n'.join(processed_lines)
        return processed_content, footnotes

    def postprocess_markdown(
        self,
        translated_content: str,
        footnotes: list[str]
    ) -> str:
        """
        Postprocess translated Markdown by restoring footnotes.

        Args:
            translated_content: Translated Markdown content
            footnotes: List of footnotes to restore

        Returns:
            str: Markdown content with footnotes restored
        """
        if not footnotes:
            return translated_content

        result = translated_content

        # Replace placeholders with original footnotes
        for i, footnote in enumerate(footnotes):
            placeholder = f"__FOOTNOTE_{i}__"
            result = result.replace(placeholder, footnote)

        return result

"""File system operations for the Markdown Translator application."""

from pathlib import Path
from .exceptions import FileSystemError


class FileSystemService:
    """Service for file system operations."""

    def find_markdown_files(self, directory: Path) -> list[Path]:
        """
        Recursively find all Markdown files in a directory.

        Args:
            directory: Directory to search

        Returns:
            list[Path]: List of Markdown file paths

        Raises:
            FileSystemError: If directory access fails
        """
        if not directory.exists():
            raise FileSystemError(f"Directory does not exist: {directory}")

        if not directory.is_dir():
            raise FileSystemError(f"Path is not a directory: {directory}")

        try:
            # Use rglob to recursively find all .md files
            markdown_files = list(directory.rglob("*.md"))
            return sorted(markdown_files)  # Sort for consistent ordering
        except Exception as e:
            raise FileSystemError(f"Failed to scan directory {directory}: {e}")

    def read_file(self, file_path: Path) -> str:
        """
        Read file content.

        Args:
            file_path: Path to file to read

        Returns:
            str: File content

        Raises:
            IOError: If file read fails
        """
        if not file_path.exists():
            raise IOError(f"File does not exist: {file_path}")

        if not file_path.is_file():
            raise IOError(f"Path is not a file: {file_path}")

        try:
            return file_path.read_text(encoding="utf-8")
        except Exception as e:
            raise IOError(f"Failed to read file {file_path}: {e}")

    def write_file(self, file_path: Path, content: str) -> None:
        """
        Write content to file.

        Args:
            file_path: Path to file to write
            content: Content to write

        Raises:
            IOError: If file write fails
        """
        try:
            # Ensure parent directory exists
            self.ensure_directory_exists(file_path.parent)

            # Write the file
            file_path.write_text(content, encoding="utf-8")
        except Exception as e:
            raise IOError(f"Failed to write file {file_path}: {e}")

    def create_output_path(
        self,
        source_file: Path,
        source_dir: Path,
        output_dir_name: str = "jp"
    ) -> Path:
        """
        Create output file path preserving directory structure.

        Args:
            source_file: Source file path
            source_dir: Source directory path
            output_dir_name: Output directory name (default: "jp")

        Returns:
            Path: Output file path

        Example:
            source_file: /path/to/source/docs/guide.md
            source_dir: /path/to/source
            output_dir_name: jp
            result: /path/to/source/jp/docs/guide.md
        """
        # Get relative path from source directory
        try:
            relative_path = source_file.relative_to(source_dir)
        except ValueError:
            # If source_file is not relative to source_dir, just use the filename
            relative_path = source_file.name

        # Create output path: source_dir / output_dir_name / relative_path
        output_path = source_dir / output_dir_name / relative_path

        return output_path

    def ensure_directory_exists(self, directory: Path) -> None:
        """
        Ensure directory exists, creating it if necessary.

        Args:
            directory: Directory to ensure exists

        Raises:
            FileSystemError: If directory creation fails
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise FileSystemError(f"Failed to create directory {directory}: {e}")

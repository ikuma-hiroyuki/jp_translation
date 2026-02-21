"""Unit tests for FileSystemService."""

import pytest
from pathlib import Path
from src.file_service import FileSystemService
from src.exceptions import FileSystemError


class TestFileSystemService:
    """Test suite for FileSystemService."""

    @pytest.fixture
    def service(self):
        """Create a FileSystemService instance."""
        return FileSystemService()

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory with test files."""
        # Create directory structure
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "nested").mkdir()

        # Create markdown files
        (tmp_path / "README.md").write_text("# Root README")
        (tmp_path / "docs" / "guide.md").write_text("# Guide")
        (tmp_path / "docs" / "nested" / "deep.md").write_text("# Deep")

        # Create non-markdown file
        (tmp_path / "test.txt").write_text("Not markdown")

        return tmp_path

    def test_find_markdown_files_success(self, service, temp_dir):
        """Test finding markdown files in a directory."""
        files = service.find_markdown_files(temp_dir)

        assert len(files) == 3
        assert all(f.suffix == ".md" for f in files)
        assert any(f.name == "README.md" for f in files)
        assert any(f.name == "guide.md" for f in files)
        assert any(f.name == "deep.md" for f in files)

    def test_find_markdown_files_nonexistent_directory(self, service):
        """Test finding files in non-existent directory raises error."""
        with pytest.raises(FileSystemError, match="does not exist"):
            service.find_markdown_files(Path("/nonexistent/path"))

    def test_find_markdown_files_not_a_directory(self, service, tmp_path):
        """Test finding files when path is not a directory."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("test")

        with pytest.raises(FileSystemError, match="not a directory"):
            service.find_markdown_files(file_path)

    def test_find_markdown_files_empty_directory(self, service, tmp_path):
        """Test finding files in empty directory returns empty list."""
        files = service.find_markdown_files(tmp_path)
        assert files == []

    def test_read_file_success(self, service, tmp_path):
        """Test reading file content."""
        file_path = tmp_path / "test.md"
        content = "# Test Content"
        file_path.write_text(content)

        result = service.read_file(file_path)
        assert result == content

    def test_read_file_nonexistent(self, service):
        """Test reading non-existent file raises error."""
        with pytest.raises(IOError, match="does not exist"):
            service.read_file(Path("/nonexistent/file.md"))

    def test_read_file_not_a_file(self, service, tmp_path):
        """Test reading directory as file raises error."""
        with pytest.raises(IOError, match="not a file"):
            service.read_file(tmp_path)

    def test_write_file_success(self, service, tmp_path):
        """Test writing file content."""
        file_path = tmp_path / "output.md"
        content = "# Output Content"

        service.write_file(file_path, content)

        assert file_path.exists()
        assert file_path.read_text() == content

    def test_write_file_creates_parent_directories(self, service, tmp_path):
        """Test writing file creates parent directories."""
        file_path = tmp_path / "nested" / "deep" / "output.md"
        content = "# Deep Output"

        service.write_file(file_path, content)

        assert file_path.exists()
        assert file_path.read_text() == content

    def test_create_output_path_preserves_structure(self, service, tmp_path):
        """Test output path preserves directory structure."""
        source_dir = tmp_path / "source"
        source_file = source_dir / "docs" / "guide.md"

        output_path = service.create_output_path(source_file, source_dir, "jp")

        expected = source_dir / "jp" / "docs" / "guide.md"
        assert output_path == expected

    def test_create_output_path_root_file(self, service, tmp_path):
        """Test output path for file in root directory."""
        source_dir = tmp_path
        source_file = source_dir / "README.md"

        output_path = service.create_output_path(source_file, source_dir, "jp")

        expected = source_dir / "jp" / "README.md"
        assert output_path == expected

    def test_create_output_path_custom_output_dir(self, service, tmp_path):
        """Test output path with custom output directory name."""
        source_dir = tmp_path
        source_file = source_dir / "test.md"

        output_path = service.create_output_path(source_file, source_dir, "translated")

        expected = source_dir / "translated" / "test.md"
        assert output_path == expected

    def test_ensure_directory_exists_creates_directory(self, service, tmp_path):
        """Test ensuring directory exists creates it."""
        new_dir = tmp_path / "new" / "nested" / "dir"

        service.ensure_directory_exists(new_dir)

        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_ensure_directory_exists_existing_directory(self, service, tmp_path):
        """Test ensuring existing directory exists doesn't raise error."""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        service.ensure_directory_exists(existing_dir)

        assert existing_dir.exists()
        assert existing_dir.is_dir()

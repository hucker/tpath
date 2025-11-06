"""Tests for the standalone matches() function."""

import tempfile
from pathlib import Path

import pytest

from tpath import TPath, matches


class TestMatchesFunction:
    """Tests for the standalone matches() function."""

    def test_basic_pattern_matching(self):
        """Test basic pattern matching functionality."""
        # Basic patterns
        assert matches("app.log", "*.log") is True
        assert matches("backup.zip", "*.log") is False
        assert matches("config.json", "*.json") is True

        # Multiple patterns (OR logic)
        assert matches("report.pdf", "*.pdf", "*.docx") is True
        assert matches("document.docx", "*.pdf", "*.docx") is True
        assert matches("image.jpg", "*.pdf", "*.docx") is False

    def test_wildcard_patterns(self):
        """Test various wildcard patterns."""
        # * wildcard
        assert matches("backup_2024.zip", "backup_*") is True
        assert matches("backup_2024.zip", "*2024*") is True
        assert matches("config.ini", "*config*") is True

        # ? wildcard
        assert matches("app.log", "app.???") is True
        assert matches("app.conf", "app.???") is False  # Too short

        # Character classes
        assert matches("data_2024.csv", "*202[3-4]*") is True
        assert matches("data_2025.csv", "*202[3-4]*") is False

    def test_case_sensitivity(self):
        """Test case-sensitive and case-insensitive matching."""
        # Case-sensitive (default)
        assert matches("IMAGE.JPG", "*.jpg") is False
        assert matches("image.jpg", "*.jpg") is True

        # Case-insensitive
        assert matches("IMAGE.JPG", "*.jpg", case_sensitive=False) is True
        assert matches("Debug.LOG", "*.log", case_sensitive=False) is True
        assert matches("CONFIG.INI", "*config*", case_sensitive=False) is True

    def test_full_path_matching(self):
        """Test matching against full path vs filename."""
        # Create a temporary file path
        with tempfile.NamedTemporaryFile(suffix=".log") as tmp:
            tmp_path = Path(tmp.name)

            # Match filename only (default)
            assert matches(tmp_path, "*.log", full_path=False) is True

            # Match full path
            full_pattern = f"*{tmp_path.parent.name}*"
            assert matches(tmp_path, full_pattern, full_path=True) is True
            assert matches(tmp_path, "*/nonexistent/*", full_path=True) is False

    def test_different_path_types(self):
        """Test that function works with different path types."""
        # String path
        assert matches("app.log", "*.log") is True

        # pathlib.Path
        path_obj = Path("config.json")
        assert matches(path_obj, "*.json") is True

        # TPath
        tpath_obj = TPath("backup.zip")
        assert matches(tpath_obj, "*.zip") is True

    def test_empty_patterns_error(self):
        """Test that providing no patterns raises an error."""
        with pytest.raises(ValueError, match="At least one pattern must be provided"):
            matches("app.log")

    def test_complex_patterns(self):
        """Test more complex pattern combinations."""
        # Multiple character classes
        assert matches("log_2024_01.txt", "*202[3-4]_[0-1][0-9]*") is True
        assert matches("log_2025_15.txt", "*202[3-4]_[0-1][0-9]*") is False

        # Negated character classes
        assert matches("file_a.txt", "file_[!0-9]*") is True
        assert matches("file_1.txt", "file_[!0-9]*") is False

        # Multiple wildcards
        assert matches("backup_app_2024.zip", "backup_*_*.zip") is True
        assert matches("backup_2024.zip", "backup_*_*.zip") is False

    def test_use_with_pquery(self):
        """Test using matches() function with PQuery."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "app.log").write_text("log content")
            (temp_path / "error.log").write_text("error log")
            (temp_path / "config.json").write_text("config")
            (temp_path / "backup.zip").write_text("backup")

            # Use matches function with PQuery
            from tpath import PQuery

            log_files = (
                PQuery()
                .from_(temp_path)
                .where(lambda p: matches(p, "*.log"))
                .files()
            )

            log_names = [f.name for f in log_files]
            assert "app.log" in log_names
            assert "error.log" in log_names
            assert len(log_names) == 2

            # Multiple patterns
            important_files = (
                PQuery()
                .from_(temp_path)
                .where(lambda p: matches(p, "*.log", "*.json"))
                .files()
            )

            important_names = [f.name for f in important_files]
            assert len(important_names) == 3  # 2 logs + 1 json

    def test_real_world_patterns(self):
        """Test patterns commonly used in real-world scenarios."""
        # Log files and rotated logs
        assert matches("app.log", "*.log", "*.[0-9]", "*.old") is True
        assert matches("app.log.1", "*.log", "*.[0-9]", "*.old") is True
        assert matches("app.old", "*.log", "*.[0-9]", "*.old") is True
        assert matches("app.txt", "*.log", "*.[0-9]", "*.old") is False

        # Backup files with dates
        assert matches("backup_2024_01_15.zip", "backup_*") is True
        assert matches("daily_backup_2024.tar.gz", "*backup*") is True

        # Configuration files
        assert matches("app.conf", "*.conf", "*.ini", "*config*") is True
        assert matches("settings.ini", "*.conf", "*.ini", "*config*") is True
        assert matches("myapp_config.json", "*.conf", "*.ini", "*config*") is True

        # Temporary files
        assert matches("temp_12345.tmp", "temp_*", "*.tmp", ".*") is True
        assert matches(".hidden_file", "temp_*", "*.tmp", ".*") is True

    def test_edge_cases(self):
        """Test edge cases and special characters."""
        # Empty filename
        empty_path = TPath("")
        assert matches(empty_path, "*") is True
        assert matches(empty_path, "*.log") is False

        # Special characters in patterns
        assert matches("file[1].txt", "file[[]1]*.txt") is True
        assert matches("file$.txt", "file$*.txt") is True

        # Unicode characters
        assert matches("файл.txt", "*.txt") is True
        assert matches("файл.log", "файл.*") is True
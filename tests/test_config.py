"""Tests for configuration management."""

import json
import os
import pytest
from pathlib import Path
from src.config import Config


class TestConfig:
    """Test cases for the Config class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        assert config.test_framework == "pytest"
        assert config.test_directory == "tests"
        assert config.coverage_threshold == 80.0
        assert config.verbose is False
        assert config.parallel is False

    def test_custom_config(self):
        """Test custom configuration values."""
        config = Config(
            test_framework="unittest",
            verbose=True,
            parallel=True,
            coverage_threshold=90.0
        )
        assert config.test_framework == "unittest"
        assert config.verbose is True
        assert config.parallel is True
        assert config.coverage_threshold == 90.0

    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = Config(verbose=True, parallel=True)
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict["verbose"] is True
        assert config_dict["parallel"] is True
        assert "test_framework" in config_dict

    def test_config_save_and_load(self, tmp_path):
        """Test saving and loading configuration."""
        config = Config(verbose=True, parallel=True, max_workers=8)
        config_file = tmp_path / "config.json"

        # Save config
        config.save(str(config_file))
        assert config_file.exists()

        # Load config
        loaded_config = Config.from_file(str(config_file))
        assert loaded_config.verbose is True
        assert loaded_config.parallel is True
        assert loaded_config.max_workers == 8

    def test_config_from_nonexistent_file(self):
        """Test loading config from non-existent file."""
        with pytest.raises(FileNotFoundError):
            Config.from_file("nonexistent_config.json")

    def test_config_from_env(self, monkeypatch):
        """Test loading configuration from environment variables."""
        monkeypatch.setenv("TEST_FRAMEWORK", "unittest")
        monkeypatch.setenv("VERBOSE", "true")
        monkeypatch.setenv("PARALLEL", "true")
        monkeypatch.setenv("COVERAGE_THRESHOLD", "85.0")

        config = Config.from_env()
        assert config.test_framework == "unittest"
        assert config.verbose is True
        assert config.parallel is True
        assert config.coverage_threshold == 85.0

    def test_config_save_creates_directory(self, tmp_path):
        """Test that save creates parent directories."""
        config = Config()
        nested_path = tmp_path / "nested" / "dir" / "config.json"

        config.save(str(nested_path))
        assert nested_path.exists()
        assert nested_path.parent.exists()

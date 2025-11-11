"""Configuration management for the testing agent."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Any


@dataclass
class Config:
    """Configuration for the testing agent."""

    test_framework: str = "pytest"
    test_directory: str = "tests"
    coverage_threshold: float = 80.0
    verbose: bool = False
    parallel: bool = False
    max_workers: int = 4
    timeout: int = 300
    fail_fast: bool = False
    generate_html_report: bool = True
    report_directory: str = "reports"
    extra_args: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """Load configuration from a JSON file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Config instance
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(path, "r") as f:
            data = json.load(f)

        return cls(**data)

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.

        Returns:
            Config instance with values from environment
        """
        return cls(
            test_framework=os.getenv("TEST_FRAMEWORK", "pytest"),
            test_directory=os.getenv("TEST_DIRECTORY", "tests"),
            coverage_threshold=float(os.getenv("COVERAGE_THRESHOLD", "80.0")),
            verbose=os.getenv("VERBOSE", "false").lower() == "true",
            parallel=os.getenv("PARALLEL", "false").lower() == "true",
            max_workers=int(os.getenv("MAX_WORKERS", "4")),
            timeout=int(os.getenv("TIMEOUT", "300")),
            fail_fast=os.getenv("FAIL_FAST", "false").lower() == "true",
            generate_html_report=os.getenv("GENERATE_HTML_REPORT", "true").lower()
            == "true",
            report_directory=os.getenv("REPORT_DIRECTORY", "reports"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            "test_framework": self.test_framework,
            "test_directory": self.test_directory,
            "coverage_threshold": self.coverage_threshold,
            "verbose": self.verbose,
            "parallel": self.parallel,
            "max_workers": self.max_workers,
            "timeout": self.timeout,
            "fail_fast": self.fail_fast,
            "generate_html_report": self.generate_html_report,
            "report_directory": self.report_directory,
            "extra_args": self.extra_args,
        }

    def save(self, config_path: str) -> None:
        """Save configuration to a JSON file.

        Args:
            config_path: Path where to save the configuration
        """
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

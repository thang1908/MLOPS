"""Small, explicit helpers for loading and validating YAML stage configuration."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml


class ConfigurationError(ValueError):
    """Raised when a pipeline configuration is missing or invalid."""


def load_config(config_path: Path) -> Mapping[str, Any]:
    """Load one YAML file and ensure its root is a mapping."""
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)
    except yaml.YAMLError as error:
        raise ConfigurationError(f"Invalid YAML in {config_path}: {error}") from error

    if not isinstance(config, Mapping):
        raise ConfigurationError("Configuration must be a YAML mapping.")
    return config


def require_section(config: Mapping[str, Any], section_name: str) -> Mapping[str, Any]:
    """Return a required named mapping from the top-level configuration."""
    section = config.get(section_name)
    if not isinstance(section, Mapping):
        raise ConfigurationError(f"Missing required '{section_name}' configuration section.")
    return section


def require_string(section: Mapping[str, Any], section_name: str, key: str) -> str:
    """Return a required, non-empty string from a configuration section."""
    value = section.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"'{section_name}.{key}' must be a non-empty string.")
    return value.strip()


def require_int(section: Mapping[str, Any], section_name: str, key: str) -> int:
    """Return a required integer (but never a boolean) from configuration."""
    value = section.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigurationError(f"'{section_name}.{key}' must be an integer.")
    return value


def require_positive_int(section: Mapping[str, Any], section_name: str, key: str) -> int:
    """Return a required positive integer from configuration."""
    value = require_int(section, section_name, key)
    if value <= 0:
        raise ConfigurationError(f"'{section_name}.{key}' must be a positive integer.")
    return value


def require_probability(section: Mapping[str, Any], section_name: str, key: str) -> float:
    """Return a numeric probability strictly between zero and one."""
    value = section.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 < value < 1:
        raise ConfigurationError(f"'{section_name}.{key}' must be between 0 and 1.")
    return float(value)


def resolve_config_path(value: str, config_dir: Path) -> Path:
    """Resolve a configured path relative to the YAML file's directory."""
    path = Path(value)
    return path if path.is_absolute() else config_dir / path

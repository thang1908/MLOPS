"""Train and persist a Logistic Regression model from configured artifacts."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import yaml
from scipy.sparse import csr_matrix, load_npz
from sklearn.linear_model import LogisticRegression

from src.logging_utils import get_logger


logger = get_logger("model_building")


class ConfigurationError(ValueError):
    """Raised when the model-building configuration is invalid."""


@dataclass(frozen=True)
class TrainingConfig:
    """Validated configuration required to train the classifier."""

    features_path: Path
    labels_path: Path
    model_path: Path
    label_column: str
    max_iter: int
    random_state: int


def parse_args() -> argparse.Namespace:
    """Parse the path to the YAML configuration file."""
    parser = argparse.ArgumentParser(
        description="Train Logistic Regression from configured TF-IDF artifacts."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("params.yaml"),
        help="Path to the YAML configuration file (default: params.yaml)",
    )
    return parser.parse_args()


def load_config(config_path: Path) -> Mapping[str, Any]:
    """Load one YAML configuration file and validate its top-level structure."""
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


def _required_string(config: Mapping[str, Any], key: str) -> str:
    """Return a required non-empty string value from a configuration section."""
    value = config.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"'model_building.{key}' must be a non-empty string.")
    return value.strip()


def _required_positive_int(config: Mapping[str, Any], key: str) -> int:
    """Return a required positive integer value from a configuration section."""
    value = config.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ConfigurationError(f"'model_building.{key}' must be a positive integer.")
    return value


def _required_int(config: Mapping[str, Any], key: str) -> int:
    """Return a required integer value from a configuration section."""
    value = config.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigurationError(f"'model_building.{key}' must be an integer.")
    return value


def build_training_config(config: Mapping[str, Any], config_dir: Path) -> TrainingConfig:
    """Extract and validate the ``model_building`` section from loaded config."""
    section = config.get("model_building")
    if not isinstance(section, Mapping):
        raise ConfigurationError("Missing required 'model_building' configuration section.")

    def resolve_path(value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else config_dir / path

    return TrainingConfig(
        features_path=resolve_path(_required_string(section, "features_path")),
        labels_path=resolve_path(_required_string(section, "labels_path")),
        model_path=resolve_path(_required_string(section, "model_path")),
        label_column=_required_string(section, "label_column"),
        max_iter=_required_positive_int(section, "max_iter"),
        random_state=_required_int(section, "random_state"),
    )


def load_training_data(
    features_path: Path, labels_path: Path, label_column: str
) -> tuple[csr_matrix, pd.Series]:
    """Load sparse TF-IDF features and their matching target labels."""
    if not features_path.is_file():
        raise FileNotFoundError(f"Feature matrix not found: {features_path}")
    if not labels_path.is_file():
        raise FileNotFoundError(f"Label CSV not found: {labels_path}")

    logger.info("Loading sparse train features from: %s", features_path)
    features = load_npz(features_path).tocsr()
    logger.info("Loaded feature matrix with shape %s", features.shape)

    logger.info("Loading training labels from: %s", labels_path)
    labels = pd.read_csv(labels_path)
    if label_column not in labels.columns:
        raise ValueError(f"Label column '{label_column}' was not found in {labels_path}.")

    targets = labels[label_column]
    if targets.isna().any():
        raise ValueError("Training labels contain missing values.")
    if features.shape[0] != len(targets):
        raise ValueError(
            "Feature and label row counts do not match: "
            f"{features.shape[0]} features, {len(targets)} labels."
        )
    if targets.nunique() < 2:
        raise ValueError("Training labels must contain at least two classes.")

    logger.info("Loaded %d labels across %d classes", len(targets), targets.nunique())
    return features, targets


def train_model(
    features: csr_matrix, targets: pd.Series, max_iter: int, random_state: int
) -> LogisticRegression:
    """Fit Logistic Regression with explicit, validated hyperparameters."""
    logger.info(
        "Training Logistic Regression (max_iter=%d, random_state=%d)",
        max_iter,
        random_state,
    )
    model = LogisticRegression(max_iter=max_iter, random_state=random_state)
    model.fit(features, targets)
    logger.info("Model training completed")
    return model


def save_model(model: LogisticRegression, model_path: Path) -> Path:
    """Persist a trained model, creating its parent directory if needed."""
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    logger.info("Trained model saved to: %s", model_path)
    return model_path


def main() -> int:
    """Load configuration once, train the model, and save the result."""
    args = parse_args()
    config_path = args.config.resolve()

    try:
        logger.info("Starting model building with config: %s", config_path)
        raw_config = load_config(config_path)
        training_config = build_training_config(raw_config, config_path.parent)
        features, targets = load_training_data(
            training_config.features_path,
            training_config.labels_path,
            training_config.label_column,
        )
        model = train_model(
            features,
            targets,
            training_config.max_iter,
            training_config.random_state,
        )
        destination = save_model(model, training_config.model_path)
    except (ConfigurationError, FileNotFoundError, OSError, ValueError) as error:
        logger.error("Model building failed: %s", error)
        return 1
    except Exception:
        logger.exception("Unexpected model-building failure")
        return 1

    logger.info("Model building finished successfully")
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

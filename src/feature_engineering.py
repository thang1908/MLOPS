"""Create TF-IDF train/test artifacts using parameters loaded once from YAML."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from scipy.sparse import csr_matrix, save_npz
from sklearn.feature_extraction.text import TfidfVectorizer

from src.config_utils import (
    ConfigurationError,
    load_config,
    require_positive_int,
    require_section,
    require_string,
    resolve_config_path,
)
from src.logging_utils import get_logger


logger = get_logger("feature_engineering")
STAGE_NAME = "feature_engineering"


@dataclass(frozen=True)
class FeatureConfig:
    """Validated parameters required for TF-IDF feature generation."""

    train_path: Path
    test_path: Path
    output_dir: Path
    text_column: str
    label_column: str
    max_features: int
    ngram_range: tuple[int, int]


def parse_args() -> argparse.Namespace:
    """Parse only the path to the pipeline YAML configuration."""
    parser = argparse.ArgumentParser(description="Create configured TF-IDF features.")
    parser.add_argument("--config", type=Path, default=Path("params.yaml"))
    return parser.parse_args()


def build_feature_config(config: Mapping[str, Any], config_dir: Path) -> FeatureConfig:
    """Extract and validate the feature-engineering section of loaded YAML."""
    section = require_section(config, STAGE_NAME)
    raw_ngram_range = section.get("ngram_range")
    if (
        not isinstance(raw_ngram_range, list)
        or len(raw_ngram_range) != 2
        or any(isinstance(value, bool) or not isinstance(value, int) for value in raw_ngram_range)
        or raw_ngram_range[0] < 1
        or raw_ngram_range[1] < raw_ngram_range[0]
    ):
        raise ConfigurationError(
            "'feature_engineering.ngram_range' must be a two-item integer list, "
            "for example [1, 2]."
        )

    def configured_path(key: str) -> Path:
        return resolve_config_path(require_string(section, STAGE_NAME, key), config_dir)

    return FeatureConfig(
        train_path=configured_path("train_path"),
        test_path=configured_path("test_path"),
        output_dir=configured_path("output_dir"),
        text_column=require_string(section, STAGE_NAME, "text_column"),
        label_column=require_string(section, STAGE_NAME, "label_column"),
        max_features=require_positive_int(section, STAGE_NAME, "max_features"),
        ngram_range=(raw_ngram_range[0], raw_ngram_range[1]),
    )


def load_processed_data(input_path: Path, label_column: str, text_column: str) -> pd.DataFrame:
    """Load and validate one processed CSV required by the feature stage."""
    if not input_path.is_file():
        raise FileNotFoundError(f"Processed CSV not found: {input_path}")
    logger.info("Reading processed CSV: %s", input_path)
    dataframe = pd.read_csv(input_path)
    required_columns = {label_column, text_column}
    missing_columns = required_columns - set(dataframe.columns)
    if missing_columns:
        raise ValueError(f"Processed CSV is missing required columns: {sorted(missing_columns)}")
    if dataframe.empty:
        raise ValueError(f"Processed CSV has no rows: {input_path}")
    return dataframe


def create_features(
    train_data: pd.DataFrame, test_data: pd.DataFrame, config: FeatureConfig
) -> tuple[csr_matrix, csr_matrix, TfidfVectorizer]:
    """Fit TF-IDF on train text only and transform both train and test text."""
    logger.info(
        "Fitting TF-IDF (max_features=%d, ngram_range=%s)",
        config.max_features,
        config.ngram_range,
    )
    vectorizer = TfidfVectorizer(
        max_features=config.max_features,
        ngram_range=config.ngram_range,
    )
    x_train = vectorizer.fit_transform(train_data[config.text_column].fillna("")).tocsr()
    x_test = vectorizer.transform(test_data[config.text_column].fillna("")).tocsr()
    if x_train.shape[1] == 0:
        raise ValueError("TF-IDF produced no features from the training text.")
    logger.info("Created %d TF-IDF features", x_train.shape[1])
    return x_train, x_test, vectorizer


def save_feature_artifacts(
    x_train: csr_matrix,
    x_test: csr_matrix,
    train_labels: pd.DataFrame,
    test_labels: pd.DataFrame,
    vectorizer: TfidfVectorizer,
    output_dir: Path,
) -> dict[str, Path]:
    """Save sparse matrices, labels, and the fitted vectorizer to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "x_train": output_dir / "X_train.npz",
        "x_test": output_dir / "X_test.npz",
        "y_train": output_dir / "y_train.csv",
        "y_test": output_dir / "y_test.csv",
        "vectorizer": output_dir / "tfidf_vectorizer.joblib",
    }
    save_npz(artifacts["x_train"], x_train)
    save_npz(artifacts["x_test"], x_test)
    train_labels.to_csv(artifacts["y_train"], index=False)
    test_labels.to_csv(artifacts["y_test"], index=False)
    joblib.dump(vectorizer, artifacts["vectorizer"])
    logger.info("Saved feature artifacts in: %s", output_dir)
    return artifacts


def main() -> int:
    """Load configuration once, create features, and save all stage outputs."""
    config_path = parse_args().config.resolve()
    try:
        raw_config = load_config(config_path)
        config = build_feature_config(raw_config, config_path.parent)
        train_data = load_processed_data(config.train_path, config.label_column, config.text_column)
        test_data = load_processed_data(config.test_path, config.label_column, config.text_column)
        x_train, x_test, vectorizer = create_features(train_data, test_data, config)
        artifacts = save_feature_artifacts(
            x_train,
            x_test,
            train_data[[config.label_column]],
            test_data[[config.label_column]],
            vectorizer,
            config.output_dir,
        )
    except (ConfigurationError, FileNotFoundError, OSError, ValueError, pd.errors.ParserError) as error:
        logger.error("Feature engineering failed: %s", error)
        return 1
    except Exception:
        logger.exception("Unexpected feature-engineering failure")
        return 1

    for artifact_name, artifact_path in artifacts.items():
        print(f"{artifact_name}: {artifact_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

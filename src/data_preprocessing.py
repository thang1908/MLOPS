"""Clean raw train/test SMS data using parameters loaded once from YAML."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from src.config_utils import (
    ConfigurationError,
    load_config,
    require_section,
    require_string,
    resolve_config_path,
)
from src.logging_utils import get_logger


logger = get_logger("data_preprocessing")
STAGE_NAME = "data_preprocessing"
STOP_WORDS = frozenset(ENGLISH_STOP_WORDS)
STEMMER = SnowballStemmer("english")
NON_ALPHANUMERIC = re.compile(r"[^a-z0-9]+")
LABEL_MAPPING = {"ham": 0, "spam": 1}


@dataclass(frozen=True)
class PreprocessingConfig:
    """Validated file locations and column names for preprocessing."""

    train_input_path: Path
    test_input_path: Path
    train_output_path: Path
    test_output_path: Path
    label_column: str
    text_column: str


def parse_args() -> argparse.Namespace:
    """Parse only the path to the pipeline YAML configuration."""
    parser = argparse.ArgumentParser(description="Preprocess configured SMS train/test data.")
    parser.add_argument("--config", type=Path, default=Path("params.yaml"))
    return parser.parse_args()


def build_preprocessing_config(
    config: Mapping[str, Any], config_dir: Path
) -> PreprocessingConfig:
    """Extract and validate the preprocessing section of loaded YAML."""
    section = require_section(config, STAGE_NAME)

    def configured_path(key: str) -> Path:
        return resolve_config_path(require_string(section, STAGE_NAME, key), config_dir)

    return PreprocessingConfig(
        train_input_path=configured_path("train_input_path"),
        test_input_path=configured_path("test_input_path"),
        train_output_path=configured_path("train_output_path"),
        test_output_path=configured_path("test_output_path"),
        label_column=require_string(section, STAGE_NAME, "label_column"),
        text_column=require_string(section, STAGE_NAME, "text_column"),
    )


def clean_text(text: str) -> str:
    """Lowercase, tokenize, remove noise/stopwords, stem, and rejoin text."""
    tokens = str(text).lower().split()
    alphanumeric_tokens = [NON_ALPHANUMERIC.sub("", token) for token in tokens]
    meaningful_tokens = [
        token for token in alphanumeric_tokens if token and token not in STOP_WORDS
    ]
    return " ".join(STEMMER.stem(token) for token in meaningful_tokens)


def preprocess_dataset(
    input_path: Path, output_path: Path, label_column: str, text_column: str
) -> Path:
    """Encode labels, deduplicate, clean messages, and save one processed CSV."""
    if not input_path.is_file():
        raise FileNotFoundError(f"Raw CSV not found: {input_path}")

    logger.info("Reading raw CSV: %s", input_path)
    dataframe = pd.read_csv(input_path)
    required_columns = {label_column, text_column}
    missing_columns = required_columns - set(dataframe.columns)
    if missing_columns:
        raise ValueError(f"Raw CSV is missing required columns: {sorted(missing_columns)}")

    dataframe = dataframe[[label_column, text_column]].dropna().copy()
    dataframe.columns = ["label", "message"]
    normalized_labels = dataframe["label"].astype(str).str.strip().str.lower()
    unknown_labels = set(normalized_labels) - set(LABEL_MAPPING)
    if unknown_labels:
        raise ValueError(f"Unknown label values: {sorted(unknown_labels)}")
    dataframe["label"] = normalized_labels.map(LABEL_MAPPING).astype(int)

    rows_before_deduplication = len(dataframe)
    dataframe = dataframe.drop_duplicates().reset_index(drop=True)
    logger.info("Removed %d duplicate rows", rows_before_deduplication - len(dataframe))

    logger.info("Cleaning text in %d rows", len(dataframe))
    dataframe["message"] = dataframe["message"].map(clean_text)
    dataframe = dataframe[dataframe["message"].ne("")].reset_index(drop=True)
    if dataframe.empty:
        raise ValueError(f"No usable rows remain after preprocessing {input_path}.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)
    logger.info("Saved %d processed rows to: %s", len(dataframe), output_path)
    return output_path


def preprocess_data(config: PreprocessingConfig) -> tuple[Path, Path]:
    """Process configured train and test CSVs with the same deterministic logic."""
    train_path = preprocess_dataset(
        config.train_input_path,
        config.train_output_path,
        config.label_column,
        config.text_column,
    )
    test_path = preprocess_dataset(
        config.test_input_path,
        config.test_output_path,
        config.label_column,
        config.text_column,
    )
    return train_path, test_path


def main() -> int:
    """Load configuration once and execute preprocessing for both data splits."""
    config_path = parse_args().config.resolve()
    try:
        raw_config = load_config(config_path)
        config = build_preprocessing_config(raw_config, config_path.parent)
        train_path, test_path = preprocess_data(config)
    except (ConfigurationError, FileNotFoundError, OSError, ValueError, pd.errors.ParserError) as error:
        logger.error("Data preprocessing failed: %s", error)
        return 1
    except Exception:
        logger.exception("Unexpected preprocessing failure")
        return 1

    print(f"Train: {train_path}\nTest: {test_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

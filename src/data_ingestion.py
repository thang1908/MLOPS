"""Download, validate, and split the SMS spam dataset from one YAML config."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.model_selection import train_test_split

from src.config_utils import (
    ConfigurationError,
    load_config,
    require_int,
    require_probability,
    require_section,
    require_string,
    resolve_config_path,
)
from src.logging_utils import get_logger


logger = get_logger("data_ingestion")
STAGE_NAME = "data_ingestion"


@dataclass(frozen=True)
class IngestionConfig:
    """Validated parameters for the ingestion stage."""

    url: str
    output_dir: Path
    test_size: float
    random_state: int


def parse_args() -> argparse.Namespace:
    """Parse only the path to the pipeline YAML configuration."""
    parser = argparse.ArgumentParser(description="Ingest the configured SMS spam dataset.")
    parser.add_argument("--config", type=Path, default=Path("params.yaml"))
    return parser.parse_args()


def build_ingestion_config(
    config: Mapping[str, Any], config_dir: Path
) -> IngestionConfig:
    """Extract and validate the data-ingestion section of loaded YAML."""
    section = require_section(config, STAGE_NAME)
    return IngestionConfig(
        url=require_string(section, STAGE_NAME, "url"),
        output_dir=resolve_config_path(
            require_string(section, STAGE_NAME, "output_dir"), config_dir
        ),
        test_size=require_probability(section, STAGE_NAME, "test_size"),
        random_state=require_int(section, STAGE_NAME, "random_state"),
    )


def ingest_data(config: IngestionConfig) -> tuple[Path, Path]:
    """Read the remote CSV, retain its useful fields, and save train/test CSVs."""
    logger.info("Reading spam dataset from URL: %s", config.url)
    dataframe = pd.read_csv(config.url, encoding="latin-1")
    logger.info("Downloaded %d rows and %d columns", *dataframe.shape)

    required_columns = {"v1", "v2"}
    missing_columns = required_columns - set(dataframe.columns)
    if missing_columns:
        raise ValueError(f"Source data is missing required columns: {sorted(missing_columns)}")

    cleaned_data = dataframe[["v1", "v2"]].rename(
        columns={"v1": "label", "v2": "message"}
    )
    if cleaned_data["label"].nunique() < 2:
        raise ValueError("Source data must contain at least two label classes.")

    logger.info("Splitting data into train/test sets (test_size=%.2f)", config.test_size)
    train_data, test_data = train_test_split(
        cleaned_data,
        test_size=config.test_size,
        random_state=config.random_state,
        stratify=cleaned_data["label"],
    )
    config.output_dir.mkdir(parents=True, exist_ok=True)
    train_path = config.output_dir / "train.csv"
    test_path = config.output_dir / "test.csv"
    train_data.to_csv(train_path, index=False)
    test_data.to_csv(test_path, index=False)
    logger.info("Saved %d train rows to: %s", len(train_data), train_path)
    logger.info("Saved %d test rows to: %s", len(test_data), test_path)
    return train_path, test_path


def main() -> int:
    """Load configuration once and execute the ingestion stage."""
    config_path = parse_args().config.resolve()
    try:
        raw_config = load_config(config_path)
        config = build_ingestion_config(raw_config, config_path.parent)
        train_path, test_path = ingest_data(config)
    except (ConfigurationError, FileNotFoundError, OSError, ValueError, pd.errors.ParserError) as error:
        logger.error("Data ingestion failed: %s", error)
        return 1
    except Exception:
        logger.exception("Unexpected data-ingestion failure")
        return 1

    print(f"Train: {train_path}\nTest: {test_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

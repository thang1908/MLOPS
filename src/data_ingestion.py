"""Ingest the SMS spam dataset and create raw train/test datasets."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from logging_utils import get_logger


DEFAULT_DATA_URL = "https://raw.githubusercontent.com/vikashishere/Datasets/main/spam.csv"
logger = get_logger("data_ingestion")


def ingest_data(
    url: str = DEFAULT_DATA_URL,
    output_dir: str | Path = "data/raw",
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[Path, Path]:
    """Download, clean, split, and save the spam dataset.

    The source dataset has useful columns ``v1`` and ``v2`` plus three empty
    columns.  The output files use the clearer names ``label`` and ``message``.
    """
    logger.info("Reading spam dataset from URL: %s", url)
    try:
        dataframe = pd.read_csv(url, encoding="latin-1")
    except Exception:
        logger.exception("Could not read the dataset from the URL")
        raise
    logger.info("Downloaded %d rows and %d columns", *dataframe.shape)

    required_columns = {"v1", "v2"}
    missing_columns = required_columns - set(dataframe.columns)
    if missing_columns:
        logger.error("Required columns are missing: %s", sorted(missing_columns))
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    logger.info("Removing unused columns")
    dataframe = dataframe[["v1", "v2"]].copy()
    logger.info("Renaming columns: v1 -> label, v2 -> message")
    dataframe = dataframe.rename(columns={"v1": "label", "v2": "message"})

    logger.info("Splitting data into train/test sets (test_size=%s)", test_size)
    train_data, test_data = train_test_split(
        dataframe,
        test_size=test_size,
        random_state=random_state,
        stratify=dataframe["label"],
    )
    logger.info("Train rows: %d; test rows: %d", len(train_data), len(test_data))

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    train_path = destination / "train.csv"
    test_path = destination / "test.csv"
    train_data.to_csv(train_path, index=False)
    test_data.to_csv(test_path, index=False)
    logger.info("Saved train data to: %s", train_path)
    logger.info("Saved test data to: %s", test_path)
    return train_path, test_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download, clean, and split the SMS spam dataset."
    )
    parser.add_argument("--url", default=DEFAULT_DATA_URL, help="CSV dataset URL")
    parser.add_argument("--output-dir", default="data/raw", help="Directory for train/test CSVs")
    parser.add_argument("--test-size", type=float, default=0.2)
    args = parser.parse_args()

    logger.info("Starting data ingestion pipeline")
    train_path, test_path = ingest_data(args.url, args.output_dir, args.test_size)
    logger.info("Data ingestion pipeline finished successfully")
    print(f"Train: {train_path}\nTest: {test_path}")


if __name__ == "__main__":
    main()

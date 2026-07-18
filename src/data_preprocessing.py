"""Preprocess the raw SMS spam data into model-ready text and labels."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from logging_utils import get_logger


logger = get_logger("data_preprocessing")
STOP_WORDS = frozenset(ENGLISH_STOP_WORDS)
STEMMER = SnowballStemmer("english")
NON_ALPHANUMERIC = re.compile(r"[^a-z0-9]+")
LABEL_MAPPING = {"ham": 0, "spam": 1}


def clean_text(text: str) -> str:
    """Lowercase, tokenize, remove noise/stopwords, stem, and rejoin text."""
    tokens = str(text).lower().split()
    alphanumeric_tokens = [NON_ALPHANUMERIC.sub("", token) for token in tokens]
    meaningful_tokens = [
        token for token in alphanumeric_tokens if token and token not in STOP_WORDS
    ]
    return " ".join(STEMMER.stem(token) for token in meaningful_tokens)


def preprocess_data(
    input_path: str | Path,
    output_path: str | Path,
    label_column: str = "label",
    text_column: str = "message",
) -> Path:
    """Encode labels, remove duplicate data, clean text, and save a CSV."""
    logger.info("Reading raw CSV from: %s", input_path)
    dataframe = pd.read_csv(input_path)
    logger.info("Loaded %d rows and %d columns", *dataframe.shape)

    required_columns = {label_column, text_column}
    missing_columns = required_columns - set(dataframe.columns)
    if missing_columns:
        logger.error("Required columns are missing: %s", sorted(missing_columns))
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    dataframe = dataframe[[label_column, text_column]].dropna().copy()
    dataframe.columns = ["label", "message"]
    logger.info("Kept label/message columns and removed missing rows (%d remain)", len(dataframe))

    logger.info("Encoding labels: ham -> 0, spam -> 1")
    normalised_labels = dataframe["label"].astype(str).str.strip().str.lower()
    unknown_labels = set(normalised_labels) - set(LABEL_MAPPING)
    if unknown_labels:
        logger.error("Unknown label values found: %s", sorted(unknown_labels))
        raise ValueError(f"Unknown label values: {sorted(unknown_labels)}")
    dataframe["label"] = normalised_labels.map(LABEL_MAPPING).astype(int)

    rows_before_deduplication = len(dataframe)
    dataframe = dataframe.drop_duplicates().reset_index(drop=True)
    logger.info(
        "Removed %d duplicate rows",
        rows_before_deduplication - len(dataframe),
    )

    logger.info(
        "Cleaning message text: lowercase, tokenize, remove non-alphanumeric "
        "characters/stopwords, stem, and rejoin"
    )
    dataframe["message"] = dataframe["message"].map(clean_text)
    dataframe = dataframe[dataframe["message"].ne("")].reset_index(drop=True)
    logger.info("Text cleaning completed (%d rows remain)", len(dataframe))

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(destination, index=False)
    logger.info("Processed CSV saved to: %s", destination)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess a raw SMS spam CSV.")
    parser.add_argument("input_path", help="Path to a raw train/test CSV")
    parser.add_argument("--output-path", default="data/processed/processed_data.csv")
    parser.add_argument("--label-column", default="label")
    parser.add_argument("--text-column", default="message")
    args = parser.parse_args()

    logger.info("Starting data preprocessing")
    destination = preprocess_data(
        args.input_path,
        args.output_path,
        args.label_column,
        args.text_column,
    )
    logger.info("Data preprocessing finished successfully")
    print(destination)


if __name__ == "__main__":
    main()

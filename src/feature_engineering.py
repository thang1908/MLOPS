"""Turn cleaned SMS messages into TF-IDF features for model training."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from scipy.sparse import save_npz
from sklearn.feature_extraction.text import TfidfVectorizer

from logging_utils import get_logger


logger = get_logger("feature_engineering")


def _load_processed_data(
    input_path: str | Path, label_column: str, text_column: str
) -> pd.DataFrame:
    """Read and validate one processed dataset."""
    logger.info("Reading processed CSV: %s", input_path)
    if not Path(input_path).is_file():
        logger.error("Processed CSV does not exist: %s", input_path)
        raise FileNotFoundError(
            f"Processed CSV not found: {input_path}. "
            "Run data_preprocessing.py for both raw train.csv and raw test.csv first."
        )
    dataframe = pd.read_csv(input_path)
    required_columns = {label_column, text_column}
    missing_columns = required_columns - set(dataframe.columns)
    if missing_columns:
        logger.error("Required columns are missing: %s", sorted(missing_columns))
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")
    logger.info("Loaded %d rows", len(dataframe))
    return dataframe


def create_features(
    train_path: str | Path = "data/processed/train.csv",
    test_path: str | Path = "data/processed/test.csv",
    output_dir: str | Path = "data/features",
    text_column: str = "message",
    label_column: str = "label",
    max_features: int = 40,
) -> dict[str, Path]:
    """Fit TF-IDF on train text, transform test text, and save all artifacts.

    The vectorizer is fit only on training data, preventing test-data leakage.
    Sparse matrices keep the many zero-valued text features compact on disk.
    """
    train_data = _load_processed_data(train_path, label_column, text_column)
    test_data = _load_processed_data(test_path, label_column, text_column)

    logger.info(
        "Fitting TF-IDF vectorizer on training text (max_features=%d)", max_features
    )
    vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=(1, 2))
    x_train = vectorizer.fit_transform(train_data[text_column].fillna(""))
    logger.info("Transforming test text with the fitted vectorizer")
    x_test = vectorizer.transform(test_data[text_column].fillna(""))
    logger.info("Created %d TF-IDF features", len(vectorizer.get_feature_names_out()))

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "x_train": destination / "X_train.npz",
        "x_test": destination / "X_test.npz",
        "y_train": destination / "y_train.csv",
        "y_test": destination / "y_test.csv",
        "vectorizer": destination / "tfidf_vectorizer.joblib",
    }

    logger.info("Saving sparse train features to: %s", artifacts["x_train"])
    save_npz(artifacts["x_train"], x_train)
    logger.info("Saving sparse test features to: %s", artifacts["x_test"])
    save_npz(artifacts["x_test"], x_test)
    train_data[[label_column]].to_csv(artifacts["y_train"], index=False)
    test_data[[label_column]].to_csv(artifacts["y_test"], index=False)
    logger.info("Saved train/test labels")
    joblib.dump(vectorizer, artifacts["vectorizer"])
    logger.info("Saved fitted TF-IDF vectorizer to: %s", artifacts["vectorizer"])
    return artifacts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create TF-IDF features from processed train/test SMS data."
    )
    parser.add_argument("--train-path", default="data/processed/train.csv")
    parser.add_argument("--test-path", default="data/processed/test.csv")
    parser.add_argument("--output-dir", default="data/features")
    parser.add_argument("--text-column", default="message")
    parser.add_argument("--label-column", default="label")
    parser.add_argument("--max-features", type=int, default=40)
    args = parser.parse_args()

    logger.info("Starting feature engineering")
    artifacts = create_features(
        args.train_path,
        args.test_path,
        args.output_dir,
        args.text_column,
        args.label_column,
        args.max_features,
    )
    logger.info("Feature engineering finished successfully")
    for artifact_name, artifact_path in artifacts.items():
        print(f"{artifact_name}: {artifact_path}")


if __name__ == "__main__":
    main()

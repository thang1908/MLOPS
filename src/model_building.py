"""Train and save a Logistic Regression model for SMS spam classification."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from scipy.sparse import load_npz
from sklearn.linear_model import LogisticRegression

from logging_utils import get_logger


logger = get_logger("model_building")


def train_model(
    features_path: str | Path = "data/features/X_train.npz",
    labels_path: str | Path = "data/features/y_train.csv",
    model_path: str | Path = "model/model.pkl",
    label_column: str = "label",
) -> Path:
    """Train Logistic Regression on sparse TF-IDF features and save it."""
    logger.info("Loading sparse train features from: %s", features_path)
    x_train = load_npz(features_path)
    logger.info("Loaded feature matrix with shape %s", x_train.shape)

    logger.info("Loading training labels from: %s", labels_path)
    labels = pd.read_csv(labels_path)
    if label_column not in labels.columns:
        logger.error("Label column '%s' was not found", label_column)
        raise ValueError(f"Label column '{label_column}' was not found.")
    y_train = labels[label_column]
    if x_train.shape[0] != len(y_train):
        logger.error("Feature/label row count mismatch: %d vs %d", x_train.shape[0], len(y_train))
        raise ValueError("Feature and label row counts do not match.")
    logger.info("Loaded %d labels", len(y_train))

    logger.info("Training Logistic Regression (max_iter=1000)")
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(x_train, y_train)
    logger.info("Model training completed")

    destination = Path(model_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, destination)
    logger.info("Trained model saved to: %s", destination)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train Logistic Regression from TF-IDF train features."
    )
    parser.add_argument("--features-path", default="data/features/X_train.npz")
    parser.add_argument("--labels-path", default="data/features/y_train.csv")
    parser.add_argument("--model-path", default="model/model.pkl")
    parser.add_argument("--label-column", default="label")
    args = parser.parse_args()

    logger.info("Starting model building")
    destination = train_model(
        args.features_path, args.labels_path, args.model_path, args.label_column
    )
    logger.info("Model building finished successfully")
    print(destination)


if __name__ == "__main__":
    main()

"""Evaluate the trained SMS spam model on held-out TF-IDF test data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from scipy.sparse import load_npz
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score

from logging_utils import get_logger


logger = get_logger("model_evaluation")


def evaluate_model(
    model_path: str | Path = "model/model.pkl",
    features_path: str | Path = "data/features/X_test.npz",
    labels_path: str | Path = "data/features/y_test.csv",
    metrics_path: str | Path = "reports/metrics.json",
    label_column: str = "label",
) -> dict[str, float]:
    """Load test artifacts, evaluate the model, and save JSON metrics."""
    config = {
        "model_path": str(model_path),
        "features_path": str(features_path),
        "labels_path": str(labels_path),
        "metrics_path": str(metrics_path),
        "label_column": label_column,
    }
    logger.info("Evaluation configuration: %s", config)

    logger.info("Loading trained model from: %s", model_path)
    model = joblib.load(model_path)

    logger.info("Loading sparse test features from: %s", features_path)
    x_test = load_npz(features_path)
    logger.info("Loaded test feature matrix with shape %s", x_test.shape)

    logger.info("Loading test labels from: %s", labels_path)
    labels = pd.read_csv(labels_path)
    if label_column not in labels.columns:
        logger.error("Label column '%s' was not found", label_column)
        raise ValueError(f"Label column '{label_column}' was not found.")
    y_test = labels[label_column]
    if x_test.shape[0] != len(y_test):
        logger.error("Feature/label row count mismatch: %d vs %d", x_test.shape[0], len(y_test))
        raise ValueError("Feature and label row counts do not match.")

    logger.info("Generating predictions")
    predictions = model.predict(x_test)
    if 1 not in model.classes_:
        raise ValueError("The model does not contain class 1, required for AUC.")
    positive_class_index = list(model.classes_).index(1)
    probabilities = model.predict_proba(x_test)[:, positive_class_index]

    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, pos_label=1, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, pos_label=1, zero_division=0)),
        "auc": float(roc_auc_score(y_test, probabilities)),
    }
    logger.info(
        "Metrics - accuracy: %.4f, precision: %.4f, recall: %.4f, auc: %.4f",
        metrics["accuracy"],
        metrics["precision"],
        metrics["recall"],
        metrics["auc"],
    )

    destination = Path(metrics_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    logger.info("Metrics JSON saved to: %s", destination)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate Logistic Regression on TF-IDF test data."
    )
    parser.add_argument("--model-path", default="model/model.pkl")
    parser.add_argument("--features-path", default="data/features/X_test.npz")
    parser.add_argument("--labels-path", default="data/features/y_test.csv")
    parser.add_argument("--metrics-path", default="reports/metrics.json")
    parser.add_argument("--label-column", default="label")
    args = parser.parse_args()

    logger.info("Starting model evaluation")
    metrics = evaluate_model(
        args.model_path,
        args.features_path,
        args.labels_path,
        args.metrics_path,
        args.label_column,
    )
    logger.info("Model evaluation finished successfully")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

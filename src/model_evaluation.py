"""Evaluate the configured spam classifier with held-out TF-IDF test artifacts."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from dvclive import Live
from scipy.sparse import csr_matrix, load_npz
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score

from src.config_utils import (
    ConfigurationError,
    load_config,
    require_section,
    require_string,
    resolve_config_path,
)
from src.logging_utils import get_logger


logger = get_logger("model_evaluation")
STAGE_NAME = "model_evaluation"


@dataclass(frozen=True)
class EvaluationConfig:
    """Validated locations and label metadata for model evaluation."""

    model_path: Path
    features_path: Path
    labels_path: Path
    metrics_path: Path
    label_column: str
    dvclive_dir: Path


def parse_args() -> argparse.Namespace:
    """Parse only the path to the pipeline YAML configuration."""
    parser = argparse.ArgumentParser(description="Evaluate the configured spam model.")
    parser.add_argument("--config", type=Path, default=Path("params.yaml"))
    return parser.parse_args()


def build_evaluation_config(
    config: Mapping[str, Any], config_dir: Path
) -> EvaluationConfig:
    """Extract and validate the model-evaluation section of loaded YAML."""
    section = require_section(config, STAGE_NAME)

    def configured_path(key: str) -> Path:
        return resolve_config_path(require_string(section, STAGE_NAME, key), config_dir)

    return EvaluationConfig(
        model_path=configured_path("model_path"),
        features_path=configured_path("features_path"),
        labels_path=configured_path("labels_path"),
        metrics_path=configured_path("metrics_path"),
        label_column=require_string(section, STAGE_NAME, "label_column"),
        dvclive_dir=configured_path("dvclive_dir"),
    )


def load_evaluation_data(
    features_path: Path, labels_path: Path, label_column: str
) -> tuple[csr_matrix, pd.Series]:
    """Load matching sparse test features and target labels."""
    if not features_path.is_file():
        raise FileNotFoundError(f"Test feature matrix not found: {features_path}")
    if not labels_path.is_file():
        raise FileNotFoundError(f"Test label CSV not found: {labels_path}")

    features = load_npz(features_path).tocsr()
    labels = pd.read_csv(labels_path)
    if label_column not in labels.columns:
        raise ValueError(f"Label column '{label_column}' was not found in {labels_path}.")
    targets = labels[label_column]
    if targets.isna().any():
        raise ValueError("Test labels contain missing values.")
    if features.shape[0] != len(targets):
        raise ValueError(
            "Feature and label row counts do not match: "
            f"{features.shape[0]} features, {len(targets)} labels."
        )
    if targets.nunique() < 2:
        raise ValueError("Test labels must contain at least two classes for AUC.")
    return features, targets


def evaluate_model(
    model: LogisticRegression, features: csr_matrix, targets: pd.Series
) -> dict[str, float]:
    """Generate predictions and return accuracy, precision, recall, and AUC."""
    if 1 not in model.classes_:
        raise ValueError("The model does not contain positive class 1 required for AUC.")

    predictions = model.predict(features)
    positive_class_index = list(model.classes_).index(1)
    probabilities = model.predict_proba(features)[:, positive_class_index]
    metrics = {
        "accuracy": float(accuracy_score(targets, predictions)),
        "precision": float(precision_score(targets, predictions, pos_label=1, zero_division=0)),
        "recall": float(recall_score(targets, predictions, pos_label=1, zero_division=0)),
        "auc": float(roc_auc_score(targets, probabilities)),
    }
    logger.info("Evaluation metrics: %s", metrics)
    return metrics


def save_metrics(metrics: dict[str, float], metrics_path: Path) -> Path:
    """Write metrics as a readable JSON report."""
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    logger.info("Metrics saved to: %s", metrics_path)
    return metrics_path


def main() -> int:
    """Load configuration once, evaluate the model, and persist its metrics."""
    config_path = parse_args().config.resolve()
    try:
        raw_config = load_config(config_path)
        config = build_evaluation_config(raw_config, config_path.parent)
        if not config.model_path.is_file():
            raise FileNotFoundError(f"Trained model not found: {config.model_path}")
        logger.info("Loading trained model from: %s", config.model_path)
        model = joblib.load(config.model_path)
        if not isinstance(model, LogisticRegression):
            raise TypeError("Configured model must be a scikit-learn LogisticRegression instance.")
        features, targets = load_evaluation_data(
            config.features_path, config.labels_path, config.label_column
        )
        metrics = evaluate_model(model, features, targets)
        metrics_path = save_metrics(metrics, config.metrics_path)
        with Live(
            dir=str(config.dvclive_dir),
            save_dvc_exp=False,
            dvcyaml=False,
        ) as live:
            for metric_name, metric_value in metrics.items():
                live.log_metric(metric_name, metric_value)
            live.next_step()
    except (
        ConfigurationError,
        FileNotFoundError,
        OSError,
        TypeError,
        ValueError,
        pd.errors.ParserError,
    ) as error:
        logger.error("Model evaluation failed: %s", error)
        return 1
    except Exception:
        logger.exception("Unexpected model-evaluation failure")
        return 1

    print(f"Metrics: {metrics_path}")
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

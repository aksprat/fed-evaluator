import argparse
import json
import os

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


def load_ground_truth():

    gt_df = pd.read_csv(
        "data/ground_truth.csv"
    )

    gt_df["ground_truth"] = (
        gt_df["ground_truth"]
        .str.strip()
        .str.lower()
    )

    return gt_df


def load_results(model):

    with open(f"results/{model}.json") as f:

        return json.load(f)


def compute_metrics(model):

    gt_df = load_ground_truth()

    result_data = load_results(model)

    predictions = pd.DataFrame(
        result_data["results"]
    )

    predictions["prediction"] = (
        predictions["prediction"]
        .fillna("other")
        .str.strip()
        .str.lower()
    )

    merged = gt_df.merge(
        predictions,
        on="issue_number"
    )

    y_true = merged["ground_truth"]

    y_pred = merged["prediction"]

    labels = sorted(
        list(
            set(y_true)
            | set(y_pred)
        )
    )

    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    report = classification_report(
        y_true,
        y_pred,
        output_dict=True,
        zero_division=0
    )

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=labels
    )

    latencies = predictions[
        predictions["success"]
    ]["latency_seconds"]

    metrics = {

        "model": model,

        "accuracy": accuracy,

        "classification_report": report,

        "confusion_matrix": cm.tolist(),

        "labels": labels,

        "p50_latency_seconds":
            float(
                np.percentile(
                    latencies,
                    50
                )
            ),

        "p95_latency_seconds":
            float(
                np.percentile(
                    latencies,
                    95
                )
            ),

        "throughput_rps":
            result_data["throughput_rps"],

        "wall_clock_seconds":
            result_data["wall_clock_seconds"],

        "concurrency":
            result_data["concurrency"],

        "error_breakdown":

            predictions["error_type"]
            .fillna("success")
            .value_counts()
            .to_dict()

    }

    return metrics


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        required=True
    )

    args = parser.parse_args()

    metrics = compute_metrics(
        args.model
    )

    os.makedirs(
        "metrics",
        exist_ok=True
    )

    output_file = (
        f"metrics/{args.model}_metrics.json"
    )

    with open(
        output_file,
        "w"
    ) as f:

        json.dump(
            metrics,
            f,
            indent=2
        )

    print()

    print(
        "Saved metrics to:",
        output_file
    )

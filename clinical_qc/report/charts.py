"""Chart generation for QC reports."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_missingness_bar(
    missingness_summary: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """Create a bar chart of missing rate by column."""
    output_path = Path(output_path)

    if missingness_summary.empty:
        return

    plt.figure(figsize=(8, 5))
    plt.bar(
        missingness_summary["column"],
        missingness_summary["missing_rate"],
    )
    plt.xlabel("Column")
    plt.ylabel("Missing Rate")
    plt.title("Missing Data Rate by Column")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_issue_type_bar(
    issues_df: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """Create a bar chart of issue counts by check type."""
    output_path = Path(output_path)

    if issues_df.empty:
        return

    counts = issues_df["check_type"].value_counts()

    plt.figure(figsize=(8, 5))
    plt.bar(counts.index, counts.values)
    plt.xlabel("Issue Type")
    plt.ylabel("Count")
    plt.title("QC Issues by Type")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
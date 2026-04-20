from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from clinical_qc.models import QCIssue


def _numeric_columns(df: pd.DataFrame, columns: Iterable[str] | None = None) -> list[str]:
    if columns is not None:
        return [col for col in columns if col in df.columns]
    return df.select_dtypes(include=[np.number]).columns.tolist()


def check_outliers_iqr(
    df: pd.DataFrame,
    columns: Iterable[str] | None = None,
    multiplier: float = 1.5,
) -> tuple[pd.DataFrame, list[QCIssue]]:
    """Detect outliers using the IQR rule."""
    selected = _numeric_columns(df, columns)

    summary_rows: list[dict[str, object]] = []
    issues: list[QCIssue] = []

    for col in selected:
        series = df[col].dropna()
        if series.empty:
            summary_rows.append(
                {"column": col, "method": "iqr", "outlier_count": 0}
            )
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr

        mask = df[col].notna() & ((df[col] < lower) | (df[col] > upper))
        idxs = df.index[mask].tolist()

        summary_rows.append(
            {
                "column": col,
                "method": "iqr",
                "outlier_count": len(idxs),
                "lower_bound": lower,
                "upper_bound": upper,
            }
        )

        for idx in idxs:
            issues.append(
                QCIssue(
                    row=int(idx),
                    column=col,
                    check_type="outlier",
                    severity="warning",
                    message=f"{col} is an outlier by IQR rule",
                    value=df.loc[idx, col],
                )
            )

    return pd.DataFrame(summary_rows), issues


def check_outliers_zscore(
    df: pd.DataFrame,
    columns: Iterable[str] | None = None,
    threshold: float = 3.0,
) -> tuple[pd.DataFrame, list[QCIssue]]:
    """Detect outliers using z-scores."""
    selected = _numeric_columns(df, columns)

    summary_rows: list[dict[str, object]] = []
    issues: list[QCIssue] = []

    for col in selected:
        series = df[col].dropna()
        if series.empty or series.std(ddof=0) == 0:
            summary_rows.append(
                {"column": col, "method": "zscore", "outlier_count": 0}
            )
            continue

        mean = series.mean()
        std = series.std(ddof=0)
        z = (df[col] - mean) / std
        mask = df[col].notna() & (z.abs() > threshold)
        idxs = df.index[mask].tolist()

        summary_rows.append(
            {
                "column": col,
                "method": "zscore",
                "outlier_count": len(idxs),
                "threshold": threshold,
            }
        )

        for idx in idxs:
            issues.append(
                QCIssue(
                    row=int(idx),
                    column=col,
                    check_type="outlier",
                    severity="warning",
                    message=f"{col} is an outlier by z-score > {threshold}",
                    value=df.loc[idx, col],
                )
            )

    return pd.DataFrame(summary_rows), issues
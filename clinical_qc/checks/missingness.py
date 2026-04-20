from __future__ import annotations

from typing import Any

import pandas as pd

from clinical_qc.models import QCIssue


def check_missingness(
    df: pd.DataFrame,
    thresholds: dict[str, float] | None = None,
) -> tuple[pd.DataFrame, list[QCIssue]]:
    """Check missing values by column."""
    thresholds = thresholds or {"warning": 0.1, "error": 0.3}

    summary_rows: list[dict[str, Any]] = []
    issues: list[QCIssue] = []

    n_rows = len(df)

    for col in df.columns:
        missing_count = int(df[col].isna().sum())
        missing_rate = missing_count / n_rows if n_rows > 0 else 0.0

        severity = None
        if missing_rate >= thresholds.get("error", 0.3):
            severity = "error"
        elif missing_rate >= thresholds.get("warning", 0.1):
            severity = "warning"

        summary_rows.append(
            {
                "column": col,
                "missing_count": missing_count,
                "missing_rate": missing_rate,
                "severity": severity,
            }
        )

        if severity is not None:
            issues.append(
                QCIssue(
                    row=None,
                    column=col,
                    check_type="missingness",
                    severity=severity,
                    message=f"{col} has {missing_rate:.1%} missing values",
                    value=missing_rate,
                )
            )

    summary = pd.DataFrame(summary_rows)
    return summary, issues
from __future__ import annotations

import pandas as pd

from clinical_qc.config import RangeRule
from clinical_qc.models import QCIssue


def check_ranges(
    df: pd.DataFrame,
    rules: dict[str, RangeRule],
) -> tuple[pd.DataFrame, list[QCIssue]]:
    """Check whether values fall within allowed ranges."""
    summary_rows: list[dict[str, object]] = []
    issues: list[QCIssue] = []

    for col, rule in rules.items():
        if col not in df.columns:
            continue

        mask = pd.Series(False, index=df.index)

        if rule.min is not None:
            mask = mask | (df[col].notna() & (df[col] < rule.min))
        if rule.max is not None:
            mask = mask | (df[col].notna() & (df[col] > rule.max))

        idxs = df.index[mask].tolist()

        summary_rows.append(
            {
                "column": col,
                "min_allowed": rule.min,
                "max_allowed": rule.max,
                "out_of_range_count": len(idxs),
                "severity": rule.severity,
            }
        )

        for idx in idxs:
            value = df.loc[idx, col]
            issues.append(
                QCIssue(
                    row=int(idx),
                    column=col,
                    check_type="range_check",
                    severity=rule.severity,
                    message=(
                        f"{col}={value} is outside allowed range "
                        f"[{rule.min}, {rule.max}]"
                    ),
                    value=value,
                )
            )

    return pd.DataFrame(summary_rows), issues
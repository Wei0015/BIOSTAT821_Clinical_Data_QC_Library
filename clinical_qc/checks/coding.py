from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd

from clinical_qc.models import QCIssue


def check_allowed_values(
    df: pd.DataFrame,
    allowed_values: dict[str, list[Any]],
    case_insensitive: bool = True,
) -> tuple[pd.DataFrame, list[QCIssue]]:
    """Check whether categorical values are within the allowed set."""
    summary_rows: list[dict[str, object]] = []
    issues: list[QCIssue] = []

    for col, allowed in allowed_values.items():
        if col not in df.columns:
            continue

        observed = df[col].dropna()

        if case_insensitive:
            allowed_set = {str(v).strip().lower() for v in allowed}
            invalid_mask = observed.map(
                lambda x: str(x).strip().lower() not in allowed_set
            )
        else:
            allowed_set = set(allowed)
            invalid_mask = observed.map(lambda x: x not in allowed_set)

        invalid = observed[invalid_mask]
        invalid_counts = Counter(invalid.tolist())

        summary_rows.append(
            {
                "column": col,
                "n_invalid": len(invalid),
                "invalid_values": sorted(map(str, invalid_counts.keys())),
            }
        )

        for idx, value in invalid.items():
            issues.append(
                QCIssue(
                    row=int(idx),
                    column=col,
                    check_type="code_check",
                    severity="warning",
                    message=f"unexpected category value: {value}",
                    value=value,
                )
            )

    return pd.DataFrame(summary_rows), issues
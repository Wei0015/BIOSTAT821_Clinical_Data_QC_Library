from __future__ import annotations

import pandas as pd

from clinical_qc.config import DateRule
from clinical_qc.models import QCIssue


def check_date_rules(
    df: pd.DataFrame,
    rules: list[DateRule],
) -> tuple[pd.DataFrame, list[QCIssue]]:
    """Check date logic rules such as discharge_date >= admit_date."""
    summary_rows: list[dict[str, object]] = []
    issues: list[QCIssue] = []

    for rule in rules:
        if rule.start not in df.columns or rule.end not in df.columns:
            continue

        start = pd.to_datetime(df[rule.start], errors="coerce")
        end = pd.to_datetime(df[rule.end], errors="coerce")

        if rule.rule == "end_on_or_after_start":
            mask = start.notna() & end.notna() & (end < start)
            msg_template = f"{rule.end} is earlier than {rule.start}"
        else:
            raise ValueError(f"Unsupported date rule: {rule.rule}")

        idxs = df.index[mask].tolist()

        summary_rows.append(
            {
                "start": rule.start,
                "end": rule.end,
                "rule": rule.rule,
                "violation_count": len(idxs),
                "severity": rule.severity,
            }
        )

        for idx in idxs:
            issues.append(
                QCIssue(
                    row=int(idx),
                    column=rule.end,
                    check_type="date_logic",
                    severity=rule.severity,
                    message=msg_template,
                    value=df.loc[idx, rule.end],
                )
            )

    return pd.DataFrame(summary_rows), issues
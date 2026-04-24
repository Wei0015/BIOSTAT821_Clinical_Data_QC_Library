"""QC pipeline that orchestrates all checks and aggregates results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from clinical_qc.checks.coding import check_allowed_values
from clinical_qc.checks.dates import check_date_rules
from clinical_qc.checks.missingness import check_missingness
from clinical_qc.checks.outliers import check_outliers_iqr, check_outliers_zscore
from clinical_qc.checks.ranges import check_ranges
from clinical_qc.config import QCConfig
from clinical_qc.models import QCIssue


VALID_CHECKS = {
    "required_columns",
    "missingness",
    "outliers",
    "dates",
    "coding",
    "ranges",
}


@dataclass
class QCResult:
    """Container for all QC pipeline outputs."""

    issues: list[QCIssue] = field(default_factory=list)

    required_columns_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    missingness_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    outlier_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    date_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    coding_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    range_summary: pd.DataFrame = field(default_factory=pd.DataFrame)

    n_rows: int = 0
    n_columns: int = 0
    column_names: list[str] = field(default_factory=list)

    def issues_table(self) -> pd.DataFrame:
        """Return all QC issues as a single DataFrame."""
        columns = ["row", "column", "check_type", "severity", "message", "value"]

        if not self.issues:
            return pd.DataFrame(columns=columns)

        return pd.DataFrame(
            [issue.to_dict() for issue in self.issues],
            columns=columns,
        )

    def issues_tables_by_column(self) -> dict[str, pd.DataFrame]:
        """Return QC issues split into separate tables by column."""
        issues_df = self.issues_table()

        if issues_df.empty:
            return {}

        tables: dict[str, pd.DataFrame] = {}

        for col_name, group in issues_df.groupby("column", dropna=False):
            pretty_col = "general" if pd.isna(col_name) else str(col_name)

            tables[pretty_col] = (
                group
                .drop(columns=["column"])
                .reset_index(drop=True)
            )

        return tables

    def summaries(self) -> dict[str, pd.DataFrame]:
        """Return all per-check summary tables."""
        return {
            "required_columns": self.required_columns_summary,
            "missingness": self.missingness_summary,
            "outliers": self.outlier_summary,
            "dates": self.date_summary,
            "coding": self.coding_summary,
            "ranges": self.range_summary,
        }

    def summary_stats(self) -> dict[str, Any]:
        """Return high-level summary statistics for the QC run."""
        issues_df = self.issues_table()

        if issues_df.empty:
            severity_counts: dict[str, int] = {}
            check_type_counts: dict[str, int] = {}
        else:
            severity_counts = issues_df["severity"].value_counts().to_dict()
            check_type_counts = issues_df["check_type"].value_counts().to_dict()

        return {
            "n_rows": self.n_rows,
            "n_columns": self.n_columns,
            "total_issues": len(self.issues),
            "severity_counts": severity_counts,
            "check_type_counts": check_type_counts,
        }


def _check_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
) -> tuple[pd.DataFrame, list[QCIssue]]:
    """Check whether all required columns are present."""
    summary_rows = []
    issues: list[QCIssue] = []

    for col in required_columns:
        present = col in df.columns
        summary_rows.append(
            {
                "column": col,
                "present": present,
            }
        )

        if not present:
            issues.append(
                QCIssue(
                    row=None,
                    column=col,
                    check_type="required_column",
                    severity="error",
                    message=f"required column is missing: {col}",
                    value=None,
                )
            )

    return pd.DataFrame(summary_rows), issues


def _validate_checks(checks: list[str] | None) -> set[str]:
    """Validate and normalize selected check names."""
    if checks is None:
        return set(VALID_CHECKS)

    unknown = set(checks) - VALID_CHECKS
    if unknown:
        raise ValueError(
            "Unknown check(s): "
            + ", ".join(sorted(unknown))
            + ". Valid checks are: "
            + ", ".join(sorted(VALID_CHECKS))
        )

    return set(checks)


def run_pipeline(
    df: pd.DataFrame,
    config: QCConfig | None = None,
    *,
    checks: list[str] | None = None,
) -> QCResult:
    """
    Run the QC pipeline on a pandas DataFrame.
    """
    config = config or QCConfig()
    enabled = _validate_checks(checks)

    result = QCResult(
        n_rows=len(df),
        n_columns=len(df.columns),
        column_names=list(df.columns),
    )

    if "required_columns" in enabled:
        summary, issues = _check_required_columns(
            df=df,
            required_columns=config.required_columns,
        )
        result.required_columns_summary = summary
        result.issues.extend(issues)

    if "missingness" in enabled:
        summary, issues = check_missingness(
            df=df,
            thresholds=config.missingness_thresholds,
        )
        result.missingness_summary = summary
        result.issues.extend(issues)

    if "ranges" in enabled and config.value_ranges:
        summary, issues = check_ranges(
            df=df,
            rules=config.value_ranges,
        )
        result.range_summary = summary
        result.issues.extend(issues)

    if "dates" in enabled and config.date_rules:
        summary, issues = check_date_rules(
            df=df,
            rules=config.date_rules,
        )
        result.date_summary = summary
        result.issues.extend(issues)

    if "coding" in enabled and config.allowed_values:
        summary, issues = check_allowed_values(
            df=df,
            allowed_values=config.allowed_values,
        )
        result.coding_summary = summary
        result.issues.extend(issues)

    if "outliers" in enabled:
        if config.outlier_method == "iqr":
            summary, issues = check_outliers_iqr(
                df=df,
                multiplier=config.outlier_iqr_multiplier,
            )
        elif config.outlier_method == "zscore":
            summary, issues = check_outliers_zscore(
                df=df,
                threshold=config.outlier_z_threshold,
            )
        else:
            raise ValueError(
                f"Unsupported outlier method: {config.outlier_method}. "
                "Use 'iqr' or 'zscore'."
            )

        result.outlier_summary = summary
        result.issues.extend(issues)

    return result


def run_qc(
    df: pd.DataFrame,
    config: QCConfig | None = None,
    *,
    checks: list[str] | None = None,
) -> QCResult:
    """Alias for run_pipeline."""
    return run_pipeline(df=df, config=config, checks=checks)
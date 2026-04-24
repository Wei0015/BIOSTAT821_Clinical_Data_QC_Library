"""Command line interface for clinical_qc."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from clinical_qc.config import load_config
from clinical_qc.pipeline import run_pipeline
from clinical_qc.report.charts import plot_issue_type_bar, plot_missingness_bar
from clinical_qc.report.export import export_html_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run clinical QC checks")
    parser.add_argument("data", help="Path to CSV file")
    parser.add_argument("--config", help="Path to config YAML", default=None)
    parser.add_argument("--output", help="Output folder", default="output")

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.data)
    config = load_config(args.config) if args.config else None

    result = run_pipeline(df, config)

    issues_df = result.issues_table()
    summaries = result.summaries()   # ⭐ 关键修复点

    issues_path = output_dir / "issues.csv"
    missingness_chart_path = output_dir / "missingness_bar.png"
    issue_type_chart_path = output_dir / "issue_type_bar.png"
    report_path = output_dir / "report.html"

    issues_df.to_csv(issues_path, index=False)

    if "missingness" in summaries:
        plot_missingness_bar(
            summaries["missingness"],
            missingness_chart_path,
        )

    plot_issue_type_bar(
        issues_df,
        issue_type_chart_path,
    )

    export_html_report(
        result,
        report_path,
    )

    print("QC complete!")
    print(result.summary_stats())
    print(f"Issues saved to: {issues_path}")
    print(f"HTML report saved to: {report_path}")


if __name__ == "__main__":
    main()
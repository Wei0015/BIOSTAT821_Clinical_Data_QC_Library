"""Export QC reports."""

from __future__ import annotations

from pathlib import Path

from clinical_qc.pipeline import QCResult


def export_html_report(result: QCResult, output_path: str | Path) -> None:
    """Export a simple HTML QC report."""
    output_path = Path(output_path)

    issues_by_column = result.issues_tables_by_column()
    stats = result.summary_stats()

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Clinical QC Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
        }}
        h1, h2 {{
            color: #2c3e50;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 16px;
        }}
        th, td {{
            border: 1px solid #cccccc;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        .summary {{
            background-color: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 24px;
        }}
        img {{
            max-width: 800px;
            width: 100%;
            margin: 16px 0;
            border: 1px solid #dddddd;
        }}
    </style>
</head>
<body>
    <h1>Clinical Data QC Report</h1>

    <div class="summary">
        <p><strong>Rows:</strong> {stats["n_rows"]}</p>
        <p><strong>Columns:</strong> {stats["n_columns"]}</p>
        <p><strong>Total Issues:</strong> {stats["total_issues"]}</p>
        <p><strong>Severity Counts:</strong> {stats["severity_counts"]}</p>
        <p><strong>Issue Type Counts:</strong> {stats["check_type_counts"]}</p>
    </div>

    <h2>Missing Data Bar Chart</h2>
    <img src="missingness_bar.png" alt="Missing data bar chart">

    <h2>Issue Type Distribution</h2>
    <img src="issue_type_bar.png" alt="Issue type distribution chart">

    <h2>Issues by Column</h2>
    {
        "<p>No QC issues found.</p>" if not issues_by_column else "".join(
            f"<h3>{col.replace('_', ' ').title()} Issues</h3>"
            + table.to_html(index=False)
            for col, table in issues_by_column.items()
        )
    }
</body>
</html>
"""

    output_path.write_text(html, encoding="utf-8")
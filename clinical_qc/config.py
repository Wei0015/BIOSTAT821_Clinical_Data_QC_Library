from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class RangeRule:
    """Allowed numeric range for a column."""

    min: float | None = None
    max: float | None = None
    severity: str = "warning"


@dataclass
class DateRule:
    """Rule for checking date order between two columns."""

    start: str
    end: str
    rule: str = "end_on_or_after_start"
    severity: str = "error"


@dataclass
class QCConfig:
    """Configuration for QC checks."""

    required_columns: list[str] = field(default_factory=list)
    value_ranges: dict[str, RangeRule] = field(default_factory=dict)
    allowed_values: dict[str, list[Any]] = field(default_factory=dict)
    date_rules: list[DateRule] = field(default_factory=list)
    missingness_thresholds: dict[str, float] = field(
        default_factory=lambda: {"warning": 0.1, "error": 0.3}
    )
    outlier_method: str = "iqr"
    outlier_z_threshold: float = 3.0
    outlier_iqr_multiplier: float = 1.5


def load_config(path: str | Path) -> QCConfig:
    """Load QC config from a YAML file."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    value_ranges = {
        col: RangeRule(**rule) for col, rule in raw.get("value_ranges", {}).items()
    }
    date_rules = [DateRule(**rule) for rule in raw.get("date_rules", [])]

    return QCConfig(
        required_columns=raw.get("required_columns", []),
        value_ranges=value_ranges,
        allowed_values=raw.get("allowed_values", {}),
        date_rules=date_rules,
        missingness_thresholds=raw.get(
            "missingness_thresholds", {"warning": 0.1, "error": 0.3}
        ),
        outlier_method=raw.get("outlier_method", "iqr"),
        outlier_z_threshold=raw.get("outlier_z_threshold", 3.0),
        outlier_iqr_multiplier=raw.get("outlier_iqr_multiplier", 1.5),
    )
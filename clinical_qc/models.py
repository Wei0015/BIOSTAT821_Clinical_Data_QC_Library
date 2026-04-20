from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class QCIssue:
    """A single QC issue identified in the dataset."""

    row: int | None
    column: str
    check_type: str
    severity: str
    message: str
    value: Any = None

    def to_dict(self) -> dict[str, Any]:
        """Convert issue to dictionary."""
        return asdict(self)
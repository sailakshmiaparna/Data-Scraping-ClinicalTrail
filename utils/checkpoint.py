import json
from pathlib import Path
from typing import Any


class Checkpoint:
    """Atomic JSON checkpoint for pagination and failed-record recovery."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"next_page_token": None, "processed": 0, "failed_nct_ids": [], "completed": False}
        try:
            with self.path.open(encoding="utf-8") as handle:
                return {"failed_nct_ids": [], "completed": False, **json.load(handle)}
        except (OSError, json.JSONDecodeError):
            return {"next_page_token": None, "processed": 0, "failed_nct_ids": [], "completed": False}

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temporary.replace(self.path)

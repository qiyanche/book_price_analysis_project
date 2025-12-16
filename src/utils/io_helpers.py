from __future__ import annotations
from pathlib import Path
import json
from typing import Any, Iterable, Dict
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def project_path(*parts: str) -> Path:
    return PROJECT_ROOT.joinpath(*parts)

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def append_csv(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(list(rows))
    header = not path.exists()
    df.to_csv(path, mode="a", header=header, index=False)

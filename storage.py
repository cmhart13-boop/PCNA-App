from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DB_PATH = Path("runtime/pcna_assistant.db")
FILES_DIR = Path("runtime/files")


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            customer TEXT NOT NULL,
            project TEXT NOT NULL,
            created_at TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )
        """
    )
    con.commit()
    return con


def save_project(kind: str, customer: str, project: str, payload: dict) -> int:
    created_at = datetime.now(timezone.utc).isoformat()
    customer = (customer or "Unassigned").strip() or "Unassigned"
    project = (project or kind).strip() or kind
    with _connect() as con:
        cur = con.execute(
            "INSERT INTO projects(kind, customer, project, created_at, payload_json) VALUES(?,?,?,?,?)",
            (kind, customer, project, created_at, json.dumps(payload, ensure_ascii=False)),
        )
        con.commit()
        return int(cur.lastrowid)


def list_projects(limit: int = 500) -> list[dict]:
    with _connect() as con:
        rows = con.execute(
            "SELECT id, kind, customer, project, created_at, payload_json FROM projects ORDER BY id DESC LIMIT ?",
            (int(limit),),
        ).fetchall()
    return [
        {
            "id": int(row["id"]),
            "type": row["kind"],
            "customer": row["customer"],
            "project": row["project"],
            "date": row["created_at"],
            "payload": json.loads(row["payload_json"]),
        }
        for row in rows
    ]


def delete_project(project_id: int) -> None:
    with _connect() as con:
        con.execute("DELETE FROM projects WHERE id = ?", (int(project_id),))
        con.commit()


def save_upload(project_id: int, filename: str, data: bytes) -> str:
    safe_name = Path(filename).name.replace("..", "_")
    folder = FILES_DIR / str(int(project_id))
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / safe_name
    target.write_bytes(data)
    return str(target)


def list_project_files(project_id: int) -> list[Path]:
    folder = FILES_DIR / str(int(project_id))
    if not folder.exists():
        return []
    return sorted([p for p in folder.iterdir() if p.is_file()])


def export_projects() -> str:
    return json.dumps(list_projects(), indent=2, ensure_ascii=False)

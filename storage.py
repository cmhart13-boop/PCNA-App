from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path("runtime/pcna_assistant.db")
FILES_DIR = Path("runtime/files")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _create_schema(con: sqlite3.Connection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            customer TEXT NOT NULL DEFAULT 'Unassigned',
            status TEXT NOT NULL DEFAULT 'Active',
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS artifacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            artifact_type TEXT NOT NULL,
            title TEXT NOT NULL,
            original_prompt TEXT NOT NULL DEFAULT '',
            ai_output TEXT NOT NULL DEFAULT '',
            structured_json TEXT NOT NULL DEFAULT '{}',
            status TEXT NOT NULL DEFAULT 'Complete',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
        """
    )


def _migrate_legacy_if_needed(con: sqlite3.Connection) -> None:
    table = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'").fetchone()
    if not table:
        return
    columns = {row[1] for row in con.execute("PRAGMA table_info(projects)").fetchall()}
    if "name" in columns:
        return
    if not {"kind", "customer", "project", "created_at", "payload_json"}.issubset(columns):
        return
    con.execute("ALTER TABLE projects RENAME TO legacy_projects")
    _create_schema(con)
    rows = con.execute("SELECT id, kind, customer, project, created_at, payload_json FROM legacy_projects ORDER BY id").fetchall()
    kind_map = {
        "Spec Sample Order": "spec_sample",
        "Quote": "quote",
        "Virtual / Design": "virtual",
        "Virtual Request": "virtual",
        "Perfectly Packaged": "virtual",
        "Blank Sample": "blank_sample",
    }
    for row in rows:
        customer = (row["customer"] or "Unassigned").strip() or "Unassigned"
        project_name = (row["project"] or row["kind"] or "Untitled Project").strip() or "Untitled Project"
        existing = con.execute(
            "SELECT id FROM projects WHERE lower(name)=lower(?) AND lower(customer)=lower(?) ORDER BY id DESC LIMIT 1",
            (project_name, customer),
        ).fetchone()
        if existing:
            project_id = int(existing["id"])
        else:
            cur = con.execute(
                "INSERT INTO projects(name, customer, status, notes, created_at, updated_at) VALUES(?,?,?,?,?,?)",
                (project_name, customer, "Active", "", row["created_at"], row["created_at"]),
            )
            project_id = int(cur.lastrowid)
        try:
            payload = json.loads(row["payload_json"] or "{}")
        except Exception:
            payload = {}
        artifact_type = kind_map.get(row["kind"], str(row["kind"] or "artifact").lower().replace(" ", "_"))
        output = str(payload.get("order") or payload.get("quote") or "")
        prompt = str(payload.get("request") or payload.get("Request") or "")
        con.execute(
            """
            INSERT INTO artifacts(project_id, artifact_type, title, original_prompt, ai_output, structured_json, status, created_at, updated_at)
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (project_id, artifact_type, row["kind"] or "Saved Work", prompt, output, json.dumps(payload, ensure_ascii=False), "Complete", row["created_at"], row["created_at"]),
        )
    con.execute("DROP TABLE legacy_projects")


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    _migrate_legacy_if_needed(con)
    _create_schema(con)
    con.commit()
    return con


def _project_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": int(row["id"]),
        "project": row["name"],
        "name": row["name"],
        "customer": row["customer"],
        "status": row["status"],
        "notes": row["notes"],
        "date": row["created_at"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def get_or_create_project(name: str, customer: str = "", notes: str = "") -> int:
    name = (name or "Untitled Project").strip() or "Untitled Project"
    customer = (customer or "Unassigned").strip() or "Unassigned"
    with _connect() as con:
        row = con.execute(
            "SELECT id FROM projects WHERE lower(name)=lower(?) AND lower(customer)=lower(?) ORDER BY id DESC LIMIT 1",
            (name, customer),
        ).fetchone()
        if row:
            project_id = int(row["id"])
            con.execute("UPDATE projects SET updated_at=? WHERE id=?", (_now(), project_id))
            con.commit()
            return project_id
        ts = _now()
        cur = con.execute(
            "INSERT INTO projects(name, customer, status, notes, created_at, updated_at) VALUES(?,?,?,?,?,?)",
            (name, customer, "Active", notes or "", ts, ts),
        )
        con.commit()
        return int(cur.lastrowid)


def create_project(name: str, customer: str = "", notes: str = "", status: str = "Active") -> int:
    name = (name or "Untitled Project").strip() or "Untitled Project"
    customer = (customer or "Unassigned").strip() or "Unassigned"
    ts = _now()
    with _connect() as con:
        cur = con.execute(
            "INSERT INTO projects(name, customer, status, notes, created_at, updated_at) VALUES(?,?,?,?,?,?)",
            (name, customer, status or "Active", notes or "", ts, ts),
        )
        con.commit()
        return int(cur.lastrowid)


def save_artifact(
    project_id: int,
    artifact_type: str,
    title: str,
    *,
    original_prompt: str = "",
    ai_output: str = "",
    structured_data: dict | list | None = None,
    status: str = "Complete",
) -> int:
    ts = _now()
    with _connect() as con:
        cur = con.execute(
            """
            INSERT INTO artifacts(project_id, artifact_type, title, original_prompt, ai_output, structured_json, status, created_at, updated_at)
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (int(project_id), artifact_type, title or artifact_type, original_prompt or "", ai_output or "", json.dumps(structured_data or {}, ensure_ascii=False), status or "Complete", ts, ts),
        )
        con.execute("UPDATE projects SET updated_at=? WHERE id=?", (ts, int(project_id)))
        con.commit()
        return int(cur.lastrowid)


def list_artifacts(project_id: int) -> list[dict[str, Any]]:
    with _connect() as con:
        rows = con.execute("SELECT * FROM artifacts WHERE project_id=? ORDER BY updated_at DESC, id DESC", (int(project_id),)).fetchall()
    return [
        {
            "id": int(r["id"]),
            "project_id": int(r["project_id"]),
            "artifact_type": r["artifact_type"],
            "type": r["artifact_type"],
            "title": r["title"],
            "original_prompt": r["original_prompt"],
            "ai_output": r["ai_output"],
            "structured_data": json.loads(r["structured_json"] or "{}"),
            "payload": json.loads(r["structured_json"] or "{}"),
            "status": r["status"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
            "date": r["created_at"],
        }
        for r in rows
    ]


def list_projects(limit: int = 500) -> list[dict]:
    with _connect() as con:
        rows = con.execute(
            """
            SELECT p.*,
                   SUM(CASE WHEN a.artifact_type='virtual' THEN 1 ELSE 0 END) AS virtual_count,
                   SUM(CASE WHEN a.artifact_type='quote' THEN 1 ELSE 0 END) AS quote_count,
                   SUM(CASE WHEN a.artifact_type='spec_sample' THEN 1 ELSE 0 END) AS spec_count
            FROM projects p
            LEFT JOIN artifacts a ON a.project_id=p.id
            GROUP BY p.id
            ORDER BY p.updated_at DESC, p.id DESC
            LIMIT ?
            """,
            (int(limit),),
        ).fetchall()
    result = []
    for row in rows:
        item = _project_dict(row)
        item.update({"virtual_count": int(row["virtual_count"] or 0), "quote_count": int(row["quote_count"] or 0), "spec_count": int(row["spec_count"] or 0)})
        artifacts = list_artifacts(item["id"])
        if artifacts:
            item["payload"] = artifacts[0]["structured_data"]
            item["type"] = artifacts[0]["artifact_type"]
        else:
            item["payload"] = {}
            item["type"] = "project"
        result.append(item)
    return result


def get_project(project_id: int) -> dict[str, Any] | None:
    with _connect() as con:
        row = con.execute("SELECT * FROM projects WHERE id=?", (int(project_id),)).fetchone()
    return _project_dict(row) if row else None


def save_project(kind: str, customer: str, project: str, payload: dict) -> int:
    project_id = get_or_create_project(project or kind, customer)
    kind_map = {
        "Spec Sample Order": "spec_sample",
        "Quote": "quote",
        "Virtual / Design": "virtual",
        "Virtual Request": "virtual",
        "Perfectly Packaged": "virtual",
        "Blank Sample": "blank_sample",
    }
    artifact_type = kind_map.get(kind, kind.lower().replace(" ", "_"))
    output = str(payload.get("order") or payload.get("quote") or "")
    prompt = str(payload.get("request") or payload.get("Request") or "")
    title = str(payload.get("title") or kind)
    save_artifact(project_id, artifact_type, title, original_prompt=prompt, ai_output=output, structured_data=payload)
    return project_id


def delete_project(project_id: int) -> None:
    with _connect() as con:
        con.execute("DELETE FROM projects WHERE id=?", (int(project_id),))
        con.commit()
    folder = FILES_DIR / str(int(project_id))
    if folder.exists():
        for path in folder.iterdir():
            if path.is_file():
                path.unlink(missing_ok=True)
        try:
            folder.rmdir()
        except OSError:
            pass


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
    projects = []
    for project in list_projects():
        item = dict(project)
        item["artifacts"] = list_artifacts(project["id"])
        projects.append(item)
    return json.dumps(projects, indent=2, ensure_ascii=False)

"""Small SQLite persistence layer for the demo application."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv("SENTINELX_DB_PATH", os.getenv("DATABASE_PATH", str(ROOT / "reports" / "sentinelx.db"))))
ALERTS_PATH = ROOT / "data" / "sample_alerts.json"


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize() -> None:
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                username TEXT NOT NULL,
                source_ip TEXT NOT NULL,
                asset TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                description TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS incidents (
                incident_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                anchor_alert_id TEXT NOT NULL,
                incident_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                confidence INTEGER NOT NULL,
                affected_user TEXT NOT NULL,
                affected_asset TEXT NOT NULL,
                source_ip TEXT NOT NULL,
                summary TEXT NOT NULL,
                score_reasons_json TEXT NOT NULL,
                evidence_json TEXT NOT NULL,
                timeline_json TEXT NOT NULL,
                recommended_actions_json TEXT NOT NULL,
                alert_ids_json TEXT NOT NULL,
                response_status TEXT NOT NULL DEFAULT 'PENDING APPROVAL',
                approval_at TEXT,
                executed_at TEXT,
                verification_status TEXT NOT NULL DEFAULT 'NOT RUN',
                verification_summary TEXT,
                final_status TEXT NOT NULL DEFAULT 'INVESTIGATING'
            );
            """
        )
        count = db.execute("SELECT COUNT(*) AS count FROM alerts").fetchone()["count"]
        if count == 0:
            seed = json.loads(ALERTS_PATH.read_text(encoding="utf-8"))
            db.executemany(
                """INSERT INTO alerts
                (alert_id, timestamp, event_type, username, source_ip, asset, severity, status, description)
                VALUES (:alert_id, :timestamp, :event_type, :username, :source_ip, :asset, :severity, :status, :description)""",
                seed,
            )
        db.commit()


def rows(query: str, parameters: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with connect() as db:
        return [dict(row) for row in db.execute(query, parameters).fetchall()]


def row(query: str, parameters: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    with connect() as db:
        result = db.execute(query, parameters).fetchone()
        return dict(result) if result else None


def execute(query: str, parameters: tuple[Any, ...] = ()) -> None:
    with connect() as db:
        db.execute(query, parameters)
        db.commit()


def upsert_incident(incident: dict[str, Any], incident_id: str, created_at: str) -> None:
    with connect() as db:
        db.execute(
            """INSERT OR REPLACE INTO incidents
            (incident_id, created_at, anchor_alert_id, incident_type, severity, risk_score, confidence,
             affected_user, affected_asset, source_ip, summary, score_reasons_json, evidence_json,
             timeline_json, recommended_actions_json, alert_ids_json, response_status, approval_at,
             executed_at, verification_status, verification_summary, final_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    COALESCE((SELECT response_status FROM incidents WHERE incident_id = ?), 'PENDING APPROVAL'),
                    (SELECT approval_at FROM incidents WHERE incident_id = ?),
                    (SELECT executed_at FROM incidents WHERE incident_id = ?),
                    COALESCE((SELECT verification_status FROM incidents WHERE incident_id = ?), 'NOT RUN'),
                    (SELECT verification_summary FROM incidents WHERE incident_id = ?),
                    COALESCE((SELECT final_status FROM incidents WHERE incident_id = ?), 'INVESTIGATING'))""",
            (
                incident_id,
                created_at,
                incident["anchor_alert_id"],
                incident["incident_type"],
                incident["severity"],
                incident["risk_score"],
                incident["confidence"],
                incident["affected_user"],
                incident["affected_asset"],
                incident["source_ip"],
                incident["summary"],
                json.dumps(incident["score_reasons"]),
                json.dumps(incident["evidence"]),
                json.dumps(incident["timeline"]),
                json.dumps(incident["recommended_actions"]),
                json.dumps(incident["alert_ids"]),
                incident_id,
                incident_id,
                incident_id,
                incident_id,
                incident_id,
                incident_id,
            ),
        )
        db.commit()


def decode_incident(item: dict[str, Any]) -> dict[str, Any]:
    for key in ("score_reasons", "evidence", "timeline", "recommended_actions", "alert_ids"):
        item[key] = json.loads(item.pop(f"{key}_json"))
    return item

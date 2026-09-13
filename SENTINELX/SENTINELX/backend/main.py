"""SENTINELX FastAPI application.

All actions are simulations over synthetic records. No endpoint, identity, or
network control is ever performed by this application.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent.investigator import investigate_alerts
from backend.database import decode_incident, execute, initialize, row, rows, upsert_incident


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"

app = FastAPI(title="SENTINELX SOC API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InvestigationRequest(BaseModel):
    alert_id: str


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def get_incident(incident_id: str) -> dict:
    item = row("SELECT * FROM incidents WHERE incident_id = ?", (incident_id,))
    if not item:
        raise HTTPException(status_code=404, detail="Incident not found")
    return decode_incident(item)


def incident_summary(item: dict) -> dict:
    return {
        "incident_id": item["incident_id"],
        "incident_type": item["incident_type"],
        "severity": item["severity"],
        "risk_score": item["risk_score"],
        "confidence": item["confidence"],
        "affected_user": item["affected_user"],
        "affected_asset": item["affected_asset"],
        "response_status": item["response_status"],
        "verification_status": item["verification_status"],
        "final_status": item["final_status"],
        "created_at": item["created_at"],
    }


@app.on_event("startup")
def on_startup() -> None:
    initialize()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "SENTINELX", "mode": "synthetic-demo"}


@app.get("/api/alerts")
def list_alerts() -> dict:
    return {"alerts": rows("SELECT * FROM alerts ORDER BY timestamp DESC")}


@app.get("/api/dashboard")
def dashboard() -> dict:
    alerts = rows("SELECT * FROM alerts ORDER BY timestamp DESC")
    incidents = [decode_incident(item) for item in rows("SELECT * FROM incidents ORDER BY created_at DESC")]
    critical = sum(1 for alert in alerts if alert["severity"] == "CRITICAL")
    active = sum(1 for item in incidents if item["final_status"] != "RESOLVED")
    risk_levels = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for item in incidents:
        risk_levels[item["severity"]] = risk_levels.get(item["severity"], 0) + 1
    response_status = {}
    for item in incidents:
        response_status[item["response_status"]] = response_status.get(item["response_status"], 0) + 1
    return {
        "total_alerts": len(alerts),
        "critical_alerts": critical,
        "active_incidents": active,
        "investigations": len(incidents),
        "risk_levels": risk_levels,
        "response_status": response_status,
        "recent_events": alerts[:6],
        "latest_incident": incident_summary(incidents[0]) if incidents else None,
    }


@app.get("/api/incidents")
def list_incidents() -> dict:
    incidents = [decode_incident(item) for item in rows("SELECT * FROM incidents ORDER BY created_at DESC")]
    return {"incidents": [incident_summary(item) for item in incidents]}


@app.get("/api/incidents/{incident_id}")
def read_incident(incident_id: str) -> dict:
    return get_incident(incident_id)


@app.post("/api/investigations")
def start_investigation(request: InvestigationRequest) -> dict:
    alerts = rows("SELECT * FROM alerts")
    try:
        investigation = investigate_alerts(alerts, request.alert_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    existing = row("SELECT incident_id FROM incidents WHERE anchor_alert_id = ?", (request.alert_id,))
    incident_id = existing["incident_id"] if existing else f"INC-{uuid4().hex[:8].upper()}"
    upsert_incident(investigation, incident_id, now())
    for alert_id in investigation["alert_ids"]:
        execute("UPDATE alerts SET status = 'UNDER INVESTIGATION' WHERE alert_id = ?", (alert_id,))
    return get_incident(incident_id)


@app.post("/api/incidents/{incident_id}/approve")
def approve_response(incident_id: str) -> dict:
    incident = get_incident(incident_id)
    if incident["final_status"] == "RESOLVED":
        raise HTTPException(status_code=409, detail="Resolved incidents do not need another approval")
    execute(
        "UPDATE incidents SET response_status = 'APPROVED', approval_at = ?, final_status = 'RESPONSE READY' WHERE incident_id = ?",
        (now(), incident_id),
    )
    return get_incident(incident_id)


@app.post("/api/incidents/{incident_id}/execute")
def execute_response(incident_id: str) -> dict:
    incident = get_incident(incident_id)
    if incident["response_status"] != "APPROVED":
        raise HTTPException(status_code=409, detail="Human approval is required before simulated execution")
    execute(
        "UPDATE incidents SET response_status = 'EXECUTED (SIMULATED)', executed_at = ?, final_status = 'VERIFYING' WHERE incident_id = ?",
        (now(), incident_id),
    )
    return {
        "incident": get_incident(incident_id),
        "simulated_actions": [action["label"] for action in incident["recommended_actions"]],
        "safety_note": "No real account, endpoint, firewall, or network state was changed.",
    }


@app.post("/api/incidents/{incident_id}/verify")
def verify_response(incident_id: str) -> dict:
    incident = get_incident(incident_id)
    if incident["response_status"] != "EXECUTED (SIMULATED)":
        raise HTTPException(status_code=409, detail="Execute the approved simulated response first")
    post_response_events = [
        {"event": "EDR heartbeat", "result": "Healthy", "detail": "No suspicious process restarted."},
        {"event": "Identity telemetry", "result": "Clear", "detail": "No new sessions from the flagged source."},
        {"event": "Network monitor", "result": "Clear", "detail": "No repeat connections to the test destination."},
    ]
    summary = "Verification passed: suspicious activity was not observed after the simulated controls."
    execute(
        "UPDATE incidents SET verification_status = 'THREAT CONTAINED', verification_summary = ?, final_status = 'RESOLVED', response_status = 'COMPLETED' WHERE incident_id = ?",
        (summary, incident_id),
    )
    for alert_id in incident["alert_ids"]:
        execute("UPDATE alerts SET status = 'RESOLVED' WHERE alert_id = ?", (alert_id,))
    return {
        "incident": get_incident(incident_id),
        "post_response_events": post_response_events,
        "verification": "PASSED",
        "summary": summary,
    }


@app.get("/api/reports/{incident_id}")
def report(incident_id: str) -> dict:
    incident = get_incident(incident_id)
    payload = {
        "report_id": f"RPT-{incident_id}",
        "generated_at": now(),
        "incident": incident,
        "final_status": incident["final_status"],
        "report_title": f"{incident['incident_type']} | {incident['severity']}",
    }
    report_path = ROOT / "reports" / f"{incident_id}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


if FRONTEND.exists():
    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")


@app.get("/")
def root() -> FileResponse:
    return FileResponse(FRONTEND / "index.html")

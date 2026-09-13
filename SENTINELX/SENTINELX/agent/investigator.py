"""Transparent, deterministic SOC investigation logic.

The agent is deliberately local and rule-based so the demo works offline. The
inputs and outputs are shaped like an AI tool call, making it straightforward
to replace this module with a hosted model later without changing the UI.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


DEMO_PATTERN = {
    "multiple_failed_logins",
    "successful_unusual_login",
    "privilege_escalation",
    "malware_detection",
    "suspicious_process",
    "unusual_network_activity",
    "sensitive_resource_access",
}


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _severity(score: int) -> str:
    if score >= 81:
        return "CRITICAL"
    if score >= 61:
        return "HIGH"
    if score >= 31:
        return "MEDIUM"
    return "LOW"


def investigate_alerts(alerts: list[dict[str, Any]], anchor_alert_id: str) -> dict[str, Any]:
    """Correlate synthetic alerts and return an incident investigation bundle."""

    anchor = next((a for a in alerts if a["alert_id"] == anchor_alert_id), None)
    if anchor is None:
        raise ValueError(f"Alert {anchor_alert_id} was not found")

    anchor_time = _parse_time(anchor["timestamp"])
    related = []
    for alert in alerts:
        same_identity = alert["username"] == anchor["username"]
        same_asset = alert["asset"] == anchor["asset"]
        same_ip = alert["source_ip"] == anchor["source_ip"]
        within_window = abs((_parse_time(alert["timestamp"]) - anchor_time).total_seconds()) <= 7200
        if within_window and (same_identity or same_asset or same_ip):
            related.append(alert)

    related.sort(key=lambda item: item["timestamp"])
    event_types = {item["event_type"] for item in related}
    is_demo_compromise = DEMO_PATTERN.issubset(event_types)

    if is_demo_compromise:
        risk_score = 91
        confidence = 94
        incident_type = "Account Compromise"
        reasons = [
            {"label": "Multiple failed authentication attempts", "points": 18},
            {"label": "Successful login from unusual source IP", "points": 15},
            {"label": "Privilege escalation after login", "points": 15},
            {"label": "Malware / suspicious process evidence", "points": 16},
            {"label": "Sensitive resource access", "points": 14},
            {"label": "Unusual outbound network activity", "points": 13},
        ]
        summary = (
            f"The identity {anchor['username']} shows a complete compromise sequence: "
            "credential pressure, an unusual successful login, privilege escalation, "
            "execution of a suspicious process, and sensitive data access. The correlated "
            "signals are consistent with an account takeover and possible data staging."
        )
        actions = [
            {"key": "isolate_endpoint", "label": "Isolate endpoint", "reason": "Stop suspicious execution on the affected asset."},
            {"key": "disable_account", "label": "Disable account", "reason": "Prevent further use of the compromised identity."},
            {"key": "block_ip", "label": "Block suspicious IP", "reason": "Cut off the observed external source."},
            {"key": "create_incident", "label": "Create incident", "reason": "Preserve an auditable response record."},
            {"key": "notify_analyst", "label": "Notify analyst", "reason": "Route the case for human follow-up."},
        ]
    else:
        score = 20
        reasons = []
        if "multiple_failed_logins" in event_types:
            score += 20
            reasons.append({"label": "Repeated failed authentication", "points": 20})
        if "successful_unusual_login" in event_types:
            score += 25
            reasons.append({"label": "Unusual successful login", "points": 25})
        if "privilege_escalation" in event_types:
            score += 20
            reasons.append({"label": "Privilege escalation", "points": 20})
        if "malware_detection" in event_types or "suspicious_process" in event_types:
            score += 20
            reasons.append({"label": "Malware or suspicious process", "points": 20})
        if "sensitive_resource_access" in event_types:
            score += 15
            reasons.append({"label": "Sensitive resource access", "points": 15})
        risk_score = min(score, 100)
        confidence = min(90, 58 + len(related) * 6)
        incident_type = "Suspicious Activity"
        summary = (
            f"Correlated {len(related)} alert(s) around {anchor['username']} on {anchor['asset']}. "
            "The available evidence supports continued analyst review."
        )
        actions = [
            {"key": "create_incident", "label": "Create incident", "reason": "Preserve an auditable response record."},
            {"key": "notify_analyst", "label": "Notify analyst", "reason": "Route the case for human follow-up."},
        ]

    evidence = []
    evidence_map = {
        "multiple_failed_logins": ("Failed authentication attempts", "Credential pressure detected from the same source."),
        "successful_unusual_login": ("Unusual login", "A successful session originated from a new or anomalous IP."),
        "privilege_escalation": ("Privilege escalation", "The account acquired elevated access after authentication."),
        "malware_detection": ("Malware detection", "Synthetic endpoint telemetry identified a known-bad test artifact."),
        "suspicious_process": ("Suspicious process", "A process outside the user's baseline executed on the asset."),
        "unusual_network_activity": ("Unusual network activity", "Outbound traffic deviated from the asset baseline."),
        "sensitive_resource_access": ("Sensitive resource access", "A protected university resource was accessed."),
    }
    for alert in related:
        if alert["event_type"] in evidence_map:
            label, detail = evidence_map[alert["event_type"]]
            evidence.append({
                "label": label,
                "detail": detail,
                "alert_id": alert["alert_id"],
                "severity": alert["severity"],
            })

    timeline = [
        {
            "timestamp": item["timestamp"],
            "title": item["event_type"].replace("_", " ").title(),
            "alert_id": item["alert_id"],
            "description": item.get("description", "Synthetic security telemetry correlated by the agent."),
            "severity": item["severity"],
        }
        for item in related
    ]
    return {
        "anchor_alert_id": anchor_alert_id,
        "alert_ids": [item["alert_id"] for item in related],
        "incident_type": incident_type,
        "severity": _severity(risk_score),
        "risk_score": risk_score,
        "confidence": confidence,
        "affected_user": anchor["username"],
        "affected_asset": anchor["asset"],
        "source_ip": anchor["source_ip"],
        "summary": summary,
        "score_reasons": reasons,
        "evidence": evidence,
        "timeline": timeline,
        "recommended_actions": actions,
        "related_alert_count": len(related),
    }

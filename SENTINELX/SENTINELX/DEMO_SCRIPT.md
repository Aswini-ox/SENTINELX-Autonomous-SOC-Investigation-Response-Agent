# SENTINELX 3–5 Minute Demo Script

## 0:00–0:30 — Problem

> Modern SOC teams receive thousands of security alerts every day. Manually correlating and investigating these alerts can cause alert fatigue and delayed response. SENTINELX addresses this problem through an autonomous, evidence-driven SOC investigation agent.

## 0:30–1:00 — Dashboard

Open the dashboard and show the operating path:

```text
Alerts → Incidents → Risk → Investigation
```

Point out Total Alerts, Critical Alerts, Active Incidents, Investigations, risk posture, and recent telemetry.

## 1:00–2:00 — Investigation

Open **Alerts** and trigger the `ALT-2401` Account Compromise scenario for `maya.patel`.

Show the correlated chain:

```text
15 failed logins → unusual login → privilege escalation → suspicious process
```

Then show the AI investigation workspace with the full seven-event correlation and incident summary.

## 2:00–2:30 — Evidence & Risk

Show:

- Risk: **91/100**
- Severity: **CRITICAL**
- Confidence: **94%**
- Evidence cards linked to synthetic alert IDs
- Chronological incident timeline

Explain that every scoring contributor is visible and auditable.

## 2:30–3:30 — Response

Open **Response Center** and show the recommended defensive actions:

- Isolate endpoint
- Disable account
- Block suspicious IP
- Create incident
- Notify analyst

Click **Approve response plan**, then **Execute simulated response**. Emphasize that no real endpoint, account, firewall, or network state is modified.

## 3:30–4:00 — Verification

Click **Run verification** and show:

```text
Verification → Threat Contained → Incident Resolved
```

Point out the simulated EDR heartbeat, identity telemetry, and network monitor checks.

## 4:00–4:30 — Final Report

Click **Generate final report** and show the incident type, risk score, evidence, response status, verification result, and final `RESOLVED` state.

## 4:30–5:00 — Innovation

> Unlike a traditional alert dashboard, SENTINELX correlates alerts, investigates incidents using evidence, explains its risk assessment, recommends defensive actions, and verifies the outcome through a self-correcting investigation loop.

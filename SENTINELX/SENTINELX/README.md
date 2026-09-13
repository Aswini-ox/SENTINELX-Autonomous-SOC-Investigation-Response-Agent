# SENTINELX

## Autonomous SOC Investigation & Response Agent

SENTINELX is a university hackathon prototype for Problem Statement 9. It demonstrates how an autonomous SOC layer can move from synthetic security alerts to a transparent investigation, human-approved simulated response, post-response verification, and a final incident report.

> **Safety boundary:** this project uses synthetic data only. Endpoint isolation, account disabling, IP blocking, analyst notification, and every other response action are simulated database state changes. No real account, endpoint, firewall, or network is touched.

## What It Demonstrates

- Alert ingestion from `data/sample_alerts.json` into SQLite.
- Normalization and alert management with searchable synthetic telemetry.
- Correlation by identity, asset, source IP, and a two-hour time window.
- A local rule-based investigation agent that works without external AI credentials.
- Evidence cards and a chronological incident timeline.
- Transparent 0–100 risk scoring and confidence scoring.
- Human approval before simulated containment.
- Simulated endpoint isolation, account disablement, IP blocking, case creation, and analyst notification.
- Verification with simulated post-response events.
- A final incident report containing the full audit trail.

## Project Structure

```text
SENTINELX/
├── agent/
│   ├── __init__.py
│   └── investigator.py       # Local correlation and scoring engine
├── backend/
│   ├── __init__.py
│   ├── database.py            # SQLite schema, seed, and persistence
│   └── main.py                # FastAPI routes and static file serving
├── data/
│   └── sample_alerts.json     # Synthetic university SOC alerts
├── frontend/
│   ├── app.js                 # API calls and UI workflow
│   ├── index.html             # Dashboard sections
│   └── styles.css             # Dark SOC interface
├── reports/                   # SQLite database is created here at runtime
├── DEMO_SCRIPT.md             # 3–5 minute presentation script
├── .env.example
├── requirements.txt
└── run_local.py
```

## Setup

Python 3.10+ is recommended.

```bash
cd SENTINELX
python -m venv .venv
```

Activate the environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

No API key is required. `.env.example` documents the optional future AI provider configuration.

## Run

```bash
python run_local.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). FastAPI serves both the API and the frontend from the same process.

## 3–5 Minute Demo Flow

1. Open **Alerts** and point out the synthetic queue: failed logins, unusual login, privilege escalation, malware, suspicious process, network activity, and sensitive resource access.
2. Click **Investigate** on `ALT-2401` for `maya.patel`.
3. Show the **Investigation workspace**: seven correlated events, `Account Compromise`, `91/100` risk, `94%` confidence, factor-by-factor scoring, and the timeline.
4. Open **Evidence** and explain that each evidence card links to a synthetic alert ID.
5. Move to **Response Center**. Explain the human-in-the-loop gate, then click **Approve response plan**.
6. Click **Execute simulated response**. Emphasize the safety note: the controls update only the prototype's state.
7. Click **Run verification** and show the three clear post-response checks.
8. Click **Generate final report**. Close on `RESOLVED`, `CRITICAL`, `91/100`, and `94%`.

## Demo Incident Data

The main scenario uses the following synthetic chain:

| Alert | Event | Identity | Asset | Severity |
|---|---|---|---|---|
| ALT-2401 | 15 failed logins | maya.patel | LAPTOP-MP-07 | HIGH |
| ALT-2402 | Successful unusual login | maya.patel | LAPTOP-MP-07 | CRITICAL |
| ALT-2403 | Privilege escalation | maya.patel | LAPTOP-MP-07 | CRITICAL |
| ALT-2404 | Malware detection | maya.patel | LAPTOP-MP-07 | CRITICAL |
| ALT-2405 | Suspicious process | maya.patel | LAPTOP-MP-07 | HIGH |
| ALT-2406 | Unusual network activity | maya.patel | LAPTOP-MP-07 | HIGH |
| ALT-2407 | Sensitive resource access | maya.patel | LAPTOP-MP-07 | CRITICAL |

Expected case result: **Account Compromise**, **CRITICAL**, **91/100**, **94% confidence**, **RESOLVED after simulated response**.

## Scoring Model

The demo scenario intentionally exposes these contributors:

| Contributor | Points |
|---|---:|
| Multiple failed authentication attempts | 18 |
| Successful login from unusual source IP | 15 |
| Privilege escalation after login | 15 |
| Malware / suspicious process evidence | 16 |
| Sensitive resource access | 14 |
| Unusual outbound network activity | 13 |
| **Total** | **91** |

Risk bands are LOW `0–30`, MEDIUM `31–60`, HIGH `61–80`, and CRITICAL `81–100`. Confidence is derived from the number and quality of correlated indicators; the complete seeded scenario is intentionally calibrated to `94%` for the hackathon demonstration.

## Architecture

```text
Synthetic JSON alerts
        ↓
FastAPI / SQLite persistence
        ↓
Local investigation agent
  correlation → evidence → timeline → score
        ↓
Frontend analyst review
        ↓
Human approval gate
        ↓
Simulated response state
        ↓
Simulated post-response telemetry
        ↓
Verification → report
```

The `agent/investigator.py` module is intentionally shaped as a replaceable agent boundary. A future LLM integration can call the same investigation contract while retaining the local rule-based fallback for demos, testing, and offline use.

## API Surface

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/dashboard` | KPI and recent telemetry data |
| GET | `/api/alerts` | Synthetic alert queue |
| POST | `/api/investigations` | Start or refresh a correlated case |
| GET | `/api/incidents` | Case list |
| GET | `/api/incidents/{id}` | Full investigation bundle |
| POST | `/api/incidents/{id}/approve` | Human approval gate |
| POST | `/api/incidents/{id}/execute` | Simulated response execution |
| POST | `/api/incidents/{id}/verify` | Simulated containment verification |
| GET | `/api/reports/{id}` | Final report payload |

## Resetting the Demo

Stop the server and delete `reports/sentinelx.db`. The next run reseeds all synthetic alerts from `data/sample_alerts.json`.

## Hackathon Talking Points

- **Autonomy with guardrails:** the agent correlates and recommends, but a human must approve response.
- **Explainability:** every score has visible contributors, evidence IDs, and a timeline.
- **Self-correction:** verification can confirm containment and would route a remaining threat back to investigation.
- **Offline-first:** the rule-based fallback makes the demo reliable without secrets or external services.
- **Safe by design:** all actions are simulated and auditable.

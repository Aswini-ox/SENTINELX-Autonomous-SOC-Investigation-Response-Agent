# 🛡️ SENTINELX
LIVE : https://sentinelx-autonomous-soc-investigation.onrender.com

## Autonomous SOC Investigation & Response Agent

> **From Alert Overload to Evidence-Driven Action**

SENTINELX is an **Autonomous Security Operations Center (SOC) Investigation & Response Agent** designed to reduce the time and effort required to investigate correlated security alerts.

Instead of treating every security alert independently, SENTINELX correlates related events, builds an investigation timeline, analyzes evidence, calculates risk, recommends defensive actions, keeps a human approval gate, executes a **simulated response**, and verifies whether the threat has been contained.

### ⚠️ Safety Boundary

SENTINELX uses **synthetic security data only**.

All response actions—including endpoint isolation, account disabling, IP blocking, case creation, and analyst notification—are **simulated database state changes**.

No real endpoint, account, firewall, network, or production system is modified.

---

# 🎯 Problem Statement

Modern SOC teams receive thousands of security alerts every day.

The major challenge is not simply detecting alerts, but:

* Correlating related alerts
* Identifying real attack patterns
* Investigating incidents quickly
* Understanding why an alert is risky
* Choosing the correct response
* Verifying whether the response worked

Manual investigation can result in **alert fatigue, delayed response, inconsistent decisions, and increased analyst workload**.

SENTINELX addresses this by providing an evidence-driven investigation workflow that connects detection, investigation, response, and verification.

---

# 💡 Our Solution

SENTINELX transforms disconnected security alerts into an actionable incident investigation.

```text
Security Alerts
      ↓
Alert Normalization
      ↓
Alert Correlation
      ↓
Investigation Agent
      ↓
Evidence Collection
      ↓
Risk & Confidence Assessment
      ↓
Human Approval
      ↓
Simulated Response
      ↓
Post-Response Verification
      ↓
Final Incident Report
```

The core philosophy is:

> **Observe → Correlate → Investigate → Assess → Recommend → Approve → Respond → Verify**

---

# 🚀 Key Features

### 🔍 1. Alert Ingestion

Loads synthetic SOC telemetry from:

```text
data/sample_alerts.json
```

The alerts are persisted into a local SQLite database.

---

### 🔗 2. Intelligent Alert Correlation

Related alerts are grouped using:

* Identity
* Asset
* Source IP
* Time window

SENTINELX uses a **two-hour correlation window** to identify connected security events.

---

### 🤖 3. Investigation Agent

The local investigation agent analyzes correlated events and determines the likely incident type.

The current prototype uses a **local rule-based investigation engine**, allowing the system to work without external AI credentials.

The investigation layer is designed as a replaceable boundary for future LLM/AI integration.

---

### 🧾 4. Evidence-Driven Investigation

Each investigation provides:

* Evidence cards
* Alert references
* Investigation factors
* Chronological timeline
* Incident classification

This makes the investigation transparent and auditable.

---

### 📊 5. Risk Scoring

SENTINELX calculates a transparent risk score from `0–100`.

Risk levels:

|  Score | Risk Level  |
| -----: | ----------- |
|   0–30 | 🟢 LOW      |
|  31–60 | 🟡 MEDIUM   |
|  61–80 | 🟠 HIGH     |
| 81–100 | 🔴 CRITICAL |

The system also provides a confidence score based on the correlated security indicators.

---

### 👤 6. Human-in-the-Loop Approval

SENTINELX does not blindly execute defensive actions.

The investigation agent first creates a response plan.

A human analyst must approve the plan before simulated response execution.

```text
AI Investigation
      ↓
Response Recommendation
      ↓
Human Approval
      ↓
Response Execution
```

This provides an important safety guardrail for autonomous security operations.

---

### 🛡️ 7. Simulated Response

The prototype demonstrates actions such as:

* Endpoint isolation
* Account disabling
* IP blocking
* Incident/case creation
* Analyst notification

These are simulated state changes inside the application.

---

### ✅ 8. Post-Response Verification

SENTINELX doesn't stop after executing a response.

It performs simulated post-response checks to determine whether the threat has been contained.

```text
Response
   ↓
Verification
   ↓
Threat Contained?
   ├── YES → Incident Resolved
   └── NO  → Continue Investigation
```

This creates a **closed-loop investigation workflow**.

---

### 📄 9. Final Incident Report

The system generates a final incident report containing:

* Incident classification
* Affected identity
* Affected asset
* Risk score
* Confidence score
* Evidence
* Timeline
* Response actions
* Verification result
* Audit trail

---

# 🧪 Demo Scenario — Account Compromise

The main demonstration uses a synthetic account-compromise scenario involving:

**User:** `maya.patel`
**Asset:** `LAPTOP-MP-07`

### Attack Chain

```text
15 Failed Login Attempts
          ↓
Unusual Successful Login
          ↓
Privilege Escalation
          ↓
Malware Detection
          ↓
Suspicious Process
          ↓
Unusual Network Activity
          ↓
Sensitive Resource Access
```

### Alert Chain

| Alert    | Event                     | Severity |
| -------- | ------------------------- | -------- |
| ALT-2401 | 15 failed logins          | HIGH     |
| ALT-2402 | Successful unusual login  | CRITICAL |
| ALT-2403 | Privilege escalation      | CRITICAL |
| ALT-2404 | Malware detection         | CRITICAL |
| ALT-2405 | Suspicious process        | HIGH     |
| ALT-2406 | Unusual network activity  | HIGH     |
| ALT-2407 | Sensitive resource access | CRITICAL |

### Expected Result

```text
Incident:       Account Compromise
Risk Score:     91/100
Severity:       CRITICAL
Confidence:     94%
Final Status:   RESOLVED
```

---

# 📊 Risk Scoring

The demonstration scenario uses the following risk contributors:

| Risk Contributor                        | Points |
| --------------------------------------- | -----: |
| Multiple failed authentication attempts |     18 |
| Successful login from unusual source IP |     15 |
| Privilege escalation after login        |     15 |
| Malware / suspicious process evidence   |     16 |
| Sensitive resource access               |     14 |
| Unusual outbound network activity       |     13 |
| **Total**                               | **91** |

The score is intentionally transparent so that analysts can understand **why** an incident was classified as critical.

---

# 🏗️ System Architecture

```text
┌──────────────────────────────┐
│   Synthetic Security Alerts  │
│     sample_alerts.json       │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│      FastAPI Backend         │
│      Alert Management        │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│        SQLite Database       │
│ Alerts • Incidents • Reports │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│    Investigation Agent       │
│                              │
│ Correlation                  │
│ Evidence                     │
│ Timeline                     │
│ Risk Scoring                 │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│       Analyst Dashboard      │
│                              │
│ Investigation                │
│ Evidence                     │
│ Risk                         │
│ Response                     │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│     Human Approval Gate      │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│     Simulated Response       │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│      Verification Engine     │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│      Final Incident Report   │
└──────────────────────────────┘
```

---

# 🛠️ Technology Stack

| Layer         | Technology                     |
| ------------- | ------------------------------ |
| Frontend      | HTML, CSS, JavaScript          |
| Backend       | Python, FastAPI                |
| Database      | SQLite                         |
| Investigation | Python Rule-Based Agent        |
| Data          | Synthetic JSON Security Alerts |
| API           | REST                           |
| Runtime       | Python 3.10+                   |

---

# 📁 Project Structure

```text
SENTINELX/
│
├── agent/
│   ├── __init__.py
│   └── investigator.py
│
├── backend/
│   ├── __init__.py
│   ├── database.py
│   └── main.py
│
├── data/
│   └── sample_alerts.json
│
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── styles.css
│
├── reports/
│   └── .gitkeep
│
├── DEMO_SCRIPT.md
├── .env.example
├── .gitignore
├── requirements.txt
├── run_local.py
└── README.md
```

---

# ⚙️ Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd SENTINELX
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

#### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

No external AI API key is required for the current prototype.

---

# ▶️ Run the Application

Start SENTINELX using:

```bash
python run_local.py
```

Then open:

```text
http://127.0.0.1:8000
```

FastAPI serves both the backend API and frontend from the same process.

---

# 🔌 API Endpoints

| Method | Endpoint                      | Description                  |
| ------ | ----------------------------- | ---------------------------- |
| GET    | `/api/dashboard`              | Dashboard KPIs and telemetry |
| GET    | `/api/alerts`                 | Retrieve alert queue         |
| POST   | `/api/investigations`         | Start/refresh investigation  |
| GET    | `/api/incidents`              | Retrieve incidents           |
| GET    | `/api/incidents/{id}`         | Get investigation details    |
| POST   | `/api/incidents/{id}/approve` | Approve response             |
| POST   | `/api/incidents/{id}/execute` | Execute simulated response   |
| POST   | `/api/incidents/{id}/verify`  | Verify containment           |
| GET    | `/api/reports/{id}`           | Retrieve final report        |

---

# 🎬 Demo Workflow

The recommended hackathon demonstration is:

```text
1. Open Dashboard
        ↓
2. Show Security Alerts
        ↓
3. Select ALT-2401
        ↓
4. Start Investigation
        ↓
5. Show Correlated Events
        ↓
6. Show Evidence & Timeline
        ↓
7. Show Risk = 91/100
        ↓
8. Show Confidence = 94%
        ↓
9. Review Response Plan
        ↓
10. Human Approval
        ↓
11. Execute Simulated Response
        ↓
12. Run Verification
        ↓
13. Show Threat Contained
        ↓
14. Generate Final Report
        ↓
15. Incident = RESOLVED
```

---

# 💡 What Makes SENTINELX Different?

Traditional SOC dashboards primarily help analysts **view and manage alerts**.

SENTINELX aims to create a complete investigation loop:

### Traditional SOC

```text
Alert
 ↓
Analyst Investigation
 ↓
Manual Decision
 ↓
Manual Response
```

### SENTINELX

```text
Alert
 ↓
Correlation
 ↓
Evidence-Based Investigation
 ↓
Risk Assessment
 ↓
Response Recommendation
 ↓
Human Approval
 ↓
Simulated Response
 ↓
Verification
 ↓
Final Report
```

The key innovation is the **closed-loop investigation and verification workflow**.

---

# 🔐 Safety & Explainability

SENTINELX is designed around three principles:

### 1. Explainability

Every risk assessment is supported by visible evidence and scoring factors.

### 2. Human Control

The response cannot proceed without analyst approval.

### 3. Safe Simulation

All security actions are simulated inside the prototype.

This makes SENTINELX suitable for demonstration, testing, and experimentation without affecting real infrastructure.

---

# 🔮 Future Enhancements

The current prototype provides the foundation for a more advanced autonomous SOC platform.

Future improvements include:

* LLM-powered investigation and reasoning
* RAG-based security knowledge retrieval
* MITRE ATT&CK technique mapping
* Real SIEM integration
* Real-time security telemetry
* Multi-agent SOC architecture
* Automated threat hunting
* Adaptive response planning
* SOAR integration
* Real endpoint security integrations
* Feedback-driven investigation refinement
* Threat intelligence integration
* Graph-based attack-path analysis

The investigation layer is intentionally designed as a **replaceable agent boundary**, allowing future AI/LLM capabilities to be introduced without redesigning the complete application.

---

# 📌 Project Status

**Prototype / Hackathon Demonstration**

Current implementation focuses on:

* Synthetic SOC alerts
* Alert correlation
* Rule-based investigation
* Evidence visualization
* Risk scoring
* Human approval
* Simulated response
* Post-response verification
* Incident reporting

---

# 👥 Team

**SENTINELX Team**

Built as a university hackathon prototype for:

> **Problem Statement 9 — Autonomous SOC Investigation & Response Agent**

---

# 📄 License

This project is intended for educational, research, and hackathon demonstration purposes.

---

## 🛡️ SENTINELX

> **Detect less. Understand more. Respond safely.**

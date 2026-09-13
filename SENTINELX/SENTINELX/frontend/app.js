const state = { alerts: [], dashboard: null, incident: null, report: null, riskChart: null };
const $ = (selector) => document.querySelector(selector);
const api = async (path, options = {}) => {
  const response = await fetch(`/api${path}`, { headers: { "Content-Type": "application/json" }, ...options });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || "Request failed");
  return payload;
};
const escapeHtml = (value = "") => String(value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
const titleCase = (value = "") => value.replaceAll("_", " ").toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase());
const timeOnly = (value) => new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
const dateTime = (value) => new Date(value).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
const severityClass = (value = "") => value.toLowerCase();
const showToast = (message) => { const toast = $("#toast"); toast.textContent = message; toast.classList.add("show"); setTimeout(() => toast.classList.remove("show"), 3300); };

function showView(view) {
  document.querySelectorAll(".view").forEach((section) => section.classList.toggle("active", section.id === `view-${view}`));
  document.querySelectorAll(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.view === view));
  $("#page-label").textContent = view.charAt(0).toUpperCase() + view.slice(1);
  if (view === "incidents") loadIncidents();
}

function renderDashboard() {
  const data = state.dashboard;
  $("#total-alerts").textContent = data.total_alerts;
  $("#critical-alerts").textContent = data.critical_alerts;
  $("#active-incidents").textContent = data.active_incidents;
  $("#investigation-count").textContent = data.investigations;
  $("#nav-alert-count").textContent = data.total_alerts;
  $("#risk-total").textContent = Object.values(data.risk_levels).reduce((sum, value) => sum + value, 0);
  $("#risk-critical").textContent = data.risk_levels.CRITICAL || 0;
  $("#risk-high").textContent = data.risk_levels.HIGH || 0;
  $("#risk-medium").textContent = data.risk_levels.MEDIUM || 0;
  $("#recent-events").innerHTML = data.recent_events.map((event) => `<div class="event-row"><span class="event-marker ${severityClass(event.severity)}"></span><div class="event-body"><b>${escapeHtml(titleCase(event.event_type))}</b><small>${escapeHtml(event.username)} · ${escapeHtml(event.asset)}</small></div><span class="event-time">${timeOnly(event.timestamp)}</span></div>`).join("") || `<p class="empty-copy">No recent events.</p>`;
  renderRiskChart(data.risk_levels);
}

function renderRiskChart(risk) {
  const canvas = $("#risk-chart");
  if (!canvas || typeof Chart === "undefined") return;
  if (state.riskChart) state.riskChart.destroy();
  state.riskChart = new Chart(canvas, { type: "doughnut", data: { labels: ["Critical", "High", "Medium", "Low"], datasets: [{ data: [risk.CRITICAL || 0, risk.HIGH || 0, risk.MEDIUM || 0, risk.LOW || 0], backgroundColor: ["#ff6679", "#f6b954", "#4b8dff", "#66d19e"], borderWidth: 0, spacing: 3 }] }, options: { responsive: true, cutout: "78%", plugins: { legend: { display: false }, tooltip: { enabled: true } } } });
}

function renderAlerts() {
  const query = $("#alert-search").value.toLowerCase().trim();
  const filtered = state.alerts.filter((alert) => [alert.alert_id, alert.username, alert.asset, alert.event_type, alert.source_ip].join(" ").toLowerCase().includes(query));
  $("#alert-summary").textContent = `${filtered.length} alert${filtered.length === 1 ? "" : "s"}`;
  $("#alerts-table").innerHTML = filtered.map((alert) => `<tr><td><span class="alert-id">${escapeHtml(alert.alert_id)}</span><span class="cell-sub">${dateTime(alert.timestamp)}</span></td><td><span class="cell-main">${escapeHtml(titleCase(alert.event_type))}</span><span class="cell-sub">${escapeHtml(alert.description)}</span></td><td><span class="cell-main">${escapeHtml(alert.username)}</span><span class="cell-sub">${escapeHtml(alert.asset)}</span></td><td><span class="cell-main">${escapeHtml(alert.source_ip)}</span></td><td><span class="severity ${severityClass(alert.severity)}">${escapeHtml(alert.severity)}</span></td><td><span class="status-tag ${alert.status.toLowerCase().replaceAll(" ", "-")}">${escapeHtml(alert.status)}</span></td><td><button class="table-action investigate-button" data-alert-id="${escapeHtml(alert.alert_id)}">Investigate →</button></td></tr>`).join("") || `<tr><td colspan="7" class="empty-copy">No alerts match this search.</td></tr>`;
  document.querySelectorAll(".investigate-button").forEach((button) => button.addEventListener("click", () => startInvestigation(button.dataset.alertId)));
}

function scoreMarkup(incident) {
  return `<div class="panel"><div class="case-hero"><div><span class="severity critical">${escapeHtml(incident.severity)}</span><h2>${escapeHtml(incident.incident_type)}</h2><p>${escapeHtml(incident.incident_id)} · ${escapeHtml(incident.affected_user)}</p></div><div class="score-box"><strong>${incident.risk_score}<small>/100</small></strong><small>RISK SCORE</small></div></div><div class="score-bar"><span style="width:${incident.risk_score}%"></span></div><div class="meta-grid"><div class="meta-box"><small>CONFIDENCE</small><b>${incident.confidence}%</b></div><div class="meta-box"><small>ASSET</small><b>${escapeHtml(incident.affected_asset)}</b></div><div class="meta-box"><small>SOURCE IP</small><b>${escapeHtml(incident.source_ip)}</b></div><div class="meta-box"><small>CORRELATED</small><b>${incident.related_alert_count || incident.alert_ids.length} alerts</b></div></div><div class="summary-box">${escapeHtml(incident.summary)}</div><div class="section-heading"><h2>Score contributors</h2><span class="muted-label">TRANSPARENT RULES</span></div><div class="factor-list">${incident.score_reasons.map((reason) => `<div class="factor"><span>${escapeHtml(reason.label)}</span><b>+${reason.points}</b></div>`).join("")}</div></div>`;
}

function timelineMarkup(incident) {
  return `<div class="panel"><div class="section-heading"><div><p class="eyebrow">CORRELATED EVENT PATH</p><h2>Incident timeline</h2></div><span class="muted-label">${incident.timeline.length} EVENTS</span></div><div class="timeline">${incident.timeline.map((item) => `<div class="timeline-item"><time>${dateTime(item.timestamp)} · ${escapeHtml(item.alert_id)}</time><b>${escapeHtml(item.title)}</b><small>${escapeHtml(item.description)}</small></div>`).join("")}</div></div>`;
}

function renderInvestigation() {
  const incident = state.incident;
  if (!incident) return;
  $("#investigation-empty").classList.add("hidden");
  const detail = $("#investigation-detail");
  detail.classList.remove("hidden");
  detail.innerHTML = `<div class="investigation-grid">${scoreMarkup(incident)}${timelineMarkup(incident)}</div><div class="investigation-footer"><button class="secondary-button" id="open-evidence-btn">▣ Review evidence</button><button class="primary-button" id="open-response-btn">Continue to response center →</button></div>`;
  $("#open-evidence-btn").addEventListener("click", () => showView("evidence"));
  $("#open-response-btn").addEventListener("click", () => { renderResponse(); showView("response"); });
  renderEvidence();
  renderResponse();
  $("#generate-report-btn").disabled = false;
}

function renderEvidence() {
  const container = $("#evidence-content");
  if (!state.incident) { container.className = "panel empty-copy"; container.textContent = "Start an investigation to populate the evidence board."; return; }
  container.className = "";
  container.innerHTML = `<div class="evidence-grid">${state.incident.evidence.map((item) => `<article class="evidence-card"><div class="ev-top"><span class="ev-icon">◉</span><span class="severity ${severityClass(item.severity)}">${escapeHtml(item.severity)}</span></div><b>${escapeHtml(item.label)}</b><p>${escapeHtml(item.detail)}</p><small>${escapeHtml(item.alert_id)} · synthetic evidence</small></article>`).join("")}</div><div class="panel" style="margin-top:15px"><div class="section-heading"><div><p class="eyebrow">CHAIN OF REASONING</p><h2>Why the agent correlated these signals</h2></div></div><p class="subcopy" style="line-height:1.7;margin-top:14px">The local investigation agent groups events when identity, asset, or source IP match inside a two-hour window. It then applies a visible rule set, preserving every score contributor for analyst review.</p></div>`;
}

function renderResponse() {
  const container = $("#response-content");
  if (!state.incident) { container.innerHTML = `<div class="panel empty-copy">Start an investigation to stage recommended actions.</div>`; return; }
  const incident = state.incident;
  const actions = incident.recommended_actions.map((action) => `<div class="action-row"><span class="action-check">✓</span><div><b>${escapeHtml(action.label)}</b><small>${escapeHtml(action.reason)}</small></div></div>`).join("");
  const verificationMarkup = incident.response_status === "COMPLETED" ? `<div class="panel post-check-list"><p class="eyebrow">VERIFICATION RESULT</p><div class="post-check"><span class="status-dot"></span><div><strong>EDR heartbeat · HEALTHY</strong>No suspicious process restarted.</div></div><div class="post-check"><span class="status-dot"></span><div><strong>Identity telemetry · CLEAR</strong>No new sessions from the flagged source.</div></div><div class="post-check"><span class="status-dot"></span><div><strong>Network monitor · CLEAR</strong>No repeat connections to the test destination.</div></div></div>` : "";
  let approval = "";
  if (incident.response_status === "PENDING APPROVAL") approval = `<div class="approval-box"><h3>Analyst approval required</h3><p>Review the simulated actions. Execution only updates SENTINELX's synthetic case state.</p><button class="primary-button" id="approve-btn">Approve response plan</button></div>`;
  if (incident.response_status === "APPROVED") approval = `<div class="approval-box"><h3>Plan approved</h3><p>The response is staged. Execute it to generate simulated post-response telemetry.</p><button class="primary-button" id="execute-btn">Execute simulated response</button></div>`;
  if (incident.response_status === "EXECUTED (SIMULATED)") approval = `<div class="approval-box"><h3>Controls simulated</h3><p>Endpoint isolation, account disablement, and IP blocking have been modeled only. Run verification next.</p><button class="primary-button" id="verify-btn">Run verification</button></div>`;
  if (incident.response_status === "COMPLETED") approval = `<div class="approval-box" style="border-color:rgba(102,209,158,.3);background:rgba(102,209,158,.05)"><h3 style="color:var(--green)">Threat contained</h3><p>${escapeHtml(incident.verification_summary || "Verification passed.")}</p><button class="secondary-button" id="report-btn">Generate final report</button></div>`;
  container.innerHTML = `<div class="panel"><div class="section-heading"><div><p class="eyebrow">RECOMMENDED ACTIONS</p><h2>${escapeHtml(incident.incident_type)} response plan</h2></div><span class="severity ${severityClass(incident.severity)}">${escapeHtml(incident.severity)}</span></div><div class="response-actions">${actions}</div><div class="response-status"><span>RESPONSE STATUS</span><b>${escapeHtml(incident.response_status)}</b></div></div><div><div class="panel">${approval}</div>${verificationMarkup}</div>`;
  $("#approve-btn")?.addEventListener("click", approveResponse);
  $("#execute-btn")?.addEventListener("click", executeResponse);
  $("#verify-btn")?.addEventListener("click", verifyResponse);
  $("#report-btn")?.addEventListener("click", generateReport);
}

async function startInvestigation(alertId) {
  try { showToast("Agent correlating related alerts..."); state.incident = await api("/investigations", { method: "POST", body: JSON.stringify({ alert_id: alertId }) }); renderInvestigation(); await loadAll(); showView("investigations"); showToast(`Investigation ${state.incident.incident_id} is ready for review.`); } catch (error) { showToast(error.message); }
}
async function approveResponse() { try { state.incident = await api(`/incidents/${state.incident.incident_id}/approve`, { method: "POST" }); renderResponse(); await loadAll(); showToast("Response plan approved by analyst."); } catch (error) { showToast(error.message); } }
async function executeResponse() { try { const result = await api(`/incidents/${state.incident.incident_id}/execute`, { method: "POST" }); state.incident = result.incident; renderResponse(); await loadAll(); showToast("Simulated controls executed safely."); } catch (error) { showToast(error.message); } }
async function verifyResponse() { try { const result = await api(`/incidents/${state.incident.incident_id}/verify`, { method: "POST" }); state.incident = result.incident; renderResponse(); await loadAll(); showToast("Verification passed. Threat contained."); } catch (error) { showToast(error.message); } }

async function loadIncidents() {
  try { const data = await api("/incidents"); $("#incidents-table").innerHTML = data.incidents.map((item) => `<tr><td><span class="alert-id">${escapeHtml(item.incident_id)}</span><span class="cell-sub">${dateTime(item.created_at)}</span></td><td>${escapeHtml(item.incident_type)}</td><td><span class="severity ${severityClass(item.severity)}">${item.risk_score}/100</span></td><td>${item.confidence}%</td><td>${escapeHtml(item.affected_user)}<span class="cell-sub">${escapeHtml(item.affected_asset)}</span></td><td>${escapeHtml(item.response_status)}</td><td><span class="status-tag ${item.final_status.toLowerCase().replaceAll(" ", "-")}">${escapeHtml(item.final_status)}</span></td></tr>`).join("") || `<tr><td colspan="7" class="empty-copy">No investigations yet.</td></tr>`; } catch (error) { showToast(error.message); }
}

async function generateReport() {
  if (!state.incident) return;
  try { state.report = await api(`/reports/${state.incident.incident_id}`); renderReport(); showView("reports"); showToast("Final incident report generated."); } catch (error) { showToast(error.message); }
}

function renderReport() {
  if (!state.report) return;
  const incident = state.report.incident;
  $("#report-content").className = "panel report-sheet";
  $("#report-content").innerHTML = `<div class="report-header"><div><p class="eyebrow">SENTINELX · FINAL INCIDENT REPORT</p><h2>${escapeHtml(state.report.report_title)}</h2><p class="subcopy">${escapeHtml(incident.incident_id)} · generated ${dateTime(state.report.generated_at)}</p></div><div class="report-meta">STATUS<br><strong style="color:var(--green)">${escapeHtml(incident.final_status)}</strong></div></div><div class="report-sections"><div class="report-section"><h3>EXECUTIVE SUMMARY</h3><p>${escapeHtml(incident.summary)}</p></div><div class="report-section"><h3>RISK &amp; CONFIDENCE</h3><p><strong style="color:var(--red)">${incident.risk_score}/100</strong> risk score · <strong style="color:var(--cyan)">${incident.confidence}%</strong> confidence. Affected user: ${escapeHtml(incident.affected_user)} on ${escapeHtml(incident.affected_asset)}.</p></div><div class="report-section"><h3>EVIDENCE (${incident.evidence.length})</h3><ul>${incident.evidence.map((item) => `<li>${escapeHtml(item.label)} <span style="color:var(--faint)">(${escapeHtml(item.alert_id)})</span></li>`).join("")}</ul></div><div class="report-section"><h3>RESPONSE &amp; VERIFICATION</h3><p>${escapeHtml(incident.verification_summary || "Response is still pending verification.")}</p><p>Response status: <strong style="color:var(--green)">${escapeHtml(incident.response_status)}</strong></p></div><div class="report-section"><h3>TIMELINE</h3><ul>${incident.timeline.map((item) => `<li>${dateTime(item.timestamp)} · ${escapeHtml(item.title)}</li>`).join("")}</ul></div><div class="report-section"><h3>SAFETY NOTE</h3><p>This report is based entirely on simulated university SOC telemetry. No real endpoint, account, IP, firewall, or network state was modified.</p></div></div>`;
}

async function loadAll() { try { const [dashboard, alertData] = await Promise.all([api("/dashboard"), api("/alerts")]); state.dashboard = dashboard; state.alerts = alertData.alerts; renderDashboard(); renderAlerts(); if (state.incident) { state.incident = await api(`/incidents/${state.incident.incident_id}`); renderInvestigation(); } } catch (error) { showToast(`Backend unavailable: ${error.message}`); } }

document.addEventListener("click", (event) => { const target = event.target.closest("[data-view], [data-view-target]"); if (!target) return; showView(target.dataset.view || target.dataset.viewTarget); });
$("#alert-search").addEventListener("input", renderAlerts);
$("#refresh-btn").addEventListener("click", async () => { await loadAll(); showToast("Telemetry refreshed."); });
$("#load-alerts-btn").addEventListener("click", async () => { await loadAll(); showToast("Synthetic alert queue loaded."); });
$("#generate-report-btn").addEventListener("click", generateReport);
loadAll();

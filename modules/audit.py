"""
Audit Trail Module
==================
Logs every significant action with user, timestamp, and details.
Provides a view of recent system activity.
"""

import streamlit as st
from datetime import datetime
from modules.database import db


def log_audit(action: str, details: str, user: str = "Admin", employee_id: str = None):
    """Insert a single audit log entry."""
    doc = {
        "action":      action,
        "details":     details,
        "user":        user,
        "employee_id": employee_id,
        "timestamp":   datetime.utcnow().isoformat(),
    }
    try:
        db.audit_logs.insert_one(doc)
    except Exception:
        pass  # Audit logging must never crash the main flow


def show_audit_trail():
    st.markdown("""
    <div class="page-header">
        <h1>📊 Audit Trail</h1>
        <p>Complete log of all system actions and user activities</p>
    </div>
    """, unsafe_allow_html=True)

    # Fetch last 200 entries
    logs = list(db.audit_logs.find({}) or [])
    # Sort newest-first
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    logs = logs[:200]

    if not logs:
        st.info("No audit records found yet. Actions will appear here as you use the system.")
        return

    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📋</div>
            <div class="metric-value">{len(logs)}</div>
            <div class="metric-label">Total Log Entries</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        unique_actions = len(set(l.get("action","") for l in logs))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">⚡</div>
            <div class="metric-value">{unique_actions}</div>
            <div class="metric-label">Distinct Action Types</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        unique_users = len(set(l.get("user","") for l in logs))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">👤</div>
            <div class="metric-value">{unique_users}</div>
            <div class="metric-label">Active Users</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Build HTML table
    rows_html = ""
    action_colors = {
        "Employee Created": "badge-success",
        "Service Entry Added": "badge-info",
        "Document Uploaded": "badge-info",
        "PDF Generated": "badge-warning",
        "Employee Updated": "badge-warning",
        "Record Deleted": "badge-danger",
    }
    for log in logs:
        ts_raw = log.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_raw).strftime("%d %b %Y  %H:%M:%S")
        except Exception:
            ts = ts_raw[:19].replace("T", "  ")
        action = log.get("action", "—")
        badge_cls = action_colors.get(action, "badge-info")
        emp = log.get("employee_id") or "—"
        rows_html += f"""
        <tr>
            <td style="font-size:0.78rem; color:#888; white-space:nowrap;">{ts}</td>
            <td><span class="badge {badge_cls}">{action}</span></td>
            <td>{log.get("user","—")}</td>
            <td>{emp}</td>
            <td style="max-width:340px; word-break:break-word;">{log.get("details","—")}</td>
        </tr>"""

    st.markdown(f"""
    <div class="section-card" style="overflow-x:auto;">
        <table class="record-table">
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Action</th>
                    <th>User</th>
                    <th>Employee ID</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)
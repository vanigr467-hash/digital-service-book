"""
Dashboard Module
================
Shows system-wide statistics and a quick overview of recent activity.
"""

import streamlit as st
from modules.database import db, is_mock
from modules.audit import log_audit


def show_dashboard():
    st.markdown("""
    <div class="page-header">
        <h1>🏠 Dashboard</h1>
        <p>Digital Service Book Management System — at a glance</p>
    </div>
    """, unsafe_allow_html=True)

    # Connection status
    if is_mock():
        st.warning("⚠️ **Demo Mode**: Running with in-memory storage (session only). "
                   "Set MONGO_URI environment variable to connect to a real MongoDB instance. "
                   "Data will be lost on page refresh.", icon="⚠️")
    else:
        st.success("✅ Connected to MongoDB", icon="✅")

    # ── Aggregate statistics ─────────────────────────────────────────────────
    employees = list(db.employees.find({}) or [])
    total_employees = len(employees)

    total_promotions = sum(len(e.get("promotions", [])) for e in employees)
    total_transfers  = sum(len(e.get("transfers",  [])) for e in employees)
    total_leaves     = sum(len(e.get("leave_records", [])) for e in employees)
    total_docs       = sum(len(e.get("documents",  [])) for e in employees)
    total_trainings  = sum(len(e.get("training_records", [])) for e in employees)
    total_pay        = sum(len(e.get("pay_revisions", [])) for e in employees)
    total_awards     = sum(len(e.get("awards", [])) for e in employees)

    # ── KPI Cards ────────────────────────────────────────────────────────────
    cols = st.columns(4)
    metrics = [
        ("👥", total_employees,  "Total Employees"),
        ("📈", total_promotions, "Promotions"),
        ("🔄", total_transfers,  "Transfers"),
        ("📁", total_docs,       "Uploaded Documents"),
    ]
    for col, (icon, value, label) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">{icon}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    cols2 = st.columns(4)
    metrics2 = [
        ("🌿", total_leaves,   "Leave Records"),
        ("💰", total_pay,      "Pay Revisions"),
        ("🎓", total_trainings,"Training Records"),
        ("🏆", total_awards,   "Awards & Recognitions"),
    ]
    for col, (icon, value, label) in zip(cols2, metrics2):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">{icon}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Recent Employees + Department Breakdown ───────────────────────────────
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">👤 Recently Registered Employees</div>', unsafe_allow_html=True)
        recent = sorted(employees, key=lambda e: e.get("date_of_joining", ""), reverse=True)[:8]
        if recent:
            for emp in recent:
                st.markdown(f"""
                <div class="employee-card">
                    <div>
                        <span class="employee-id-badge">{emp.get("employee_id","")}</span>&nbsp;&nbsp;
                        <strong>{emp.get("name","—")}</strong>
                        <span style="color:var(--text-light); font-size:0.82rem; margin-left:0.5rem;">
                            — {emp.get("designation","")}, {emp.get("department","")}
                        </span>
                    </div>
                    <div style="font-size:0.78rem; color:var(--text-light);">
                        Joined: {emp.get("date_of_joining","—")}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No employees registered yet. Use Employee Master to add the first employee.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🏢 By Department</div>', unsafe_allow_html=True)
        dept_counts: dict = {}
        for e in employees:
            dept = e.get("department", "Unknown")
            dept_counts[dept] = dept_counts.get(dept, 0) + 1

        if dept_counts:
            # Sort by count descending
            for dept, count in sorted(dept_counts.items(), key=lambda x: -x[1]):
                pct = int(count / total_employees * 100) if total_employees else 0
                st.markdown(f"""
                <div style="margin-bottom:0.7rem;">
                    <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:3px;">
                        <span style="font-weight:600; color:var(--navy);">{dept}</span>
                        <span style="color:var(--text-light);">{count} emp</span>
                    </div>
                    <div style="background:#e8e4dc; border-radius:4px; height:6px;">
                        <div style="background:var(--gold); width:{pct}%; height:6px; border-radius:4px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No department data yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── System Information ────────────────────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">ℹ️ System Information</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        **What is a Digital Service Book?**  
        A Service Book is the official record of an employee's entire service history —
        appointments, promotions, transfers, leave, pay, training, and disciplinary actions.
        This system digitizes those records for instant access and structured entry.
        """)
    with c2:
        st.markdown("""
        **Key Advantages over Paper**
        - 🔍 Instant search across all records  
        - ➕ New entries without modifying original scan  
        - 📄 Auto-generate up-to-date PDF Service Book  
        - 🔒 Audit trail for every change  
        """)
    with c3:
        st.markdown("""
        **Getting Started**
        1. Register employees via **Employee Master**  
        2. Add service entries via **Service Entries**  
        3. Upload scanned docs via **Document Archive**  
        4. Generate a PDF from **Service Book View**  
        """)
    st.markdown('</div>', unsafe_allow_html=True)
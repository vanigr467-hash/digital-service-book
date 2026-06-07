"""
Digital Service Book Management System
======================================
A complete digital transformation of paper-based employee service books.
Technology: Streamlit + Python + MongoDB + ReportLab
"""

import streamlit as st
import os
from datetime import datetime

# --- Page Configuration (MUST be first Streamlit command) ---
st.set_page_config(
    page_title="Digital Service Book System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Import modules ---
from modules.database import db
from modules.style import apply_styles
from modules.dashboard import show_dashboard
from modules.employee import show_employee_registration, show_employee_search
from modules.service_entrice import show_service_entries
from modules.documents import show_document_archive
from modules.service_book_view import show_service_book_view
from modules.audit import log_audit, show_audit_trail

# --- Apply custom CSS ---
apply_styles()

# --- Session State Initialization ---
if "current_user" not in st.session_state:
    st.session_state.current_user = "Admin"
if "selected_employee" not in st.session_state:
    st.session_state.selected_employee = None
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-logo">📋</div>
        <div class="sidebar-title">Digital Service Book</div>
        <div class="sidebar-subtitle">Management System</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigation menu
    nav_items = {
        "🏠  Dashboard":         "Dashboard",
        "👤  Employee Master":   "Employee Registration",
        "🔍  Search Employee":   "Search",
        "📝  Service Entries":   "Service Entries",
        "📁  Document Archive":  "Document Archive",
        "📖  View Service Book": "Service Book View",
        "📊  Audit Trail":       "Audit Trail",
    }

    for label, page in nav_items.items():
        is_active = st.session_state.active_page == page
        btn_class = "nav-btn-active" if is_active else "nav-btn"
        if st.button(label, key=f"nav_{page}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.active_page = page
            st.rerun()

    st.markdown("---")

    # Quick employee selector (shown on relevant pages)
    if st.session_state.active_page in ["Service Entries", "Service Book View", "Document Archive"]:
        st.markdown('<p class="sidebar-section-label">Quick Select Employee</p>', unsafe_allow_html=True)
        employees = list(db.employees.find({}, {"employee_id": 1, "name": 1}))
        if employees:
            emp_options = {f"{e['employee_id']} - {e['name']}": e['employee_id'] for e in employees}
            selected = st.selectbox("Employee", options=list(emp_options.keys()), label_visibility="collapsed")
            if selected:
                st.session_state.selected_employee = emp_options[selected]
        else:
            st.info("No employees registered yet.")

    st.markdown("---")
    st.markdown(f"""
    <div class="sidebar-footer">
        <span>👤 {st.session_state.current_user}</span><br/>
        <span style="font-size:0.7rem; opacity:0.6;">{datetime.now().strftime('%d %b %Y, %H:%M')}</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN CONTENT AREA
# ─────────────────────────────────────────────
page = st.session_state.active_page

if page == "Dashboard":
    show_dashboard()

elif page == "Employee Registration":
    show_employee_registration()

elif page == "Search":
    show_employee_search()

elif page == "Service Entries":
    if st.session_state.selected_employee:
        show_service_entries(st.session_state.selected_employee)
    else:
        st.markdown("""
        <div class="info-banner">
            <span style="font-size:2rem;">👈</span>
            <div>
                <strong>Select an Employee</strong><br/>
                Use the sidebar to select an employee before adding service entries.
            </div>
        </div>
        """, unsafe_allow_html=True)

elif page == "Document Archive":
    if st.session_state.selected_employee:
        show_document_archive(st.session_state.selected_employee)
    else:
        st.markdown("""
        <div class="info-banner">
            <span style="font-size:2rem;">👈</span>
            <div>
                <strong>Select an Employee</strong><br/>
                Use the sidebar to select an employee before uploading documents.
            </div>
        </div>
        """, unsafe_allow_html=True)

elif page == "Service Book View":
    if st.session_state.selected_employee:
        show_service_book_view(st.session_state.selected_employee)
    else:
        st.markdown("""
        <div class="info-banner">
            <span style="font-size:2rem;">👈</span>
            <div>
                <strong>Select an Employee</strong><br/>
                Use the sidebar to select an employee to view their service book.
            </div>
        </div>
        """, unsafe_allow_html=True)

elif page == "Audit Trail":
    show_audit_trail()
"""
Service Entries Module
======================
Forms and CRUD for all service book sections:
  - Promotions, Transfers, Leave Records, Pay Revisions,
    Training Records, Awards, Disciplinary Records
"""

import streamlit as st
from datetime import date
from modules.database import db
from modules.audit import log_audit


def _emp_header(emp: dict):
    st.markdown(f"""
    <div style="background:white; border:1px solid #d4ccc0; border-left:5px solid #c9a84c;
                border-radius:8px; padding:0.8rem 1.2rem; margin-bottom:1rem;
                display:flex; align-items:center; gap:1rem;">
        <span style="background:#0d1f3c; color:#e4c47a; font-size:0.8rem; font-weight:700;
                     padding:0.25rem 0.65rem; border-radius:4px;">{emp.get("employee_id","")}</span>
        <strong style="font-size:1rem;">{emp.get("name","")}</strong>
        <span style="color:#8888aa; font-size:0.85rem;">— {emp.get("designation","")}, {emp.get("department","")}</span>
    </div>
    """, unsafe_allow_html=True)


def _records_table(records: list, headers: list, row_fn):
    """Render a styled HTML table for a list of records."""
    if not records:
        st.info("No records found. Use the form above to add entries.")
        return
    th = "".join(f"<th>{h}</th>" for h in headers)
    rows = "".join(row_fn(r) for r in records)
    st.markdown(f"""
    <div style="overflow-x:auto;">
    <table class="record-table">
        <thead><tr>{th}<th>Added</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>
    </div>""", unsafe_allow_html=True)


def show_service_entries(employee_id: str):
    emp = db.employees.find_one({"employee_id": employee_id})
    if not emp:
        st.error(f"Employee {employee_id} not found.")
        return

    st.markdown("""
    <div class="page-header">
        <h1>📝 Service Entries</h1>
        <p>Add and view service-related records for the selected employee</p>
    </div>
    """, unsafe_allow_html=True)

    _emp_header(emp)

    tabs = st.tabs([
        "📈 Promotions", "🔄 Transfers", "🌿 Leave Records",
        "💰 Pay Revisions", "🎓 Training", "🏆 Awards", "⚖️ Disciplinary"
    ])

    # ── 1. PROMOTIONS ─────────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown('<div class="section-title">📈 Promotion History</div>', unsafe_allow_html=True)
        with st.form("promo_form", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            with c1: promo_date = st.date_input("Promotion Date *")
            with c2: old_desig  = st.text_input("Old Designation *")
            with c3: new_desig  = st.text_input("New Designation *")
            with c4: order_no   = st.text_input("Order Number *")
            remarks = st.text_input("Remarks (optional)")
            if st.form_submit_button("➕ Add Promotion", type="primary"):
                if not old_desig.strip() or not new_desig.strip() or not order_no.strip():
                    st.error("Please fill all required fields.")
                else:
                    entry = {
                        "promotion_date":   str(promo_date),
                        "old_designation":  old_desig.strip(),
                        "new_designation":  new_desig.strip(),
                        "order_number":     order_no.strip(),
                        "remarks":          remarks.strip(),
                        "added_on":         str(date.today()),
                    }
                    db.employees.update_one({"employee_id": employee_id}, {"$push": {"promotions": entry}})
                    log_audit("Service Entry Added", f"Promotion: {old_desig} → {new_desig}", employee_id=employee_id)
                    st.success("✅ Promotion record added!")
                    st.rerun()

        emp = db.employees.find_one({"employee_id": employee_id})
        _records_table(
            emp.get("promotions", []),
            ["Date", "Old Designation", "New Designation", "Order No.", "Remarks"],
            lambda r: f"""<tr>
                <td>{r.get("promotion_date","")}</td>
                <td>{r.get("old_designation","")}</td>
                <td><strong>{r.get("new_designation","")}</strong></td>
                <td><span class="badge badge-info">{r.get("order_number","")}</span></td>
                <td>{r.get("remarks","")}</td>
                <td style="color:#aaa;font-size:0.78rem;">{r.get("added_on","")}</td>
            </tr>"""
        )

    # ── 2. TRANSFERS ──────────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown('<div class="section-title">🔄 Transfer History</div>', unsafe_allow_html=True)
        with st.form("transfer_form", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            with c1: tr_date   = st.date_input("Transfer Date *")
            with c2: from_loc  = st.text_input("From Location *")
            with c3: to_loc    = st.text_input("To Location *")
            with c4: tr_order  = st.text_input("Order Number *")
            tr_remarks = st.text_input("Remarks (optional)")
            if st.form_submit_button("➕ Add Transfer", type="primary"):
                if not from_loc.strip() or not to_loc.strip() or not tr_order.strip():
                    st.error("Please fill all required fields.")
                else:
                    entry = {
                        "transfer_date": str(tr_date),
                        "from_location": from_loc.strip(),
                        "to_location":   to_loc.strip(),
                        "order_number":  tr_order.strip(),
                        "remarks":       tr_remarks.strip(),
                        "added_on":      str(date.today()),
                    }
                    db.employees.update_one({"employee_id": employee_id}, {"$push": {"transfers": entry}})
                    log_audit("Service Entry Added", f"Transfer: {from_loc} → {to_loc}", employee_id=employee_id)
                    st.success("✅ Transfer record added!")
                    st.rerun()

        emp = db.employees.find_one({"employee_id": employee_id})
        _records_table(
            emp.get("transfers", []),
            ["Date", "From", "To", "Order No.", "Remarks"],
            lambda r: f"""<tr>
                <td>{r.get("transfer_date","")}</td>
                <td>{r.get("from_location","")}</td>
                <td><strong>{r.get("to_location","")}</strong></td>
                <td><span class="badge badge-warning">{r.get("order_number","")}</span></td>
                <td>{r.get("remarks","")}</td>
                <td style="color:#aaa;font-size:0.78rem;">{r.get("added_on","")}</td>
            </tr>"""
        )

    # ── 3. LEAVE RECORDS ─────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown('<div class="section-title">🌿 Leave Records</div>', unsafe_allow_html=True)
        leave_types = ["Earned Leave", "Half Pay Leave", "Commuted Leave",
                       "Extraordinary Leave", "Maternity Leave", "Paternity Leave",
                       "Child Care Leave", "Study Leave", "Medical Leave", "Casual Leave"]
        with st.form("leave_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1: leave_type   = st.selectbox("Leave Type *", leave_types)
            with c2: leave_start  = st.date_input("Start Date *")
            with c3: leave_end    = st.date_input("End Date *")
            c4, c5 = st.columns(2)
            with c4: sanction_auth = st.text_input("Sanction Authority *")
            with c5: sanction_order = st.text_input("Sanction Order Number")
            leave_remarks = st.text_input("Remarks")
            if st.form_submit_button("➕ Add Leave Record", type="primary"):
                if not sanction_auth.strip():
                    st.error("Sanction Authority is required.")
                elif leave_end < leave_start:
                    st.error("End date cannot be before start date.")
                else:
                    days = (leave_end - leave_start).days + 1
                    entry = {
                        "leave_type":      leave_type,
                        "start_date":      str(leave_start),
                        "end_date":        str(leave_end),
                        "days":            days,
                        "sanction_auth":   sanction_auth.strip(),
                        "sanction_order":  sanction_order.strip(),
                        "remarks":         leave_remarks.strip(),
                        "added_on":        str(date.today()),
                    }
                    db.employees.update_one({"employee_id": employee_id}, {"$push": {"leave_records": entry}})
                    log_audit("Service Entry Added", f"Leave: {leave_type} ({days} days)", employee_id=employee_id)
                    st.success(f"✅ Leave record added! ({days} days)")
                    st.rerun()

        emp = db.employees.find_one({"employee_id": employee_id})
        _records_table(
            emp.get("leave_records", []),
            ["Leave Type", "Start Date", "End Date", "Days", "Sanction Authority", "Order No."],
            lambda r: f"""<tr>
                <td><span class="badge badge-success">{r.get("leave_type","")}</span></td>
                <td>{r.get("start_date","")}</td>
                <td>{r.get("end_date","")}</td>
                <td><strong>{r.get("days","")}</strong></td>
                <td>{r.get("sanction_auth","")}</td>
                <td>{r.get("sanction_order","")}</td>
                <td style="color:#aaa;font-size:0.78rem;">{r.get("added_on","")}</td>
            </tr>"""
        )

    # ── 4. PAY REVISIONS ─────────────────────────────────────────────────────
    with tabs[3]:
        st.markdown('<div class="section-title">💰 Pay Revision Records</div>', unsafe_allow_html=True)
        with st.form("pay_form", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            with c1: eff_date  = st.date_input("Effective Date *")
            with c2: old_pay   = st.number_input("Old Basic Pay (₹) *", min_value=0, step=100)
            with c3: new_pay   = st.number_input("New Basic Pay (₹) *", min_value=0, step=100)
            with c4: pay_scale = st.text_input("Pay Scale / Level")
            pay_order   = st.text_input("Pay Revision Order Number")
            pay_remarks = st.text_input("Remarks")
            if st.form_submit_button("➕ Add Pay Revision", type="primary"):
                if old_pay == 0 and new_pay == 0:
                    st.error("Please enter pay details.")
                else:
                    entry = {
                        "effective_date": str(eff_date),
                        "old_pay":        old_pay,
                        "new_pay":        new_pay,
                        "pay_scale":      pay_scale.strip(),
                        "order_number":   pay_order.strip(),
                        "remarks":        pay_remarks.strip(),
                        "added_on":       str(date.today()),
                    }
                    db.employees.update_one({"employee_id": employee_id}, {"$push": {"pay_revisions": entry}})
                    log_audit("Service Entry Added", f"Pay Revision: ₹{old_pay} → ₹{new_pay}", employee_id=employee_id)
                    st.success("✅ Pay revision record added!")
                    st.rerun()

        emp = db.employees.find_one({"employee_id": employee_id})
        _records_table(
            emp.get("pay_revisions", []),
            ["Effective Date", "Old Pay (₹)", "New Pay (₹)", "Pay Scale", "Order No."],
            lambda r: f"""<tr>
                <td>{r.get("effective_date","")}</td>
                <td>₹{r.get("old_pay",""):,}</td>
                <td><strong>₹{r.get("new_pay",""):,}</strong></td>
                <td>{r.get("pay_scale","")}</td>
                <td><span class="badge badge-info">{r.get("order_number","")}</span></td>
                <td style="color:#aaa;font-size:0.78rem;">{r.get("added_on","")}</td>
            </tr>"""
        )

    # ── 5. TRAINING RECORDS ───────────────────────────────────────────────────
    with tabs[4]:
        st.markdown('<div class="section-title">🎓 Training Records</div>', unsafe_allow_html=True)
        with st.form("training_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1: training_name = st.text_input("Training Name *")
            with c2: institution   = st.text_input("Institution / Organisation")
            with c3: duration      = st.text_input("Duration (e.g. 5 days, 2 weeks)")
            c4, c5 = st.columns(2)
            with c4: t_start = st.date_input("Start Date *", key="t_start")
            with c5: t_end   = st.date_input("End Date *",   key="t_end")
            cert_number = st.text_input("Certificate Number")
            t_remarks   = st.text_input("Remarks")
            if st.form_submit_button("➕ Add Training Record", type="primary"):
                if not training_name.strip():
                    st.error("Training Name is required.")
                else:
                    entry = {
                        "training_name":  training_name.strip(),
                        "institution":    institution.strip(),
                        "duration":       duration.strip(),
                        "start_date":     str(t_start),
                        "end_date":       str(t_end),
                        "cert_number":    cert_number.strip(),
                        "remarks":        t_remarks.strip(),
                        "added_on":       str(date.today()),
                    }
                    db.employees.update_one({"employee_id": employee_id}, {"$push": {"training_records": entry}})
                    log_audit("Service Entry Added", f"Training: {training_name}", employee_id=employee_id)
                    st.success("✅ Training record added!")
                    st.rerun()

        emp = db.employees.find_one({"employee_id": employee_id})
        _records_table(
            emp.get("training_records", []),
            ["Training Name", "Institution", "Duration", "Start Date", "End Date", "Cert. No."],
            lambda r: f"""<tr>
                <td><strong>{r.get("training_name","")}</strong></td>
                <td>{r.get("institution","")}</td>
                <td>{r.get("duration","")}</td>
                <td>{r.get("start_date","")}</td>
                <td>{r.get("end_date","")}</td>
                <td>{r.get("cert_number","")}</td>
                <td style="color:#aaa;font-size:0.78rem;">{r.get("added_on","")}</td>
            </tr>"""
        )

    # ── 6. AWARDS & RECOGNITION ───────────────────────────────────────────────
    with tabs[5]:
        st.markdown('<div class="section-title">🏆 Awards & Recognition</div>', unsafe_allow_html=True)
        with st.form("awards_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1: award_name   = st.text_input("Award / Recognition *")
            with c2: award_by     = st.text_input("Awarded By")
            with c3: award_date   = st.date_input("Award Date *")
            award_desc = st.text_area("Description", height=70)
            if st.form_submit_button("➕ Add Award", type="primary"):
                if not award_name.strip():
                    st.error("Award name is required.")
                else:
                    entry = {
                        "award_name":  award_name.strip(),
                        "awarded_by":  award_by.strip(),
                        "award_date":  str(award_date),
                        "description": award_desc.strip(),
                        "added_on":    str(date.today()),
                    }
                    db.employees.update_one({"employee_id": employee_id}, {"$push": {"awards": entry}})
                    log_audit("Service Entry Added", f"Award: {award_name}", employee_id=employee_id)
                    st.success("✅ Award record added!")
                    st.rerun()

        emp = db.employees.find_one({"employee_id": employee_id})
        _records_table(
            emp.get("awards", []),
            ["Award / Recognition", "Awarded By", "Date", "Description"],
            lambda r: f"""<tr>
                <td><strong>{r.get("award_name","")}</strong></td>
                <td>{r.get("awarded_by","")}</td>
                <td>{r.get("award_date","")}</td>
                <td>{r.get("description","")}</td>
                <td style="color:#aaa;font-size:0.78rem;">{r.get("added_on","")}</td>
            </tr>"""
        )

    # ── 7. DISCIPLINARY RECORDS ───────────────────────────────────────────────
    with tabs[6]:
        st.markdown('<div class="section-title">⚖️ Disciplinary Records</div>', unsafe_allow_html=True)
        penalty_types = ["Warning", "Censure", "Minor Penalty", "Major Penalty",
                         "Suspension", "Compulsory Retirement", "Dismissal", "Other"]
        with st.form("disc_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1: disc_date  = st.date_input("Date of Action *")
            with c2: penalty    = st.selectbox("Penalty Type *", penalty_types)
            with c3: disc_order = st.text_input("Order Number")
            disc_desc   = st.text_area("Description of Misconduct *", height=70)
            disc_auth   = st.text_input("Disciplinary Authority")
            if st.form_submit_button("➕ Add Disciplinary Record", type="primary"):
                if not disc_desc.strip():
                    st.error("Description is required.")
                else:
                    entry = {
                        "date":        str(disc_date),
                        "penalty":     penalty,
                        "order_number":disc_order.strip(),
                        "description": disc_desc.strip(),
                        "authority":   disc_auth.strip(),
                        "added_on":    str(date.today()),
                    }
                    db.employees.update_one({"employee_id": employee_id}, {"$push": {"disciplinary_records": entry}})
                    log_audit("Service Entry Added", f"Disciplinary: {penalty}", employee_id=employee_id)
                    st.success("✅ Disciplinary record added!")
                    st.rerun()

        emp = db.employees.find_one({"employee_id": employee_id})
        _records_table(
            emp.get("disciplinary_records", []),
            ["Date", "Penalty", "Order No.", "Description", "Authority"],
            lambda r: f"""<tr>
                <td>{r.get("date","")}</td>
                <td><span class="badge badge-danger">{r.get("penalty","")}</span></td>
                <td>{r.get("order_number","")}</td>
                <td>{r.get("description","")}</td>
                <td>{r.get("authority","")}</td>
                <td style="color:#aaa;font-size:0.78rem;">{r.get("added_on","")}</td>
            </tr>"""
        )
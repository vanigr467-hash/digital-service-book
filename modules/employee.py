"""
Employee Master Module
======================
Handles employee registration, editing, and search.
"""

import streamlit as st
from datetime import date
from modules.database import db
from modules.audit import log_audit


DEPARTMENTS = [
    "Administration", "Finance", "HR", "Information Technology",
    "Legal", "Operations", "Planning", "Public Works",
    "Revenue", "Social Welfare", "Technical", "Other"
]

DESIGNATIONS = [
    "Clerk", "Senior Clerk", "Assistant", "Senior Assistant",
    "Section Officer", "Deputy Director", "Director", "Joint Secretary",
    "Under Secretary", "Additional Secretary", "Secretary",
    "Junior Engineer", "Assistant Engineer", "Executive Engineer",
    "Superintendent Engineer", "Chief Engineer", "Other"
]

GENDERS = ["Male", "Female", "Transgender", "Prefer not to say"]


def generate_employee_id():
    """Auto-generate the next EMP ID."""
    employees = list(db.employees.find({}, {"employee_id": 1}) or [])
    nums = []
    for e in employees:
        try:
            nums.append(int(e["employee_id"].replace("EMP", "")))
        except Exception:
            pass
    next_num = max(nums, default=0) + 1
    return f"EMP{next_num:04d}"


def show_employee_registration():
    st.markdown("""
    <div class="page-header">
        <h1>👤 Employee Master</h1>
        <p>Register new employees and manage personal details</p>
    </div>
    """, unsafe_allow_html=True)

    tab_register, tab_list, tab_edit = st.tabs(
        ["➕ Register New Employee", "📋 Employee List", "✏️ Edit Employee"]
    )

    # ── Register New Employee ─────────────────────────────────────────────────
    with tab_register:
        st.markdown("### Personal & Service Details")
        with st.form("emp_register_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                auto_id = generate_employee_id()
                emp_id = st.text_input("Employee ID *", value=auto_id, help="Auto-generated. You may change it.")
            with col2:
                name = st.text_input("Full Name *")
            with col3:
                dob = st.date_input("Date of Birth *", min_value=date(1940, 1, 1), max_value=date(2005, 12, 31))

            col4, col5, col6 = st.columns(3)
            with col4:
                gender = st.selectbox("Gender *", GENDERS)
            with col5:
                department = st.selectbox("Department *", DEPARTMENTS)
            with col6:
                designation = st.selectbox("Designation *", DESIGNATIONS)

            col7, col8 = st.columns(2)
            with col7:
                doj = st.date_input("Date of Joining *", min_value=date(1970, 1, 1))
            with col8:
                appointment_order = st.text_input("Appointment Order Number")

            st.markdown("**Contact Details**")
            col9, col10, col11 = st.columns(3)
            with col9:
                phone = st.text_input("Phone Number")
            with col10:
                email = st.text_input("Email Address")
            with col11:
                address = st.text_area("Residential Address", height=70)

            st.markdown("**Additional Details**")
            col12, col13, col14 = st.columns(3)
            with col12:
                pan = st.text_input("PAN Number")
            with col13:
                aadhaar = st.text_input("Aadhaar Number")
            with col14:
                blood_group = st.selectbox("Blood Group", ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

            submitted = st.form_submit_button("✅ Register Employee", type="primary", use_container_width=True)

        if submitted:
            # Validation
            errors = []
            if not emp_id.strip():   errors.append("Employee ID is required.")
            if not name.strip():     errors.append("Full Name is required.")
            if not department:       errors.append("Department is required.")
            if not designation:      errors.append("Designation is required.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                # Duplicate check
                existing = db.employees.find_one({"employee_id": emp_id.strip()})
                if existing:
                    st.error(f"Employee ID **{emp_id}** already exists. Please use a different ID.")
                else:
                    doc = {
                        "employee_id":         emp_id.strip(),
                        "name":                name.strip(),
                        "date_of_birth":       str(dob),
                        "gender":              gender,
                        "department":          department,
                        "designation":         designation,
                        "date_of_joining":     str(doj),
                        "appointment_order":   appointment_order.strip(),
                        "phone":               phone.strip(),
                        "email":               email.strip(),
                        "address":             address.strip(),
                        "pan":                 pan.strip(),
                        "aadhaar":             aadhaar.strip(),
                        "blood_group":         blood_group,
                        "promotions":          [],
                        "transfers":           [],
                        "leave_records":       [],
                        "pay_revisions":       [],
                        "training_records":    [],
                        "awards":              [],
                        "disciplinary_records":[],
                        "documents":           [],
                    }
                    db.employees.insert_one(doc)
                    log_audit("Employee Created", f"Registered {name.strip()} ({emp_id.strip()})",
                              employee_id=emp_id.strip())
                    st.success(f"✅ Employee **{name.strip()}** registered successfully with ID **{emp_id.strip()}**!")

    # ── Employee List ─────────────────────────────────────────────────────────
    with tab_list:
        employees = list(db.employees.find({}) or [])
        if not employees:
            st.info("No employees registered yet. Use the 'Register New Employee' tab.")
            return

        st.markdown(f"**{len(employees)} employee(s) registered**")
        st.markdown("<br/>", unsafe_allow_html=True)

        rows = ""
        for e in sorted(employees, key=lambda x: x.get("employee_id", "")):
            rows += f"""<tr>
                <td><span class="employee-id-badge">{e.get("employee_id","")}</span></td>
                <td><strong>{e.get("name","")}</strong></td>
                <td>{e.get("designation","")}</td>
                <td>{e.get("department","")}</td>
                <td>{e.get("gender","")}</td>
                <td>{e.get("date_of_joining","")}</td>
                <td>{e.get("phone","")}</td>
            </tr>"""

        st.markdown(f"""
        <div style="overflow-x:auto;">
        <table class="record-table">
            <thead><tr>
                <th>Emp ID</th><th>Name</th><th>Designation</th>
                <th>Department</th><th>Gender</th><th>Date of Joining</th><th>Phone</th>
            </tr></thead>
            <tbody>{rows}</tbody>
        </table>
        </div>""", unsafe_allow_html=True)

    # ── Edit Employee ─────────────────────────────────────────────────────────
    with tab_edit:
        employees = list(db.employees.find({}) or [])
        if not employees:
            st.info("No employees to edit.")
            return

        options = {f"{e['employee_id']} — {e['name']}": e["employee_id"] for e in employees}
        chosen = st.selectbox("Select Employee to Edit", list(options.keys()))
        emp = db.employees.find_one({"employee_id": options[chosen]})

        if emp:
            with st.form("edit_emp_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name    = st.text_input("Full Name",    value=emp.get("name",""))
                    new_dept    = st.selectbox("Department",    DEPARTMENTS,
                                               index=DEPARTMENTS.index(emp.get("department","Administration"))
                                               if emp.get("department","Administration") in DEPARTMENTS else 0)
                    new_phone   = st.text_input("Phone",        value=emp.get("phone",""))
                    new_email   = st.text_input("Email",        value=emp.get("email",""))
                with col2:
                    new_desig   = st.selectbox("Designation",   DESIGNATIONS,
                                               index=DESIGNATIONS.index(emp.get("designation","Clerk"))
                                               if emp.get("designation","Clerk") in DESIGNATIONS else 0)
                    new_gender  = st.selectbox("Gender",        GENDERS,
                                               index=GENDERS.index(emp.get("gender","Male"))
                                               if emp.get("gender","Male") in GENDERS else 0)
                    new_pan     = st.text_input("PAN",          value=emp.get("pan",""))
                    new_aadhaar = st.text_input("Aadhaar",      value=emp.get("aadhaar",""))
                new_address = st.text_area("Address", value=emp.get("address",""))

                if st.form_submit_button("💾 Save Changes", type="primary"):
                    db.employees.update_one(
                        {"employee_id": emp["employee_id"]},
                        {"$set": {
                            "name":        new_name.strip(),
                            "department":  new_dept,
                            "designation": new_desig,
                            "gender":      new_gender,
                            "phone":       new_phone.strip(),
                            "email":       new_email.strip(),
                            "pan":         new_pan.strip(),
                            "aadhaar":     new_aadhaar.strip(),
                            "address":     new_address.strip(),
                        }}
                    )
                    log_audit("Employee Updated", f"Updated details for {emp['employee_id']}",
                              employee_id=emp["employee_id"])
                    st.success("✅ Employee details updated successfully!")
                    st.rerun()


def show_employee_search():
    st.markdown("""
    <div class="page-header">
        <h1>🔍 Search Employee</h1>
        <p>Find employees by ID, name, or department</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        query = st.text_input("Search by Employee ID or Name", placeholder="e.g. EMP0001 or John Doe")
    with col2:
        dept_filter = st.selectbox("Filter by Department", ["All"] + DEPARTMENTS)

    employees = list(db.employees.find({}) or [])

    # Filter
    results = []
    q = query.strip().lower()
    for e in employees:
        if dept_filter != "All" and e.get("department") != dept_filter:
            continue
        if q:
            if (q not in e.get("employee_id","").lower() and
                q not in e.get("name","").lower()):
                continue
        results.append(e)

    st.markdown(f"<br/>**{len(results)} result(s) found**<br/>", unsafe_allow_html=True)

    for emp in results:
        with st.expander(f"📋 {emp.get('employee_id','')}  —  {emp.get('name','')}  |  {emp.get('designation','')}  |  {emp.get('department','')}"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                **Employee ID:** {emp.get('employee_id','')}  
                **Name:** {emp.get('name','')}  
                **Date of Birth:** {emp.get('date_of_birth','')}  
                **Gender:** {emp.get('gender','')}  
                **Blood Group:** {emp.get('blood_group','')}  
                """)
            with c2:
                st.markdown(f"""
                **Department:** {emp.get('department','')}  
                **Designation:** {emp.get('designation','')}  
                **Date of Joining:** {emp.get('date_of_joining','')}  
                **Appointment Order:** {emp.get('appointment_order','')}  
                """)
            with c3:
                st.markdown(f"""
                **Phone:** {emp.get('phone','')}  
                **Email:** {emp.get('email','')}  
                **PAN:** {emp.get('pan','')}  
                **Aadhaar:** {emp.get('aadhaar','')}  
                """)
            st.markdown("**Address:** " + emp.get("address","—"))

            # Quick record counts
            st.markdown("---")
            cols = st.columns(6)
            counts = [
                ("Promotions",   len(emp.get("promotions", []))),
                ("Transfers",    len(emp.get("transfers",  []))),
                ("Leave Records",len(emp.get("leave_records", []))),
                ("Pay Revisions",len(emp.get("pay_revisions", []))),
                ("Trainings",    len(emp.get("training_records", []))),
                ("Documents",    len(emp.get("documents",  []))),
            ]
            for col, (label, cnt) in zip(cols, counts):
                with col:
                    st.metric(label, cnt)

            # Select for service entries
            if st.button("📝 Open Service Entries", key=f"open_{emp['employee_id']}"):
                st.session_state.selected_employee = emp["employee_id"]
                st.session_state.active_page = "Service Entries"
                st.rerun()
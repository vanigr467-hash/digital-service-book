"""
Service Book View & PDF Generation Module
==========================================
Displays a complete in-app view of an employee's service book
and generates a professional PDF using ReportLab.
"""

import streamlit as st
import io
from datetime import date, datetime
from modules.database import db
from modules.audit import log_audit

# ── ReportLab imports ──────────────────────────────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# ─────────────────────────────────────────────────────────────────────────────
#  PDF GENERATION
# ─────────────────────────────────────────────────────────────────────────────

NAVY  = colors.HexColor("#0d1f3c")
GOLD  = colors.HexColor("#c9a84c")
CREAM = colors.HexColor("#f8f4ec")
WHITE = colors.white
LIGHT = colors.HexColor("#e8e4dc")
TEXT  = colors.HexColor("#1a1a2e")
GREY  = colors.HexColor("#8888aa")


def _styles():
    base = getSampleStyleSheet()
    custom = {
        "title": ParagraphStyle("title",
            fontName="Helvetica-Bold", fontSize=18,
            textColor=WHITE, alignment=TA_CENTER, spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle",
            fontName="Helvetica", fontSize=10,
            textColor=colors.HexColor("#e4c47a"), alignment=TA_CENTER, spaceAfter=2),
        "section_header": ParagraphStyle("section_header",
            fontName="Helvetica-Bold", fontSize=11,
            textColor=WHITE, alignment=TA_LEFT,
            leftIndent=6, spaceBefore=12, spaceAfter=4),
        "field_label": ParagraphStyle("field_label",
            fontName="Helvetica-Bold", fontSize=9,
            textColor=NAVY, spaceAfter=1),
        "field_value": ParagraphStyle("field_value",
            fontName="Helvetica", fontSize=9,
            textColor=TEXT, spaceAfter=1),
        "normal": ParagraphStyle("normal_custom",
            fontName="Helvetica", fontSize=9,
            textColor=TEXT, spaceAfter=4),
        "footer": ParagraphStyle("footer",
            fontName="Helvetica", fontSize=7,
            textColor=GREY, alignment=TA_CENTER),
        "no_records": ParagraphStyle("no_records",
            fontName="Helvetica-Oblique", fontSize=8.5,
            textColor=GREY, alignment=TA_CENTER, spaceAfter=6),
    }
    return custom


def _section_header(text, styles):
    return Table(
        [[Paragraph(text, styles["section_header"])]],
        colWidths=[17.5*cm],
        style=TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), NAVY),
            ("TOPPADDING",    (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING",   (0,0), (-1,-1), 10),
            ("ROUNDEDCORNERS", [4]),
        ])
    )


def _data_table(headers, rows, col_widths):
    data = [headers] + (rows if rows else [["—"] * len(headers)])
    style = TableStyle([
        ("BACKGROUND",    (0,0),  (-1,0),  NAVY),
        ("TEXTCOLOR",     (0,0),  (-1,0),  GOLD),
        ("FONTNAME",      (0,0),  (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),  (-1,0),  8),
        ("ALIGN",         (0,0),  (-1,-1), "LEFT"),
        ("VALIGN",        (0,0),  (-1,-1), "MIDDLE"),
        ("FONTNAME",      (0,1),  (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1),  (-1,-1), 8),
        ("TEXTCOLOR",     (0,1),  (-1,-1), TEXT),
        ("ROWBACKGROUNDS",(0,1),  (-1,-1), [WHITE, CREAM]),
        ("GRID",          (0,0),  (-1,-1), 0.3, LIGHT),
        ("TOPPADDING",    (0,0),  (-1,-1), 4),
        ("BOTTOMPADDING", (0,0),  (-1,-1), 4),
        ("LEFTPADDING",   (0,0),  (-1,-1), 6),
    ])
    return Table(data, colWidths=col_widths, style=style, repeatRows=1)


def generate_pdf(emp: dict) -> bytes:
    """Generate a complete Service Book PDF and return as bytes."""
    buffer = io.BytesIO()
    styles = _styles()
    W = A4[0] - 3*cm   # usable width

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=2*cm, bottomMargin=2*cm,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        title=f"Service Book — {emp.get('name','')}",
    )

    story = []

    # ── COVER HEADER ──────────────────────────────────────────────────────────
    cover = Table(
        [[
            Paragraph("GOVERNMENT OF INDIA", ParagraphStyle("gov",fontName="Helvetica-Bold",
                       fontSize=9, textColor=GOLD, alignment=TA_CENTER, spaceBefore=0, spaceAfter=2)),
            "",
        ],
        [
            Paragraph("SERVICE BOOK", ParagraphStyle("sb", fontName="Helvetica-Bold",
                       fontSize=22, textColor=WHITE, alignment=TA_CENTER, spaceAfter=4)),
            "",
        ],
        [
            Paragraph(emp.get("name","").upper(), ParagraphStyle("nm", fontName="Helvetica-Bold",
                       fontSize=14, textColor=GOLD, alignment=TA_CENTER, spaceAfter=2)),
            "",
        ],
        [
            Paragraph(f"{emp.get('designation','')}  |  {emp.get('department','')}",
                       ParagraphStyle("desig", fontName="Helvetica", fontSize=10,
                       textColor=colors.HexColor("#e4c47a"), alignment=TA_CENTER, spaceAfter=2)),
            "",
        ],
        [
            Paragraph(f"Employee ID: {emp.get('employee_id','')}",
                       ParagraphStyle("eid", fontName="Helvetica", fontSize=9,
                       textColor=colors.HexColor("#ccccdd"), alignment=TA_CENTER)),
            "",
        ]],
        colWidths=[W, 0],
        style=TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), NAVY),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("SPAN",          (0,0), (1,0)),
            ("SPAN",          (0,1), (1,1)),
            ("SPAN",          (0,2), (1,2)),
            ("SPAN",          (0,3), (1,3)),
            ("SPAN",          (0,4), (1,4)),
            ("ROUNDEDCORNERS", [6]),
        ])
    )
    story.append(cover)
    story.append(Spacer(1, 0.5*cm))

    # ── SECTION 1: PERSONAL DETAILS ───────────────────────────────────────────
    story.append(_section_header("1.  PERSONAL DETAILS", styles))
    story.append(Spacer(1, 0.2*cm))
    personal_data = [
        ["Employee ID",    emp.get("employee_id","—"),  "Date of Birth",     emp.get("date_of_birth","—")],
        ["Full Name",      emp.get("name","—"),         "Gender",            emp.get("gender","—")],
        ["Department",     emp.get("department","—"),   "Designation",       emp.get("designation","—")],
        ["Date of Joining",emp.get("date_of_joining","—"), "Blood Group",    emp.get("blood_group","—")],
        ["Phone",          emp.get("phone","—"),        "Email",             emp.get("email","—")],
        ["PAN",            emp.get("pan","—"),          "Aadhaar",           emp.get("aadhaar","—")],
        ["Address",        emp.get("address","—"),      "Appt. Order",       emp.get("appointment_order","—")],
    ]
    w4 = [3.5*cm, 5*cm, 3.5*cm, 5*cm]
    pers_table = Table(
        [[Paragraph(str(r[0]), styles["field_label"]),
          Paragraph(str(r[1]), styles["field_value"]),
          Paragraph(str(r[2]), styles["field_label"]),
          Paragraph(str(r[3]), styles["field_value"])] for r in personal_data],
        colWidths=w4,
        style=TableStyle([
            ("GRID",          (0,0), (-1,-1), 0.3, LIGHT),
            ("ROWBACKGROUNDS",(0,0), (-1,-1), [WHITE, CREAM]),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ])
    )
    story.append(pers_table)
    story.append(Spacer(1, 0.4*cm))

    # ── SECTION 2: PROMOTION HISTORY ─────────────────────────────────────────
    story.append(_section_header("2.  PROMOTION HISTORY", styles))
    story.append(Spacer(1, 0.2*cm))
    promos = emp.get("promotions", [])
    promo_rows = [[r.get("promotion_date",""), r.get("old_designation",""),
                   r.get("new_designation",""), r.get("order_number",""),
                   r.get("remarks","")] for r in promos]
    story.append(_data_table(
        ["Date", "Old Designation", "New Designation", "Order No.", "Remarks"],
        promo_rows,
        [2.5*cm, 4*cm, 4*cm, 3.5*cm, 3.5*cm]
    ))
    story.append(Spacer(1, 0.4*cm))

    # ── SECTION 3: TRANSFER HISTORY ──────────────────────────────────────────
    story.append(_section_header("3.  TRANSFER HISTORY", styles))
    story.append(Spacer(1, 0.2*cm))
    transfers = emp.get("transfers", [])
    trans_rows = [[r.get("transfer_date",""), r.get("from_location",""),
                   r.get("to_location",""), r.get("order_number",""),
                   r.get("remarks","")] for r in transfers]
    story.append(_data_table(
        ["Date", "From", "To", "Order No.", "Remarks"],
        trans_rows,
        [2.5*cm, 3.5*cm, 3.5*cm, 3.5*cm, 4.5*cm]
    ))
    story.append(Spacer(1, 0.4*cm))

    # ── SECTION 4: LEAVE RECORDS ──────────────────────────────────────────────
    story.append(_section_header("4.  LEAVE RECORDS", styles))
    story.append(Spacer(1, 0.2*cm))
    leaves = emp.get("leave_records", [])
    leave_rows = [[r.get("leave_type",""), r.get("start_date",""),
                   r.get("end_date",""), str(r.get("days","")),
                   r.get("sanction_auth",""), r.get("sanction_order","")] for r in leaves]
    story.append(_data_table(
        ["Leave Type", "Start", "End", "Days", "Sanction Authority", "Order No."],
        leave_rows,
        [3*cm, 2.5*cm, 2.5*cm, 1.5*cm, 4*cm, 4*cm]
    ))
    story.append(Spacer(1, 0.4*cm))

    # ── SECTION 5: PAY REVISIONS ─────────────────────────────────────────────
    story.append(_section_header("5.  PAY REVISION RECORDS", styles))
    story.append(Spacer(1, 0.2*cm))
    pays = emp.get("pay_revisions", [])
    pay_rows = [[r.get("effective_date",""), f"Rs.{r.get('old_pay',''):,}",
                 f"Rs.{r.get('new_pay',''):,}", r.get("pay_scale",""),
                 r.get("order_number",""), r.get("remarks","")] for r in pays]
    story.append(_data_table(
        ["Eff. Date", "Old Pay", "New Pay", "Pay Scale", "Order No.", "Remarks"],
        pay_rows,
        [2.5*cm, 2.5*cm, 2.5*cm, 3*cm, 3*cm, 4*cm]
    ))
    story.append(Spacer(1, 0.4*cm))

    # ── SECTION 6: TRAINING RECORDS ──────────────────────────────────────────
    story.append(_section_header("6.  TRAINING RECORDS", styles))
    story.append(Spacer(1, 0.2*cm))
    trainings = emp.get("training_records", [])
    train_rows = [[r.get("training_name",""), r.get("institution",""),
                   r.get("duration",""), r.get("start_date",""),
                   r.get("end_date",""), r.get("cert_number","")] for r in trainings]
    story.append(_data_table(
        ["Training Name", "Institution", "Duration", "Start", "End", "Cert. No."],
        train_rows,
        [4*cm, 3.5*cm, 2*cm, 2.3*cm, 2.3*cm, 3.4*cm]
    ))
    story.append(Spacer(1, 0.4*cm))

    # ── SECTION 7: AWARDS ────────────────────────────────────────────────────
    story.append(_section_header("7.  AWARDS & RECOGNITION", styles))
    story.append(Spacer(1, 0.2*cm))
    awards = emp.get("awards", [])
    award_rows = [[r.get("award_name",""), r.get("awarded_by",""),
                   r.get("award_date",""), r.get("description","")] for r in awards]
    story.append(_data_table(
        ["Award / Recognition", "Awarded By", "Date", "Description"],
        award_rows,
        [4*cm, 4*cm, 2.5*cm, 7*cm]
    ))
    story.append(Spacer(1, 0.4*cm))

    # ── SECTION 8: DISCIPLINARY RECORDS ─────────────────────────────────────
    story.append(_section_header("8.  DISCIPLINARY RECORDS", styles))
    story.append(Spacer(1, 0.2*cm))
    disc = emp.get("disciplinary_records", [])
    disc_rows = [[r.get("date",""), r.get("penalty",""),
                  r.get("order_number",""), r.get("description",""),
                  r.get("authority","")] for r in disc]
    story.append(_data_table(
        ["Date", "Penalty", "Order No.", "Description", "Authority"],
        disc_rows,
        [2.5*cm, 3*cm, 3*cm, 5.5*cm, 3.5*cm]
    ))
    story.append(Spacer(1, 0.4*cm))

    # ── SECTION 9: DOCUMENTS LIST ────────────────────────────────────────────
    docs = emp.get("documents", [])
    story.append(_section_header("9.  ARCHIVED DOCUMENTS", styles))
    story.append(Spacer(1, 0.2*cm))
    doc_rows = [[r.get("doc_type",""), r.get("title",""),
                 r.get("doc_date",""), r.get("ref_number",""),
                 r.get("original_name",""), r.get("uploaded_on","")] for r in docs]
    story.append(_data_table(
        ["Doc Type", "Title", "Date", "Ref. No.", "File Name", "Uploaded On"],
        doc_rows,
        [3.5*cm, 4*cm, 2*cm, 2.5*cm, 3.5*cm, 2*cm]
    ))

    # ── FOOTER ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width=W, thickness=0.5, color=GOLD))
    story.append(Spacer(1, 0.2*cm))
    gen_time = datetime.now().strftime("%d %B %Y at %H:%M")
    story.append(Paragraph(
        f"This Service Book was digitally generated on {gen_time}. "
        f"All entries are sourced from the Digital Service Book Management System.",
        styles["footer"]
    ))

    doc.build(story)
    return buffer.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
#  SERVICE BOOK VIEW PAGE
# ─────────────────────────────────────────────────────────────────────────────

def _section_card(title, content_fn):
    st.markdown(f'<div class="section-card"><div class="section-title">{title}</div>', unsafe_allow_html=True)
    content_fn()
    st.markdown('</div>', unsafe_allow_html=True)


def _render_table(headers, rows):
    if not rows:
        st.markdown('<p style="color:#aaa; font-style:italic; font-size:0.85rem;">No records found.</p>',
                    unsafe_allow_html=True)
        return
    th = "".join(f"<th>{h}</th>" for h in headers)
    row_html = "".join(f"<tr>{''.join(f'<td>{c}</td>' for c in r)}</tr>" for r in rows)
    st.markdown(f"""
    <div style="overflow-x:auto;">
    <table class="record-table">
        <thead><tr>{th}</tr></thead>
        <tbody>{row_html}</tbody>
    </table>
    </div>""", unsafe_allow_html=True)


def show_service_book_view(employee_id: str):
    emp = db.employees.find_one({"employee_id": employee_id})
    if not emp:
        st.error(f"Employee {employee_id} not found.")
        return

    st.markdown("""
    <div class="page-header">
        <h1>📖 Service Book View</h1>
        <p>Complete service history and PDF generation</p>
    </div>
    """, unsafe_allow_html=True)

    # Employee summary banner
    promos    = len(emp.get("promotions", []))
    transfers = len(emp.get("transfers",  []))
    leaves    = len(emp.get("leave_records", []))
    docs      = len(emp.get("documents",  []))

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d1f3c,#1e3f70);
                color:white; border-radius:10px; padding:1.2rem 1.8rem;
                margin-bottom:1.2rem; display:flex; flex-wrap:wrap;
                align-items:center; justify-content:space-between; gap:1rem;">
        <div>
            <div style="font-size:1.3rem; font-weight:700; font-family:'EB Garamond',serif;">
                {emp.get("name","")}
            </div>
            <div style="color:#e4c47a; font-size:0.82rem; margin-top:3px;">
                {emp.get("employee_id","")} &nbsp;|&nbsp; {emp.get("designation","")} &nbsp;|&nbsp; {emp.get("department","")}
            </div>
        </div>
        <div style="display:flex; gap:1.5rem; flex-wrap:wrap;">
            {"".join(f'<div style="text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:#c9a84c;">{v}</div><div style="font-size:0.7rem;opacity:0.6;text-transform:uppercase;">{l}</div></div>'
                      for v, l in [(promos,"Promotions"),(transfers,"Transfers"),(leaves,"Leaves"),(docs,"Documents")])}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── PDF Generation button ──────────────────────────────────────────────────
    col_btn, col_info = st.columns([2, 5])
    with col_btn:
        if st.button("📄 Generate Service Book PDF", type="primary", use_container_width=True):
            with st.spinner("Generating PDF…"):
                try:
                    pdf_bytes = generate_pdf(emp)
                    log_audit("PDF Generated",
                              f"Service Book PDF generated for {emp.get('name','')}",
                              employee_id=employee_id)
                    st.session_state[f"pdf_{employee_id}"] = pdf_bytes
                    st.success("✅ PDF generated successfully!")
                except Exception as ex:
                    st.error(f"PDF generation failed: {ex}")

    # Download button if PDF is ready
    if f"pdf_{employee_id}" in st.session_state:
        with col_btn:
            st.download_button(
                label="⬇️ Download PDF",
                data=st.session_state[f"pdf_{employee_id}"],
                file_name=f"ServiceBook_{employee_id}_{date.today()}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Accordion view of all sections ────────────────────────────────────────
    with st.expander("👤 Personal Details", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            **Employee ID:** `{emp.get("employee_id","")}`  
            **Full Name:** {emp.get("name","")}  
            **Date of Birth:** {emp.get("date_of_birth","")}  
            **Gender:** {emp.get("gender","")}  
            **Blood Group:** {emp.get("blood_group","—")}  
            """)
        with c2:
            st.markdown(f"""
            **Department:** {emp.get("department","")}  
            **Designation:** {emp.get("designation","")}  
            **Date of Joining:** {emp.get("date_of_joining","")}  
            **Appt. Order:** {emp.get("appointment_order","—")}  
            """)
        with c3:
            st.markdown(f"""
            **Phone:** {emp.get("phone","—")}  
            **Email:** {emp.get("email","—")}  
            **PAN:** {emp.get("pan","—")}  
            **Aadhaar:** {emp.get("aadhaar","—")}  
            """)
        st.markdown(f"**Address:** {emp.get('address','—')}")

    with st.expander(f"📈 Promotion History ({len(emp.get('promotions',[]))})"):
        _render_table(
            ["Date", "Old Designation", "New Designation", "Order No.", "Remarks"],
            [[r.get("promotion_date",""), r.get("old_designation",""),
              r.get("new_designation",""), r.get("order_number",""), r.get("remarks","")] 
             for r in emp.get("promotions",[])]
        )

    with st.expander(f"🔄 Transfer History ({len(emp.get('transfers',[]))})"):
        _render_table(
            ["Date", "From", "To", "Order No.", "Remarks"],
            [[r.get("transfer_date",""), r.get("from_location",""),
              r.get("to_location",""), r.get("order_number",""), r.get("remarks","")]
             for r in emp.get("transfers",[])]
        )

    with st.expander(f"🌿 Leave Records ({len(emp.get('leave_records',[]))})"):
        _render_table(
            ["Leave Type", "Start", "End", "Days", "Sanction Authority", "Order No."],
            [[r.get("leave_type",""), r.get("start_date",""), r.get("end_date",""),
              str(r.get("days","")), r.get("sanction_auth",""), r.get("sanction_order","")]
             for r in emp.get("leave_records",[])]
        )

    with st.expander(f"💰 Pay Revisions ({len(emp.get('pay_revisions',[]))})"):
        _render_table(
            ["Eff. Date", "Old Pay (₹)", "New Pay (₹)", "Pay Scale", "Order No.", "Remarks"],
            [[r.get("effective_date",""), f"₹{r.get('old_pay',''):,}",
              f"₹{r.get('new_pay',''):,}", r.get("pay_scale",""),
              r.get("order_number",""), r.get("remarks","")]
             for r in emp.get("pay_revisions",[])]
        )

    with st.expander(f"🎓 Training Records ({len(emp.get('training_records',[]))})"):
        _render_table(
            ["Training Name", "Institution", "Duration", "Start", "End", "Cert. No."],
            [[r.get("training_name",""), r.get("institution",""), r.get("duration",""),
              r.get("start_date",""), r.get("end_date",""), r.get("cert_number","")]
             for r in emp.get("training_records",[])]
        )

    with st.expander(f"🏆 Awards & Recognition ({len(emp.get('awards',[]))})"):
        _render_table(
            ["Award", "Awarded By", "Date", "Description"],
            [[r.get("award_name",""), r.get("awarded_by",""),
              r.get("award_date",""), r.get("description","")]
             for r in emp.get("awards",[])]
        )

    with st.expander(f"⚖️ Disciplinary Records ({len(emp.get('disciplinary_records',[]))})"):
        _render_table(
            ["Date", "Penalty", "Order No.", "Description", "Authority"],
            [[r.get("date",""), r.get("penalty",""), r.get("order_number",""),
              r.get("description",""), r.get("authority","")]
             for r in emp.get("disciplinary_records",[])]
        )

    with st.expander(f"📁 Archived Documents ({len(emp.get('documents',[]))})"):
        _render_table(
            ["Doc Type", "Title", "Date", "Ref No.", "File", "Uploaded On"],
            [[d.get("doc_type",""), d.get("title",""), d.get("doc_date",""),
              d.get("ref_number",""), d.get("original_name",""), d.get("uploaded_on","")]
             for d in emp.get("documents",[])]
        )
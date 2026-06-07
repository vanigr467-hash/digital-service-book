"""
Document Archive Module
=======================
Handles upload and management of scanned documents.
Files are saved to disk; metadata is stored in MongoDB.
"""

import streamlit as st
import os
import shutil
from datetime import date
from modules.database import db
from modules.audit import log_audit

UPLOAD_BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_BASE, exist_ok=True)

DOC_TYPES = [
    "Scanned Service Book Page",
    "Appointment Order",
    "Promotion Order",
    "Transfer Order",
    "Leave Sanction",
    "Pay Revision Order",
    "Training Certificate",
    "Award Certificate",
    "Disciplinary Order",
    "Medical Certificate",
    "Identity Document",
    "Other",
]


def _employee_upload_dir(employee_id: str) -> str:
    path = os.path.join(UPLOAD_BASE, employee_id)
    os.makedirs(path, exist_ok=True)
    return path


def show_document_archive(employee_id: str):
    emp = db.employees.find_one({"employee_id": employee_id})
    if not emp:
        st.error(f"Employee {employee_id} not found.")
        return

    st.markdown("""
    <div class="page-header">
        <h1>📁 Document Archive</h1>
        <p>Upload and manage scanned documents for the selected employee</p>
    </div>
    """, unsafe_allow_html=True)

    # Employee header
    st.markdown(f"""
    <div style="background:white; border:1px solid #d4ccc0; border-left:5px solid #c9a84c;
                border-radius:8px; padding:0.8rem 1.2rem; margin-bottom:1rem;">
        <span style="background:#0d1f3c; color:#e4c47a; font-size:0.8rem; font-weight:700;
                     padding:0.25rem 0.65rem; border-radius:4px;">{emp.get("employee_id","")}</span>&nbsp;&nbsp;
        <strong style="font-size:1rem;">{emp.get("name","")}</strong>
        <span style="color:#8888aa; font-size:0.85rem;">— {emp.get("designation","")}, {emp.get("department","")}</span>
    </div>
    """, unsafe_allow_html=True)

    tab_upload, tab_view = st.tabs(["📤 Upload Document", "📂 Archived Documents"])

    # ── Upload ─────────────────────────────────────────────────────────────────
    with tab_upload:
        st.markdown('<div class="section-title">📤 Upload New Document</div>', unsafe_allow_html=True)

        with st.form("doc_upload_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                doc_type  = st.selectbox("Document Type *", DOC_TYPES)
                doc_title = st.text_input("Document Title / Description *")
            with c2:
                doc_date   = st.date_input("Document Date *")
                ref_number = st.text_input("Reference / Order Number")
            remarks  = st.text_area("Remarks", height=60)
            uploaded = st.file_uploader(
                "Upload File (PDF, JPG, PNG) *",
                type=["pdf", "jpg", "jpeg", "png"],
                accept_multiple_files=False
            )
            submitted = st.form_submit_button("📤 Upload Document", type="primary", use_container_width=True)

        if submitted:
            errors = []
            if not doc_title.strip(): errors.append("Document title is required.")
            if not uploaded:          errors.append("Please select a file to upload.")
            if errors:
                for e in errors: st.error(e)
            else:
                # Save file
                upload_dir = _employee_upload_dir(employee_id)
                safe_name  = f"{employee_id}_{doc_type.replace(' ','_')}_{doc_date}_{uploaded.name}"
                safe_name  = "".join(c for c in safe_name if c.isalnum() or c in "._-")
                file_path  = os.path.join(upload_dir, safe_name)

                with open(file_path, "wb") as f:
                    f.write(uploaded.getbuffer())

                file_size = os.path.getsize(file_path)

                doc_meta = {
                    "doc_type":    doc_type,
                    "title":       doc_title.strip(),
                    "doc_date":    str(doc_date),
                    "ref_number":  ref_number.strip(),
                    "remarks":     remarks.strip(),
                    "file_name":   safe_name,
                    "file_path":   file_path,
                    "file_size":   file_size,
                    "original_name": uploaded.name,
                    "mime_type":   uploaded.type,
                    "uploaded_on": str(date.today()),
                }
                db.employees.update_one(
                    {"employee_id": employee_id},
                    {"$push": {"documents": doc_meta}}
                )
                log_audit("Document Uploaded", f"'{doc_title}' ({doc_type})", employee_id=employee_id)
                st.success(f"✅ Document **'{doc_title}'** uploaded successfully! "
                           f"({file_size/1024:.1f} KB)")
                st.rerun()

    # ── View archived documents ────────────────────────────────────────────────
    with tab_view:
        emp = db.employees.find_one({"employee_id": employee_id})
        documents = emp.get("documents", [])

        if not documents:
            st.info("No documents uploaded yet. Use the Upload tab to archive documents.")
            return

        # Filter bar
        c1, c2 = st.columns([2, 1])
        with c1:
            search_doc = st.text_input("Search documents", placeholder="Title, type, reference...")
        with c2:
            type_filter = st.selectbox("Filter by type", ["All"] + DOC_TYPES)

        filtered = []
        for d in documents:
            if type_filter != "All" and d.get("doc_type") != type_filter:
                continue
            sq = search_doc.strip().lower()
            if sq:
                haystack = f"{d.get('title','')} {d.get('doc_type','')} {d.get('ref_number','')}".lower()
                if sq not in haystack:
                    continue
            filtered.append(d)

        st.markdown(f"**{len(filtered)} document(s) found**")
        st.markdown("<br/>", unsafe_allow_html=True)

        # Render cards
        for i, doc in enumerate(reversed(filtered)):
            ext = doc.get("original_name","").rsplit(".",1)[-1].upper()
            icon = {"PDF":"📄","JPG":"🖼️","JPEG":"🖼️","PNG":"🖼️"}.get(ext,"📎")
            size_kb = f"{doc.get('file_size',0)/1024:.1f} KB"

            with st.expander(f"{icon}  {doc.get('title','')}  |  {doc.get('doc_type','')}  |  {doc.get('doc_date','')}"):
                cols = st.columns([2, 2, 1])
                with cols[0]:
                    st.markdown(f"""
                    **Type:** {doc.get("doc_type","")}  
                    **Title:** {doc.get("title","")}  
                    **Date:** {doc.get("doc_date","")}  
                    **Ref. No.:** {doc.get("ref_number","—")}  
                    **Remarks:** {doc.get("remarks","—")}  
                    """)
                with cols[1]:
                    st.markdown(f"""
                    **Original File:** {doc.get("original_name","")}  
                    **Size:** {size_kb}  
                    **Uploaded On:** {doc.get("uploaded_on","")}  
                    **MIME:** {doc.get("mime_type","")}  
                    """)
                with cols[2]:
                    # Download button if file exists
                    fpath = doc.get("file_path","")
                    if fpath and os.path.exists(fpath):
                        with open(fpath, "rb") as fh:
                            file_bytes = fh.read()
                        st.download_button(
                            label=f"⬇️ Download",
                            data=file_bytes,
                            file_name=doc.get("original_name", "document"),
                            mime=doc.get("mime_type","application/octet-stream"),
                            key=f"dl_{employee_id}_{i}",
                            use_container_width=True
                        )
                        # Preview for images
                        if ext in ("JPG","JPEG","PNG"):
                            st.image(fpath, use_column_width=True)
                    else:
                        st.warning("File not found on disk (may be in demo mode).")
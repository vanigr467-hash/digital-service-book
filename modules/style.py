"""
Styles Module
=============
Defines the government-office inspired professional theme for the application.
Deep navy + gold palette with clean typography.
"""

import streamlit as st


def apply_styles():
    st.markdown("""
    <style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&family=Source+Sans+3:wght@300;400;600;700&display=swap');

    /* ── Root Variables ── */
    :root {
        --navy:       #0d1f3c;
        --navy-mid:   #162d52;
        --navy-light: #1e3f70;
        --gold:       #c9a84c;
        --gold-light: #e4c47a;
        --cream:      #f8f4ec;
        --white:      #ffffff;
        --text-dark:  #1a1a2e;
        --text-mid:   #4a4a6a;
        --text-light: #8888aa;
        --border:     #d4ccc0;
        --success:    #2e7d5e;
        --danger:     #8b2020;
        --warning:    #8b6020;
        --shadow:     0 2px 12px rgba(13,31,60,0.10);
        --shadow-lg:  0 8px 32px rgba(13,31,60,0.18);
    }

    /* ── Base App ── */
    .stApp {
        background: var(--cream) !important;
        font-family: 'Source Sans 3', sans-serif !important;
        color: var(--text-dark) !important;
    }

    /* ── Hide default Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden !important; }
    .block-container { padding: 1.5rem 2rem !important; max-width: 1400px !important; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--navy) !important;
        border-right: 3px solid var(--gold) !important;
    }
    [data-testid="stSidebar"] > div { padding: 0 !important; }

    .sidebar-header {
        background: linear-gradient(135deg, var(--navy-light), var(--navy));
        padding: 1.5rem 1.2rem 1rem;
        text-align: center;
        border-bottom: 2px solid var(--gold);
    }
    .sidebar-logo {
        font-size: 2.5rem;
        margin-bottom: 0.3rem;
    }
    .sidebar-title {
        font-family: 'EB Garamond', serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--gold-light);
        letter-spacing: 0.5px;
    }
    .sidebar-subtitle {
        font-size: 0.7rem;
        color: rgba(255,255,255,0.5);
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: 2px;
    }

    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        background: transparent !important;
        color: rgba(255,255,255,0.75) !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0.65rem 1.2rem !important;
        text-align: left !important;
        font-family: 'Source Sans 3', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 400 !important;
        letter-spacing: 0.2px;
        transition: all 0.18s ease !important;
        border-left: 3px solid transparent !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(201,168,76,0.12) !important;
        color: var(--gold-light) !important;
        border-left-color: var(--gold) !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: rgba(201,168,76,0.18) !important;
        color: var(--gold-light) !important;
        border-left: 3px solid var(--gold) !important;
        font-weight: 600 !important;
    }

    .sidebar-section-label {
        color: rgba(255,255,255,0.4);
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        padding: 0 1.2rem;
        margin-bottom: 0.3rem;
    }
    .sidebar-footer {
        color: rgba(255,255,255,0.5);
        font-size: 0.78rem;
        padding: 0.8rem 1.2rem;
        text-align: center;
    }

    /* ── Page Header ── */
    .page-header {
        background: linear-gradient(135deg, var(--navy) 0%, var(--navy-light) 100%);
        color: white;
        padding: 1.4rem 2rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 5px solid var(--gold);
        box-shadow: var(--shadow-lg);
    }
    .page-header h1 {
        font-family: 'EB Garamond', serif !important;
        font-size: 1.7rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        color: white !important;
        letter-spacing: 0.3px;
    }
    .page-header p {
        margin: 0.3rem 0 0 !important;
        opacity: 0.7;
        font-size: 0.85rem;
        color: rgba(255,255,255,0.75) !important;
    }

    /* ── Metric Cards ── */
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1.2rem 1.4rem;
        box-shadow: var(--shadow);
        border-top: 4px solid var(--gold);
        height: 100%;
    }
    .metric-card .metric-icon {
        font-size: 1.8rem;
        margin-bottom: 0.4rem;
    }
    .metric-card .metric-value {
        font-family: 'EB Garamond', serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: var(--navy);
        line-height: 1;
    }
    .metric-card .metric-label {
        color: var(--text-light);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 0.3rem;
    }

    /* ── Section Cards ── */
    .section-card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: var(--shadow);
        margin-bottom: 1.2rem;
        border: 1px solid var(--border);
    }
    .section-title {
        font-family: 'EB Garamond', serif;
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--navy);
        margin-bottom: 1rem;
        padding-bottom: 0.6rem;
        border-bottom: 2px solid var(--gold);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ── Info Banner ── */
    .info-banner {
        background: linear-gradient(135deg, #e8f0fe, #f0f4ff);
        border: 1px solid #b8ccf8;
        border-left: 4px solid var(--navy-light);
        border-radius: 8px;
        padding: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-top: 2rem;
        color: var(--navy);
        font-size: 0.95rem;
    }

    /* ── Employee Card ── */
    .employee-card {
        background: white;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--border);
        border-left: 5px solid var(--navy-light);
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: box-shadow 0.2s ease;
    }
    .employee-card:hover {
        box-shadow: var(--shadow-lg);
    }
    .employee-id-badge {
        background: var(--navy);
        color: var(--gold-light);
        font-family: 'EB Garamond', serif;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        letter-spacing: 0.5px;
    }

    /* ── Form Inputs ── */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stDateInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 1.5px solid var(--border) !important;
        border-radius: 5px !important;
        font-family: 'Source Sans 3', sans-serif !important;
        font-size: 0.92rem !important;
        background: white !important;
        color: var(--text-dark) !important;
        transition: border-color 0.18s ease !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--navy-light) !important;
        box-shadow: 0 0 0 2px rgba(30,63,112,0.12) !important;
    }

/* ── Form Labels Fix ── */
label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
.stTextInput label,
.stSelectbox label,
.stDateInput label,
.stTextArea label {
    color: #0d1f3c !important;
    opacity: 1 !important;
    font-weight: 600 !important;
    visibility: visible !important;
}
                
                /* Force visibility inside forms */
[data-testid="stForm"] label,
[data-testid="stForm"] p {
    color: #0d1f3c !important;
    opacity: 1 !important;
}
    /* ── Buttons ── */
    .stButton > button {
        font-family: 'Source Sans 3', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 5px !important;
        letter-spacing: 0.3px !important;
        transition: all 0.18s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: var(--navy) !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: var(--navy-light) !important;
        box-shadow: 0 4px 12px rgba(13,31,60,0.3) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0 !important;
        background: var(--navy) !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 0 0.5rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: rgba(255,255,255,0.6) !important;
        font-family: 'Source Sans 3', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 0.7rem 1rem !important;
        border-radius: 0 !important;
        border-bottom: 3px solid transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--gold-light) !important;
        background: transparent !important;
        border-bottom: 3px solid var(--gold) !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background: white !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        padding: 1.5rem !important;
    }

    /* ── Data Table ── */
    .record-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
    .record-table th {
        background: var(--navy);
        color: var(--gold-light);
        padding: 0.6rem 0.8rem;
        text-align: left;
        font-family: 'Source Sans 3', sans-serif;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .record-table td {
        padding: 0.6rem 0.8rem;
        border-bottom: 1px solid var(--border);
        color: var(--text-dark);
        vertical-align: middle;
    }
    .record-table tr:nth-child(even) td { background: #f9f7f3; }
    .record-table tr:hover td { background: #f0ede6; }

    /* ── Status Badges ── */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.73rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .badge-success { background: #d4edda; color: var(--success); }
    .badge-info    { background: #d1ecf1; color: #0c5460; }
    .badge-warning { background: #fff3cd; color: var(--warning); }
    .badge-danger  { background: #f8d7da; color: var(--danger); }

    /* ── Alerts ── */
    .stSuccess > div { border-radius: 6px !important; }
    .stError   > div { border-radius: 6px !important; }
    .stWarning > div { border-radius: 6px !important; }
    .stInfo    > div { border-radius: 6px !important; }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: var(--cream) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        font-family: 'Source Sans 3', sans-serif !important;
        font-weight: 600 !important;
        color: var(--navy) !important;
    }

    /* ── Dividers ── */
    hr { border: none; border-top: 1px solid var(--border); margin: 1.2rem 0; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--cream); }
    ::-webkit-scrollbar-thumb { background: #b0a898; border-radius: 3px; }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        border: 2px dashed var(--border) !important;
        border-radius: 8px !important;
        background: #faf8f4 !important;
    }

    /* ── Service Book PDF preview area ── */
    .pdf-section-header {
        background: var(--navy);
        color: var(--gold-light);
        font-family: 'EB Garamond', serif;
        font-size: 1rem;
        font-weight: 600;
        padding: 0.5rem 1rem;
        margin: 1rem 0 0.5rem;
        border-radius: 4px;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)
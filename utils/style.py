import streamlit as st

WHITE    = "#FFFFFF"
SURFACE  = "#F8F9FA"
BORDER   = "#E4E7EB"
BORDER_2 = "#CBD2DA"
TEXT     = "#111827"
TEXT_SUB = "#313E5A"
TEXT_XS  = "#9CA3AF"
ACCENT   = "#1D4ED8"
ACCENT_L = "#EFF6FF"
GREEN    = "#059669"
AMBER    = "#D97706"
RED      = "#DC2626"
SIDEBAR  = "#1A1D23"


def inject_custom_css() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    }
    .stApp { background: #F0F2F5 !important; }

    h1 { font-size: 1.65rem !important; font-weight: 700 !important;
         color: #111827 !important; letter-spacing: -0.4px; margin-bottom: 4px !important; }
    h2 { font-size: 1.25rem !important; font-weight: 600 !important; color: #111827 !important; }
    h3 { font-size: 1.05rem !important; font-weight: 600 !important; color: #111827 !important; }
    h4 { font-size: 0.95rem !important; font-weight: 600 !important; color: #111827 !important; }
    p, li { color: #111827 !important; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #1A1D23 !important;
        border-right: 1px solid #2C2F38 !important;
    }
    section[data-testid="stSidebar"] * { color: #C9CDD6 !important; }
    section[data-testid="stSidebar"] .stRadio > div > label {
        border-radius: 7px !important;
        padding: 9px 13px !important;
        margin-bottom: 2px;
        color: #9AA3B0 !important;
        font-size: 0.875rem;
        font-weight: 500;
        transition: background 0.15s ease, color 0.15s ease;
        border: 1px solid transparent;
    }
    section[data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(255,255,255,0.07) !important;
        color: #E8EAF0 !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.08) !important;
        color: #9AA3B0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 7px !important;
        font-size: 0.83rem !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.13) !important;
        color: #E8EAF0 !important;
    }

    /* Buttons */
    .stButton > button {
        background: #9CA3AF !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        padding: 9px 20px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.18) !important;
        transition: background 0.15s ease !important;
        transform: none !important;
    }
    .stButton > button:hover {
        background: #2D3748 !important;
        box-shadow: 0 3px 8px rgba(0,0,0,0.2) !important;
        transform: none !important;
    }
    .stDownloadButton > button {
        background: #059669 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stDownloadButton > button:hover {
        background: #047857 !important;
        transform: none !important;
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: #FFFFFF !important;
        border: 1.5px solid #E4E7EB !important;
        border-radius: 8px !important;
        color: #111827 !important;
        font-size: 0.9rem !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #1D4ED8 !important;
        box-shadow: 0 0 0 3px rgba(29,78,216,0.1) !important;
    }
    .stTextInput label, .stTextArea label, .stSelectbox label,
    .stFileUploader label, .stSlider label, .stDateInput label, .stTimeInput label {
        color: #111827 !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
    }

    /* File uploader */
    .stFileUploader > div {
        border: 2px dashed #E4E7EB !important;
        border-radius: 10px !important;
        background: #F8F9FA !important;
    }
    .stFileUploader > div:hover { border-color: #1D4ED8 !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0; background: transparent;
        border-bottom: 2px solid #E4E7EB; padding: 0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 0 !important;
        padding: 10px 20px !important;
        color: #6B7280 !important;
        font-weight: 500; font-size: 0.875rem !important;
        background: transparent !important;
        border-bottom: 2px solid transparent;
        margin-bottom: -2px;
    }
    .stTabs [aria-selected="true"] {
        color: #1D4ED8 !important;
        border-bottom: 2px solid #1D4ED8 !important;
        font-weight: 600 !important;
        background: transparent !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #F8F9FA !important;
        border: 1px solid #E4E7EB !important;
        border-radius: 8px !important;
        color: #111827 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    /* Alerts */
    .stAlert > div { border-radius: 8px !important; font-size: 0.875rem !important; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #F0F2F5; }
    ::-webkit-scrollbar-thumb { background: #CBD2DA; border-radius: 3px; }

    /* Cards */
    .wcard, .glass-card {
        background: #FFFFFF;
        border: 1.5px solid #E4E7EB;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }

    .stat-card {
        background: #FFFFFF;
        border: 1.5px solid #E4E7EB;
        border-radius: 12px;
        padding: 18px 20px;
        border-top: 3px solid #111827;
        text-align: center;
    }
    .stat-icon  { font-size: 1.4rem; margin-bottom: 4px; }
    .stat-number { font-size: 2rem; font-weight: 700; color: #111827; line-height: 1.1; margin: 4px 0; }
    .stat-label  { font-size: 0.72rem; font-weight: 700; color: #6B7280;
                   text-transform: uppercase; letter-spacing: 0.8px; }

    .app-card {
        background: #FFFFFF;
        border: 1.5px solid #E4E7EB;
        border-radius: 10px;
        padding: 14px 18px;
        margin: 5px 0;
        transition: border-color 0.15s;
    }
    .app-card:hover { border-color: #CBD2DA; }
    .app-position { color: #111827; font-size: 1rem; font-weight: 700; }
    .app-meta     { color: #6B7280; font-size: 0.83rem; margin-top: 3px; }

    .sbadge {
        display: inline-block; padding: 2px 10px;
        border-radius: 20px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.3px;
    }
    .sbadge-applied   { background:#EFF6FF; color:#1D4ED8; border:1px solid #BFDBFE; }
    .sbadge-interview { background:#FFFBEB; color:#92400E; border:1px solid #FDE68A; }
    .sbadge-offer     { background:#ECFDF5; color:#065F46; border:1px solid #A7F3D0; }
    .sbadge-rejected  { background:#FEF2F2; color:#991B1B; border:1px solid #FECACA; }

    .q-card {
        background: #F8F9FA;
        border-left: 3px solid #1D4ED8;
        border-radius: 0 8px 8px 0;
        padding: 14px 18px; margin: 7px 0;
    }
    .q-num  { color: #1D4ED8; font-size: 0.72rem; font-weight: 700;
              text-transform: uppercase; letter-spacing: 0.5px; }
    .q-text { color: #111827; font-size: 0.93rem; font-weight: 500; margin-top: 4px; }
    .q-tip  { color: #6B7280; font-size: 0.81rem; margin-top: 6px; font-style: italic; }

    .letter-preview {
        background: #FFFFFF;
        border: 1.5px solid #E4E7EB;
        border-radius: 10px;
        padding: 28px 32px;
        font-family: 'Georgia', serif;
        font-size: 0.95rem;
        line-height: 1.85;
        color: #111827;
        white-space: pre-wrap;
    }

    .hero-section {
        background: #FFFFFF;
        border: 1.5px solid #E4E7EB;
        border-radius: 14px;
        padding: 28px 32px;
        margin-bottom: 24px;
    }
    .hero-title    { font-size: 1.5rem; font-weight: 700; color: #111827; margin-bottom: 6px; }
    .hero-subtitle { color: #6B7280; font-size: 0.95rem; line-height: 1.5; }

    .feature-card {
        background: #FFFFFF;
        border: 1.5px solid #E4E7EB;
        border-radius: 12px;
        padding: 20px 18px;
        text-align: center; height: 100%;
        transition: box-shadow 0.15s ease, border-color 0.15s ease;
    }
    .feature-card:hover {
        border-color: #CBD2DA;
        box-shadow: 0 4px 16px rgba(0,0,0,0.07);
    }
    .feature-icon  { font-size: 1.8rem; margin-bottom: 10px; }
    .feature-title { font-weight: 700; font-size: 0.95rem; color: #111827; margin-bottom: 5px; }
    .feature-desc  { font-size: 0.8rem; color: #6B7280; line-height: 1.5; }

    .fancy-divider { height: 1px; background: #E4E7EB; margin: 20px 0; }

    .status-pill {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 4px 12px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600;
    }
    .pill-ok  { background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }
    .pill-err { background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }

    .tips-card {
        background: #FFFFFF; border: 1.5px solid #E4E7EB;
        border-radius: 12px; padding: 20px 24px;
    }
    .tips-card h4 { color: #111827 !important; margin-top: 0; font-size: 0.9rem !important; }
    .tips-card li { color: #6B7280 !important; font-size: 0.87rem; line-height: 2; }
    </style>
    """, unsafe_allow_html=True)


def stat_card(icon: str, number: str, label: str) -> str:
    return (
        f'<div class="stat-card">'
        f'<div class="stat-icon">{icon}</div>'
        f'<div class="stat-number">{number}</div>'
        f'<div class="stat-label">{label}</div>'
        f'</div>'
    )

def status_badge(status: str) -> str:
    cls = {
        "Applied": "sbadge-applied", "Interview": "sbadge-interview",
        "Offer": "sbadge-offer", "Rejected": "sbadge-rejected",
    }.get(status, "sbadge-applied")
    return f'<span class="sbadge {cls}">{status}</span>'

def fancy_divider() -> None:
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

def glass_card(content: str) -> str:
    return f'<div class="glass-card">{content}</div>'

def question_card(number: int, text: str, tip: str = "") -> str:
    tip_html = f'<div class="q-tip">💡 {tip}</div>' if tip else ""
    return (
        f'<div class="q-card">'
        f'<div class="q-num">Q{number}</div>'
        f'<div class="q-text">{text}</div>'
        f'{tip_html}</div>'
    )

def hero_section(title: str, subtitle: str) -> str:
    return (
        f'<div class="hero-section">'
        f'<div class="hero-title">{title}</div>'
        f'<div class="hero-subtitle">{subtitle}</div>'
        f'</div>'
    )

def feature_card(icon: str, title: str, description: str) -> str:
    return (
        f'<div class="feature-card">'
        f'<div class="feature-icon">{icon}</div>'
        f'<div class="feature-title">{title}</div>'
        f'<div class="feature-desc">{description}</div>'
        f'</div>'
    )

def page_header(title: str, subtitle: str = "") -> None:
    sub = f'<p style="color:#6B7280;font-size:0.93rem;margin:4px 0 0;">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<div style="margin-bottom:24px;"><h1 style="margin:0;">{title}</h1>{sub}</div>',
        unsafe_allow_html=True,
    )

def infobox(text: str) -> None:
    st.markdown(
        f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;'
        f'padding:12px 16px;font-size:0.875rem;color:#1D4ED8;">{text}</div>',
        unsafe_allow_html=True,
    )

def ollama_pill(ok: bool, msg: str) -> None:
    cls = "pill-ok" if ok else "pill-err"
    st.markdown(f'<span class="status-pill {cls}">● {msg}</span>', unsafe_allow_html=True)
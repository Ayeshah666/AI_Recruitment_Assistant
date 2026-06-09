import streamlit as st
from utils.auth import authenticate_user, logout
from utils.style import (
    inject_custom_css, stat_card, hero_section,
    feature_card, fancy_divider, ollama_pill,
)
from utils.database import db

st.set_page_config(
    page_title="Job Search Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()

if not authenticate_user():
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px 0 12px; text-align: center;">
        <div style="font-size: 2rem;">💼</div>
        <div style="font-size: 1rem; font-weight: 700; color: #E8EAF0; margin-top: 6px;">
            Job Search Assistant
        </div>
        <div style="color: #5A6070; font-size: 0.72rem; margin-top: 2px;">v2.0 · Powered by Ollama</div>
    </div>
    """, unsafe_allow_html=True)

    fancy_divider()

    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.06); border-radius: 8px;
                padding: 10px 14px; margin-bottom: 14px;">
        <div style="color: #5A6070; font-size: 0.72rem; text-transform: uppercase;
                    letter-spacing: 1px; font-weight: 600;">Signed in as</div>
        <div style="color: #E8EAF0; font-weight: 600; font-size: 0.9rem; margin-top: 2px;">
            {st.session_state.get("name", "User")}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div style="color:#5A6070;font-size:0.7rem;text-transform:uppercase;'
        'letter-spacing:1.2px;font-weight:700;margin-bottom:8px;">Navigation</div>',
        unsafe_allow_html=True,
    )

    pages = {
        "Dashboard":            "dashboard",
        "Resume Feedback":      "resume",
        "Cover Letter":         "cover_letter",
        "Application Tracker":  "tracker",
        "Interview Prep":       "interview",
    }

    # Prepend icons for display only
    icons = {
        "Dashboard": "🏠",
        "Resume Feedback": "📝",
        "Cover Letter": "✉️",
        "Application Tracker": "📊",
        "Interview Prep": "🎯",
    }
    display_labels = [f"{icons[k]}  {k}" for k in pages]
    selection = st.radio("nav", display_labels, label_visibility="collapsed")
    selected_page = pages[selection.split("  ", 1)[1]]

    fancy_divider()

    if st.button("Sign Out", use_container_width=True, key="logout_btn"):
        logout()

    fancy_divider()

    # Ollama status — shown at bottom of sidebar
    try:
        from utils.ollama_client import check_ollama
        ok, msg = check_ollama()
        ollama_pill(ok, msg)
    except Exception:
        pass


# ── Pages ─────────────────────────────────────────────────────────────────────
if selected_page == "dashboard":
    user_id = st.session_state.get("user", "demo_user")
    name    = st.session_state.get("name", "User")

    st.markdown(
        hero_section(
            f"Welcome back, {name} 👋",
            "Your private, local job search workspace — track applications, "
            "sharpen your resume, and prepare for interviews.",
        ),
        unsafe_allow_html=True,
    )

    stats = db.get_stats(user_id)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(stat_card("📋", str(stats["total"]),     "Applications"), unsafe_allow_html=True)
    with c2: st.markdown(stat_card("📨", str(stats["applied"]),   "Applied"),      unsafe_allow_html=True)
    with c3: st.markdown(stat_card("🎤", str(stats["interview"]), "Interviews"),   unsafe_allow_html=True)
    with c4: st.markdown(stat_card("🎉", str(stats["offer"]),     "Offers"),       unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Quick Actions")
    f1, f2, f3, f4 = st.columns(4)
    with f1: st.markdown(feature_card("📝", "Resume Optimizer",
        "Upload your resume and get AI-powered feedback with keyword gap analysis"), unsafe_allow_html=True)
    with f2: st.markdown(feature_card("✉️", "Cover Letter",
        "Generate tailored cover letters from your resume and the job posting"), unsafe_allow_html=True)
    with f3: st.markdown(feature_card("📊", "Application Tracker",
        "Track every application with status, notes, and analytics"), unsafe_allow_html=True)
    with f4: st.markdown(feature_card("🎯", "Interview Prep",
        "Role-specific questions with tips on what strong answers look like"), unsafe_allow_html=True)

    fancy_divider()
    st.markdown("### Job Search Tips")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown("""
        <div class="tips-card">
            <h4>📌 Resume</h4>
            <ul>
                <li>Tailor your resume for every application — mirror the JD language</li>
                <li>Quantify every achievement — numbers, percentages, dollar values</li>
                <li>Start bullets with action verbs: Led, Built, Reduced, Shipped</li>
                <li>Keep it 1 page if under 5 years experience, 2 max otherwise</li>
                <li>Run it through the Resume Feedback tool for keyword gaps</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with t2:
        st.markdown("""
        <div class="tips-card">
            <h4>🎤 Interviews</h4>
            <ul>
                <li>Research the company's latest news, product, and culture</li>
                <li>Use STAR method for every behavioural question</li>
                <li>Prepare 3–5 thoughtful questions to ask the interviewer</li>
                <li>Practise out loud — recording yourself is uncomfortable but it works</li>
                <li>Send a follow-up thank-you email within 24 hours</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif selected_page == "resume":
    from views.Resume_Feedback import main as view
    view()

elif selected_page == "cover_letter":
    from views.Cover_Letter import main as view
    view()

elif selected_page == "tracker":
    from views.Application_Tracker import main as view
    view()

elif selected_page == "interview":
    from views.Interview_Prep import main as view
    view()
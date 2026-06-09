import streamlit as st
from utils.database import db
from utils.style import fancy_divider, stat_card, status_badge
from datetime import datetime


def _fmt_date(d) -> str:
    if isinstance(d, datetime):
        return d.strftime("%b %d, %Y")
    try:
        return str(d)
    except Exception:
        return "—"


def display_application(app: dict, key: str) -> None:
    status   = app.get("status", "Applied")
    company  = app.get("company", "Unknown")
    position = app.get("position", "Unknown")
    date_str = _fmt_date(app.get("applied_date", datetime.now()))

    st.markdown(f"""
    <div class="app-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:5px;">
                    <span class="app-position">{position}</span>
                    {status_badge(status)}
                </div>
                <div class="app-meta">🏢 {company} &nbsp;&nbsp; 📅 {date_str}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    b1, b2, _ = st.columns([1, 1, 5])
    with b1:
        if st.button("Edit", key=f"edit_{key}"):
            st.session_state.editing = key
    with b2:
        if st.button("Delete", key=f"del_{key}"):
            st.session_state.deleting = key


def application_form(existing: dict = None, key_suffix: str = "new"):
    defaults = existing or {
        "company": "", "position": "", "status": "Applied",
        "applied_date": datetime.now(), "notes": "",
    }
    statuses = ["Applied", "Interview", "Offer", "Rejected"]

    with st.form(key=f"app_form_{key_suffix}"):
        c1, c2 = st.columns(2)
        with c1:
            company = st.text_input("Company", value=defaults["company"], placeholder="Company name")
            status  = st.selectbox("Status", statuses,
                                   index=statuses.index(defaults.get("status", "Applied")))
        with c2:
            position     = st.text_input("Position", value=defaults["position"], placeholder="Job title")
            applied_date = st.date_input("Application Date",
                                         value=defaults.get("applied_date", datetime.now()))

        notes     = st.text_area("Notes (optional)", value=defaults.get("notes", ""),
                                  placeholder="Anything worth remembering…", height=80)
        submitted = st.form_submit_button("Save Application", use_container_width=True)

        if submitted:
            if not company or not position:
                st.error("Company and Position are required.")
                return None
            return {
                "company": company.strip(),
                "position": position.strip(),
                "status": status,
                "applied_date": applied_date,
                "notes": notes.strip(),
                "last_updated": datetime.now(),
            }
    return None


def main():
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h1 style="margin-bottom:4px;">Application Tracker</h1>
        <p style="color:#6B7280;font-size:0.93rem;margin:0;">
            Every application in one place — add, update, and track your progress.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if "editing"  not in st.session_state: st.session_state.editing  = None
    if "deleting" not in st.session_state: st.session_state.deleting = None

    user_id = st.session_state.get("user", "demo_user")
    stats   = db.get_stats(user_id)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(stat_card("📋", str(stats["total"]),     "Total"),      unsafe_allow_html=True)
    with c2: st.markdown(stat_card("📨", str(stats["applied"]),   "Applied"),    unsafe_allow_html=True)
    with c3: st.markdown(stat_card("🎤", str(stats["interview"]), "Interviews"), unsafe_allow_html=True)
    with c4: st.markdown(stat_card("🎉", str(stats["offer"]),     "Offers"),     unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    fancy_divider()

    with st.expander("➕  Add New Application", expanded=st.session_state.editing is None):
        new_app = application_form()
        if new_app:
            db.save_application(user_id, new_app)
            st.success("Application saved!")
            st.rerun()

    fancy_divider()
    st.markdown("### Your Applications")

    tab_labels = ["All", "Applied", "Interview", "Offer", "Rejected"]
    tab_filters = [None, "Applied", "Interview", "Offer", "Rejected"]
    tabs = st.tabs(tab_labels)

    for tab_idx, (tab, status_filter) in enumerate(zip(tabs, tab_filters)):
        with tab:
            applications = db.get_applications(user_id, status_filter)

            if not applications:
                empty_msg = "No applications yet." if tab_idx == 0 else f"No '{status_filter}' applications."
                st.markdown(f"""
                <div class="glass-card" style="text-align:center; padding:40px 20px;">
                    <div style="font-size:2.5rem; margin-bottom:12px;">📂</div>
                    <div style="font-weight:600; color:#111827; margin-bottom:6px;">{empty_msg}</div>
                    <div style="color:#6B7280; font-size:0.87rem;">
                        {"Use the 'Add New Application' form above to get started." if tab_idx == 0 else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                continue

            for idx, app in enumerate(applications):
                app_key = f"{tab_idx}_{idx}"

                # ── Delete confirmation ────────────────────────────────────
                if st.session_state.deleting == app_key:
                    st.warning(
                        f"Delete **{app.get('position')}** at **{app.get('company')}**?")
                    yes, no, _ = st.columns([1, 1, 4])
                    with yes:
                        if st.button("Yes, delete", key=f"cfdel_{app_key}"):
                            db.delete_application(app.get("_id"))
                            st.session_state.deleting = None
                            st.success("Deleted.")
                            st.rerun()
                    with no:
                        if st.button("Cancel", key=f"nodeldel_{app_key}"):
                            st.session_state.deleting = None
                            st.rerun()
                    continue

                # ── Edit form ──────────────────────────────────────────────
                if st.session_state.editing == app_key:
                    st.markdown(f"""
                    <div class="glass-card" style="padding:16px 20px; margin-bottom:4px;">
                        <span style="font-weight:600; color:#111827;">
                            Editing: {app.get("position")} at {app.get("company")}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                    edited = application_form(app, key_suffix=f"edit_{app_key}")
                    if edited:
                        db.update_application(app.get("_id"), edited)
                        st.session_state.editing = None
                        st.success("Updated!")
                        st.rerun()
                    if st.button("Cancel", key=f"cancel_edit_{app_key}"):
                        st.session_state.editing = None
                        st.rerun()
                else:
                    display_application(app, app_key)


if __name__ == "__main__":
    main()
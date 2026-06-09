import bcrypt
import streamlit as st

from utils.database import db


# ─────────────────────────────────────────────
# Password helpers
# ─────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


# ─────────────────────────────────────────────
# Main gate
# ─────────────────────────────────────────────

def authenticate_user() -> bool:
    """
    Call at the top of app.py.
    Returns True if the user is logged in, False otherwise (and renders the login UI).
    """
    if st.session_state.get("authenticated"):
        return True

    _render_auth_page()
    return False


def logout() -> None:
    for key in ("authenticated", "user", "name", "username"):
        st.session_state.pop(key, None)
    st.rerun()


# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────

def _render_auth_page() -> None:
    st.markdown(
        """
        <div style="max-width:420px; margin:64px auto 0;">
            <div style="text-align:center; margin-bottom:32px;">
                <div style="font-size:2.4rem; margin-bottom:8px;">💼</div>
                <div style="font-size:1.5rem; font-weight:700; color:#1E293B;
                            letter-spacing:-0.5px;">AI Recruitment Assistant</div>
                <div style="color:#64748B; font-size:0.9rem; margin-top:4px;">
                    Your local, private job search workspace
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col = st.columns([1, 2, 1])[1]
    with col:
        tab_in, tab_up = st.tabs(["Sign in", "Create account"])
        with tab_in:
            _login_form()
        with tab_up:
            _register_form()


def _login_form() -> None:
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", use_container_width=True)

    if submitted:
        if not username or not password:
            st.error("Fill in both fields.")
            return
        user = db.get_user(username)
        if user and verify_password(password, user.get("password", "")):
            _set_session(username, user.get("name", username))
        else:
            st.error("Wrong username or password.")

    st.divider()
    st.caption("Just exploring?")
    if st.button("Continue as demo user", use_container_width=True):
        _set_session("demo_user", "Demo User")


def _register_form() -> None:
    with st.form("register"):
        name = st.text_input("Full name")
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password", help="Minimum 8 characters")
        confirm = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Create account", use_container_width=True)

    if submitted:
        errors = []
        if not all([name, email, username, password, confirm]):
            errors.append("All fields are required.")
        if password and len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password and password != confirm:
            errors.append("Passwords do not match.")
        if email and "@" not in email:
            errors.append("Enter a valid email address.")

        if errors:
            for e in errors:
                st.error(e)
            return

        ok = db.create_user(username, email, name, hash_password(password))
        if ok:
            st.success("Account created — sign in on the other tab.")
        else:
            st.error("That username is taken. Choose another.")


def _set_session(username: str, display_name: str) -> None:
    st.session_state["authenticated"] = True
    st.session_state["user"] = username
    st.session_state["username"] = username
    st.session_state["name"] = display_name
    st.rerun()

import os
import streamlit as st
from frontend.components.navbar import render_header
from frontend.utils.api_client import api_client
from frontend.translations import t

def render_settings_view():
    """Renders the Organic System Settings, User Account & Diagnostics page."""
    lang = st.session_state.get("language", "en")

    render_header(
        f"⚙ {t('nav_settings', lang)} & {t('nav_profile', lang)}",
        "Inspect FastAPI backend server health, manage user authentication profile, and SQLite database storage."
    )

    # ── 1. User Profile & Account Authentication Section ──────────────
    st.subheader(f"👤 {t('nav_profile', lang)}")
    
    current_username = st.session_state.get("username")
    user_id = st.session_state.get("user_id")

    if current_username:
        st.success(t("hello_user", lang, name=current_username))
        c_p1, c_p2 = st.columns([2, 1])
        with c_p1:
            st.markdown(f"• **{t('username', lang)}:** `{current_username}`")
            st.markdown(f"• **User ID:** `{user_id}`")
            st.markdown(f"• **{t('language_label', lang)}:** `{lang.upper()}`")
        with c_p2:
            if st.button(f"🚪 {t('log_out', lang)}", use_container_width=True):
                del st.session_state["username"]
                if "user_id" in st.session_state:
                    del st.session_state["user_id"]
                st.rerun()
    else:
        auth_mode = st.radio(
            "Account Mode",
            options=[t("log_in", lang), t("create_account", lang)],
            horizontal=True,
            label_visibility="collapsed"
        )

        c_auth1, c_auth2 = st.columns([1, 1], gap="medium")

        if auth_mode == t("log_in", lang):
            with c_auth1:
                in_username = st.text_input(t("username", lang), key="login_user")
                in_password = st.text_input(t("password", lang), type="password", key="login_pass")
                if st.button(t("log_in", lang), use_container_width=True):
                    if in_username and in_password:
                        res = api_client.login(in_username, in_password)
                        if "error" in res:
                            st.error(res["error"])
                        else:
                            st.session_state["username"] = res.get("username", in_username)
                            st.session_state["user_id"] = res.get("id")
                            if res.get("preferred_language"):
                                st.session_state["language"] = res["preferred_language"]
                            st.success(f"Welcome, {res.get('username')}!")
                            st.rerun()
                    else:
                        st.warning("Please provide username and password.")
        else:
            with c_auth1:
                up_username = st.text_input(t("username", lang), key="signup_user")
                up_email = st.text_input(t("email", lang), key="signup_email")
                up_fullname = st.text_input(t("full_name", lang), key="signup_full")
            with c_auth2:
                up_farm = st.text_input(t("farm_name", lang), key="signup_farm")
                up_password = st.text_input(t("password", lang), type="password", key="signup_pass")
                up_confirm = st.text_input(t("confirm_password", lang), type="password", key="signup_conf")

            if st.button(t("create_account", lang), use_container_width=True):
                if not up_username or not up_password:
                    st.warning("Username and Password are required.")
                elif up_password != up_confirm:
                    st.error("Passwords do not match.")
                else:
                    res = api_client.signup(up_username, up_password, preferred_language=lang)
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.success(f"Account created successfully for {res.get('username')}!")
                        st.session_state["username"] = res.get("username")
                        st.session_state["user_id"] = res.get("id")
                        st.rerun()

    st.markdown("<div style='margin-bottom: 2.5rem;'></div>", unsafe_allow_html=True)



    # Database Maintenance Controls
    st.subheader(f"🧹 {t('clear_all', lang)} & Storage Controls")
    col_btn, col_txt = st.columns([1, 2])

    with col_btn:
        if st.button(f"🗑 {t('clear_all', lang)}", use_container_width=True):
            res = api_client.clear_all_history()
            if res.get("success"):
                st.success("Successfully deleted all detection records and stored JPEG files.")
                st.rerun()
            else:
                st.error("Failed to clear database.")

    with col_txt:
        st.markdown(
            """
            <div style="font-size: 0.85rem; color: #5c6f64;">
                Note: Clearing history removes scan records from SQLite and cleans up original and annotated images saved in <code>./uploads</code>.
            </div>
            """,
            unsafe_allow_html=True
        )

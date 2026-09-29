import streamlit as st
from frontend.utils.api_client import api_client
from frontend.translations import t, LANGUAGES


def render_sidebar() -> str:
    """Renders the custom organic biophilic sidebar navigation."""
    lang = st.session_state.get("language", "en")

    with st.sidebar:
        # Branding Header
        st.markdown(
            """
            <div style="text-align: center; padding-bottom: 1.25rem; border-bottom: 1px dashed #d8f3dc; margin-bottom: 1.5rem;">
                <div style="font-size: 2.5rem; line-height: 1; margin-bottom: 0.35rem;">🌴</div>
                <h2 style="font-size: 1.6rem; margin: 0; color: #1b4332; font-family: 'Outfit', sans-serif; font-weight: 800;">CocoCare AI</h2>
                <p style="font-size: 0.8rem; color: #5c6f64; margin-top: 0.25rem; font-weight: 500;">
                    Organic Biophilic Coconut Health Platform
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ── Language Selector ─────────────────────────────────────────
        lang_options = {code: f"{info['flag']} {info['native']}" for code, info in LANGUAGES.items()}
        lang_codes = list(lang_options.keys())
        lang_labels = list(lang_options.values())
        current_index = lang_codes.index(lang) if lang in lang_codes else 0

        selected_label = st.selectbox(
            f"🌐 {t('language_label', lang)}",
            options=lang_labels,
            index=current_index,
            key="language_selector",
        )

        # Resolve selected code
        selected_code = lang_codes[lang_labels.index(selected_label)]
        if selected_code != lang:
            st.session_state["language"] = selected_code
            # Persist to backend if user is logged in
            user_id = st.session_state.get("user_id")
            if user_id:
                api_client.update_language(user_id, selected_code)
            st.rerun()

        st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px dashed #e2ece6;'>", unsafe_allow_html=True)

        # Navigation Options (translated)
        pages = {
            "Dashboard": f"⌂ {t('nav_dashboard', lang)}",
            "Farm Profile": f"🌴 {t('nav_farm_management', lang, default='Farm Profile & Planner')}",
            "Farm Operations": f"🌱 {t('nav_farm_operations', lang, default='Irrigation, Soil & Calendar')}",
            "Finance & Growth": f"💰 {t('nav_finance_growth', lang, default='Expenses & Growth Tracker')}",
            "Disease Detection": f"🌿 {t('nav_detect', lang)}",
            "AI Assistant": f"🤖 {t('nav_chatbot', lang)}",
            "Analytics": f"📊 {t('nav_analytics', lang)}",
            "Detection History": f"🕘 {t('nav_history', lang)}",
            "Disease Guide": f"📖 {t('nav_disease_guide', lang)}",
            "Settings": f"⚙ {t('nav_settings', lang)}",
        }

        # Handle page state
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Dashboard"

        selected_label = st.radio(
            "Navigation",
            options=list(pages.values()),
            index=list(pages.keys()).index(st.session_state.current_page) if st.session_state.current_page in pages else 0,
            label_visibility="collapsed"
        )

        # Sync key
        for key, label in pages.items():
            if label == selected_label:
                st.session_state.current_page = key
                break

    return st.session_state.current_page

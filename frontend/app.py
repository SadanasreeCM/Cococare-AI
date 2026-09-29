import os
import sys
import streamlit as st

# Add the project root to the Python path to resolve 'frontend' and 'backend' module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Configure Streamlit Page Settings (Must be first Streamlit command)
st.set_page_config(
    page_title="CocoCare AI — Coconut Tree Disease Detection System",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS Stylesheet
CSS_PATH = os.path.join(os.path.dirname(__file__), "styles", "styles.css")
if os.path.exists(CSS_PATH):
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from frontend.components.sidebar import render_sidebar
from frontend.views.dashboard import render_dashboard_view
from frontend.views.farm_profile import render_farm_profile_view
from frontend.views.farm_operations import render_farm_operations_view
from frontend.views.finance_growth import render_finance_growth_view
from frontend.views.detect import render_detect_view
from frontend.views.history import render_history_view
from frontend.views.analytics import render_analytics_view
from frontend.views.disease_guide import render_disease_guide_view
from frontend.views.settings import render_settings_view
from frontend.components.chatbot_component import render_chatbot_view

def main():
    # Initialize language in session state if not set
    if "language" not in st.session_state:
        st.session_state["language"] = "en"

    # Render Navigation Sidebar and get active page key
    current_page = render_sidebar()

    # Dispatch View based on selection
    if current_page == "Dashboard":
        render_dashboard_view()
    elif current_page == "Farm Profile":
        render_farm_profile_view()
    elif current_page == "Farm Operations":
        render_farm_operations_view()
    elif current_page == "Finance & Growth":
        render_finance_growth_view()
    elif current_page == "Disease Detection":
        render_detect_view()
    elif current_page == "AI Assistant":
        render_chatbot_view()
    elif current_page == "Analytics":
        render_analytics_view()
    elif current_page == "Detection History":
        render_history_view()
    elif current_page == "Disease Guide":
        render_disease_guide_view()
    elif current_page == "Settings":
        render_settings_view()

    # Floating Chatbot Button
    if current_page == "AI Assistant":
        st.markdown('<span id="chat-fab-close"></span>', unsafe_allow_html=True)
        if st.button("✕", key="fab_close", help="Close AI Assistant"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    else:
        st.markdown('<span id="chat-fab-open"></span>', unsafe_allow_html=True)
        if st.button("🌴", key="fab_open", help="Open AI Assistant"):
            st.session_state.current_page = "AI Assistant"
            st.rerun()

if __name__ == "__main__":
    main()

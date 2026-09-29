import streamlit as st

def render_header(title: str, subtitle: str = ""):
    """Renders page header title and subtitle banner."""
    st.markdown(
        f"""
        <div style="margin-bottom: 2rem;">
            <h1 style="margin: 0; font-size: 2.2rem; color: #1b4332; font-weight: 700;">{title}</h1>
            {f'<p style="margin-top: 0.25rem; font-size: 1.05rem; color: #5c6f64;">{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

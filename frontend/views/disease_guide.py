import streamlit as st
from frontend.components.navbar import render_header
from backend.disease_info import get_disease_info, STATIC_DISEASE_INFO
from frontend.translations import t

def render_disease_guide_view():
    """Renders the Organic Biophilic Disease Guide encyclopedia page with static localized content."""
    lang = st.session_state.get("language", "en")

    render_header(
        f"📖 {t('nav_disease_guide', lang)}",
        "Comprehensive diagnostic guide detailing symptoms, root causes, fungicide sprays, and cultural care for coconut palm diseases."
    )

    search_term = st.text_input(
        f"🔍 {t('nav_disease_guide', lang)}",
        placeholder=t("search_logs_ph", lang)
    ).lower().strip()

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    disease_keys = list(STATIC_DISEASE_INFO.keys())
    filtered_keys = []

    for key in disease_keys:
        info = get_disease_info(key, language=lang)
        disp_name = info["display_name"]
        desc = info["description"]
        treat = info["treatment"]
        
        if not search_term:
            filtered_keys.append((key, info))
        else:
            searchable = f"{disp_name} {desc} {treat}".lower()
            if search_term in searchable:
                filtered_keys.append((key, info))

    if not filtered_keys:
        st.info("No matching diseases found in field guide.")
        return

    # Render accordion cards
    for key, info in filtered_keys:
        disp_name = info["display_name"]
        sci_name = info["scientific_name"]
        sev = info["severity"]
        sev_color = info["severity_color"]
        desc = info["description"]
        treatment = info["treatment"]
        
        badge_class = "badge-diseased" if sev == "High" else "badge-warning" if sev == "Medium" else "badge-healthy"

        with st.expander(f"🌴 {disp_name} ({sci_name})", expanded=(key == "leaf_blight")):
            st.markdown(
                f"""
                <div class="organic-card" style="border-left: 6px solid {sev_color}; margin-bottom: 1.25rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem;">
                        <h3 style="margin: 0; color: #1b4332;">{disp_name}</h3>
                        <span class="{badge_class}">Severity: {sev}</span>
                    </div>
                    <p style="font-style: italic; color: #5c6f64; margin-top: 0;">Pathogen: <strong>{sci_name}</strong></p>
                    <p style="font-size: 1rem; color: #1f2923; margin: 0;">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_symp, col_treat = st.columns(2, gap="large")

            with col_symp:
                st.markdown(f"#### 🚨 {t('prediction_breakdown', lang)}")
                for s in info.get("symptoms", []):
                    st.markdown(f"- {s}")

                st.markdown("#### 🧪 Root Causes")
                for c in info.get("causes", []):
                    st.markdown(f"- {c}")

            with col_treat:
                st.markdown(f"#### 🛠 {t('recommended_treatment', lang)}")
                st.markdown(f"1. **{treatment}**")
                for a in info.get("recommended_action", []):
                    if a != treatment:
                        st.markdown(f"- {a}")

                st.markdown("#### 🛡 Long-Term Prevention")
                for p in info.get("prevention", []):
                    st.markdown(f"- {p}")

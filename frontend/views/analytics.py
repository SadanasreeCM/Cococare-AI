import streamlit as st
from frontend.components.navbar import render_header
from frontend.components.cards import render_organic_metric_card
from frontend.components.charts import render_disease_distribution_chart, render_health_ratio_donut
from frontend.utils.api_client import api_client
from frontend.translations import t

def render_analytics_view():
    """Renders the Organic Biophilic Analytics Dashboard page."""
    lang = st.session_state.get("language", "en")

    render_header(
        f"🌱 {t('nav_analytics', lang)}",
        "Comprehensive real-time analytics calculated directly from your SQLite database scan records."
    )

    stats = api_client.get_statistics()

    total_scans = stats.get("total_scans", 0)
    healthy_scans = stats.get("healthy_scans", 0)
    diseased_scans = stats.get("diseased_scans", 0)
    healthy_pct = stats.get("healthy_percentage", 0.0)
    diseased_pct = stats.get("diseased_percentage", 0.0)
    avg_conf = stats.get("average_confidence", 0.0)
    distribution = stats.get("disease_distribution", [])

    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_organic_metric_card(t("total_scans", lang), str(total_scans), icon="🌴", color="#1b4332")
    with m2:
        render_organic_metric_card(t("healthy_pct", lang), f"{healthy_pct:.1f}%", icon="🌿", delta=f"{healthy_scans} {t('healthy_trees', lang)}", color="#2a9d8f")
    with m3:
        render_organic_metric_card(t("active_alerts", lang), f"{diseased_pct:.1f}%", icon="⚠️", delta=f"{diseased_scans} {t('diseases_detected', lang)}", color="#d90429")
    with m4:
        render_organic_metric_card(t("confidence", lang), f"{avg_conf:.1f}%", icon="🎯", color="#f77f00")

    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # Charts Row
    col_dist, col_donut = st.columns([1.3, 1], gap="large")

    with col_dist:
        st.subheader(f"📈 {t('confidence_by_class', lang)}")
        render_disease_distribution_chart(distribution)

    with col_donut:
        st.subheader("🍩 Plantation Health Ratio")
        render_health_ratio_donut(healthy_scans, diseased_scans)

    st.markdown("<div style='margin-bottom: 2.5rem;'></div>", unsafe_allow_html=True)

    # Table Breakdown
    st.subheader("📋 Disease Frequency Breakdown Table")
    if not distribution:
        st.info("No scan records available in database.")
    else:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #e2ece6; border-radius: 20px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.03);">
            <table style="width: 100%; border-collapse: collapse; text-align: left;">
                <thead>
                    <tr style="background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%); color: #ffffff;">
                        <th style="padding: 14px 18px; font-family: 'Outfit', sans-serif;">Disease / Condition</th>
                        <th style="padding: 14px 18px; font-family: 'Outfit', sans-serif;">Scan Count</th>
                        <th style="padding: 14px 18px; font-family: 'Outfit', sans-serif;">Percentage Share</th>
                    </tr>
                </thead>
                <tbody>
            """,
            unsafe_allow_html=True
        )

        for d in distribution:
            raw_d_name = d.get("disease_name", "")
            d_name = t(raw_d_name, lang)
            cnt = d.get("count", 0)
            pct = (cnt / total_scans * 100) if total_scans > 0 else 0
            
            st.markdown(
                f"""
                <tr style="border-bottom: 1px solid #e2ece6;">
                    <td style="padding: 14px 18px; font-weight: 700; color: #1b4332;">{d_name}</td>
                    <td style="padding: 14px 18px;">{cnt}</td>
                    <td style="padding: 14px 18px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="width: 120px; background: #e2ece6; border-radius: 6px; height: 10px; overflow: hidden;">
                                <div style="width: {pct:.0f}%; background: #2d6a4f; height: 100%;"></div>
                            </div>
                            <span style="font-weight: 600;">{pct:.1f}%</span>
                        </div>
                    </td>
                </tr>
                """,
                unsafe_allow_html=True
            )

        st.markdown("</tbody></table></div>", unsafe_allow_html=True)

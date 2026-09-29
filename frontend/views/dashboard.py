import os
import streamlit as st
from frontend.utils.api_client import api_client
from frontend.translations import t
from frontend.components.cards import render_organic_metric_card

def render_dashboard_view():
    """Renders the Complete Phase 4 Coconut Farm Management Dashboard."""
    lang = st.session_state.get("language", "en")
    user = st.session_state.get("user", {})
    user_id = user.get("id", 1) if isinstance(user, dict) else 1

    farm = api_client.get_farm(user_id)
    farm_id = farm.get("id") if farm and isinstance(farm, dict) and farm.get("id") else None

    # ------------------------------------------------------------------
    # 1. Farm Profile Summary / Setup Hero Banner
    # ------------------------------------------------------------------
    if farm and farm_id:
        farm_name = farm.get("name") or farm.get("farm_name", "My Coconut Plantation")
        loc_name = farm.get("location") or farm.get("location_name", "Pollachi")
        total_acres = farm.get("land_area") or farm.get("total_area_acres", 0.0)
        tree_count = farm.get("existing_trees") or farm.get("tree_count", 0)
        land_unit = farm.get("land_unit", "acres")
        soil_type = str(farm.get("soil_type", "loamy")).title()
        irr_method = str(farm.get("irrigation_method", "drip")).title()

        st.markdown(
            f"""
            <div class="organic-card" style="background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%); color: white; padding: 1.75rem 2rem; border-radius: 24px; margin-bottom: 2rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                    <div>
                        <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #74c69d; font-weight: 700;">🌴 Plantation Profile</div>
                        <h2 style="margin: 0.25rem 0 0.5rem 0; color: #ffffff; font-size: 1.8rem;">{farm_name}</h2>
                        <div style="font-size: 0.95rem; color: #d8f3dc; display: flex; gap: 1.5rem; flex-wrap: wrap;">
                            <span>📍 <strong>Location:</strong> {loc_name}</span>
                            <span>📐 <strong>Area:</strong> {total_acres} {land_unit}</span>
                            <span>🌴 <strong>Palms:</strong> {tree_count} trees</span>
                        </div>
                    </div>
                    <div style="background: rgba(255,255,255,0.12); backdrop-filter: blur(8px); padding: 0.75rem 1.25rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.2);">
                        <div style="font-size: 0.85rem; color: #d8f3dc;">Soil & Irrigation</div>
                        <strong style="font-size: 1.05rem; color: #ffffff;">{soil_type} Soil • {irr_method}</strong>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            f"""
            <div class="organic-card" style="background: #fff3bf; border-left: 6px solid #f77f00; padding: 1.5rem; margin-bottom: 2rem;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="font-size: 2rem;">⚠️</span>
                    <div>
                        <h4 style="margin: 0; color: #9d0208;">Farm Profile Incomplete</h4>
                        <p style="margin: 0.25rem 0 0 0; font-size: 0.9rem; color: #5c6f64;">
                            Configure your farm profile in the <strong>Farm Profile & Planner</strong> tab to enable tailored irrigation, nutrient, and weather advisories.
                        </p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Quick Action Buttons
    c_btn1, c_btn2, c_btn3 = st.columns([1, 1, 1])
    with c_btn1:
        if st.button(f"🔍 {t('start_scan', lang)}", use_container_width=True):
            st.session_state.current_page = "Disease Detection"
            st.rerun()
    with c_btn2:
        if st.button(f"💧 {t('nav_farm_operations', lang)}", use_container_width=True):
            st.session_state.current_page = "Farm Operations"
            st.rerun()
    with c_btn3:
        if st.button(f"📊 {t('view_analytics', lang)}", use_container_width=True):
            st.session_state.current_page = "Analytics"
            st.rerun()

    st.markdown("<div style='margin-bottom: 1.75rem;'></div>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # 2. Live Weather Widget & Field Advisories (Open-Meteo Integration)
    # ------------------------------------------------------------------
    location_query = (farm.get("location") or farm.get("location_name", "Pollachi")) if farm and farm_id else "Pollachi"

    weather = api_client.get_weather(location_query)

    st.subheader(f"🌤 {t('weather_widget_title', lang)} — {location_query}")
    
    w_col1, w_col2, w_col3, w_col4 = st.columns(4)
    with w_col1:
        temp_val = f"{weather.get('temperature', 28.5)}°C"
        render_organic_metric_card(t("temp", lang), temp_val, icon="🌡️", color="#1b4332")
    with w_col2:
        hum_val = f"{weather.get('humidity', 70)}%"
        render_organic_metric_card(t("humidity", lang), hum_val, icon="💧", color="#2a9d8f")
    with w_col3:
        rain_val = f"{weather.get('rain_probability', 20)}%"
        render_organic_metric_card(t("rain_prob", lang), rain_val, icon="🌧️", color="#457b9d")
    with w_col4:
        cond_val = weather.get("condition", "Partly Cloudy")
        render_organic_metric_card("Condition", cond_val, icon="☀️", color="#f77f00")

    # Safe Advisory Banner
    advisory_msg = weather.get("advisory", "Favorable weather conditions for routine plantation operations.")
    st.markdown(
        f"""
        <div style="background: #e8f5e9; border: 1px solid #74c69d; border-radius: 16px; padding: 1rem 1.25rem; margin: 1rem 0 2rem 0;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.5rem;">📢</span>
                <div>
                    <strong style="color: #1b4332; font-size: 0.95rem;">{t('field_advisory', lang)}:</strong>
                    <div style="color: #2d6a4f; font-size: 0.9rem; margin-top: 0.15rem;">{advisory_msg}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # 3. Individual Status Indicators (NO Composite Health Score!)
    # ------------------------------------------------------------------
    st.subheader(f"🚦 {t('status_indicators', lang)}")
    st.caption("Individual status indicators derived from stored farm management records.")

    # Calculate status from real DB data
    stats = api_client.get_statistics()
    diseased_scans = stats.get("diseased_scans", 0)

    # Watering status check
    irr_records = api_client.get_irrigation_history(farm_id) if farm_id else []
    if irr_records:
        watering_status = t("on_track", lang)
        watering_badge = "#2a9d8f"
    else:
        watering_status = t("untested", lang)
        watering_badge = "#f77f00"

    # Soil status check
    soil_records = api_client.get_soil_history(farm_id) if farm_id else []
    if soil_records:
        latest_ph = soil_records[-1].get("ph_level", 6.5)
        if 5.5 <= latest_ph <= 7.5:
            soil_status = f"{t('on_track', lang)} (pH {latest_ph})"
            soil_badge = "#2a9d8f"
        else:
            soil_status = f"{t('needs_attention', lang)} (pH {latest_ph})"
            soil_badge = "#d90429"
    else:
        soil_status = t("untested", lang)
        soil_badge = "#f77f00"

    # Nutrition status check
    nutrition_status = t("on_track", lang)
    nutrition_badge = "#2a9d8f"

    # Pest / Disease status check
    if diseased_scans > 0:
        pest_status = f"{t('needs_attention', lang)} ({diseased_scans} alert)"
        pest_badge = "#d90429"
    else:
        pest_status = f"{t('on_track', lang)} (Healthy)"
        pest_badge = "#2a9d8f"

    ind1, ind2, ind3, ind4 = st.columns(4)
    with ind1:
        st.markdown(
            f"""
            <div class="organic-card" style="padding: 1.1rem; border-top: 4px solid {watering_badge};">
                <div style="font-size: 0.8rem; color: #5c6f64; text-transform: uppercase; font-weight: 700;">💧 {t('watering_status', lang)}</div>
                <div style="font-size: 1.1rem; font-weight: 800; color: {watering_badge}; margin-top: 0.35rem;">{watering_status}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with ind2:
        st.markdown(
            f"""
            <div class="organic-card" style="padding: 1.1rem; border-top: 4px solid {soil_badge};">
                <div style="font-size: 0.8rem; color: #5c6f64; text-transform: uppercase; font-weight: 700;">🧪 {t('soil_status', lang)}</div>
                <div style="font-size: 1.1rem; font-weight: 800; color: {soil_badge}; margin-top: 0.35rem;">{soil_status}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with ind3:
        st.markdown(
            f"""
            <div class="organic-card" style="padding: 1.1rem; border-top: 4px solid {nutrition_badge};">
                <div style="font-size: 0.8rem; color: #5c6f64; text-transform: uppercase; font-weight: 700;">🌿 {t('nutrition_status', lang)}</div>
                <div style="font-size: 1.1rem; font-weight: 800; color: {nutrition_badge}; margin-top: 0.35rem;">{nutrition_status}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with ind4:
        st.markdown(
            f"""
            <div class="organic-card" style="padding: 1.1rem; border-top: 4px solid {pest_badge};">
                <div style="font-size: 0.8rem; color: #5c6f64; text-transform: uppercase; font-weight: 700;">⚠️ {t('pest_disease_status', lang)}</div>
                <div style="font-size: 1.1rem; font-weight: 800; color: {pest_badge}; margin-top: 0.35rem;">{pest_status}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # 4. Financial Investment Totals
    # ------------------------------------------------------------------
    if farm_id:
        exp_summary = api_client.get_expense_summary(farm_id)
        tot_invest = exp_summary.get("total_investment", 0.0)
        month_exp = exp_summary.get("this_month", 0.0)
        rec_count = exp_summary.get("total_records", 0)

        st.subheader(f"💰 {t('tab_expense_tracker', lang)} Summary")
        f1, f2, f3 = st.columns(3)
        with f1:
            render_organic_metric_card(t("metric_total_investment", lang), f"₹{tot_invest:,.2f}", icon="💳", color="#1b4332")
        with f2:
            render_organic_metric_card(t("metric_monthly_expense", lang), f"₹{month_exp:,.2f}", icon="📅", color="#2a9d8f")
        with f3:
            render_organic_metric_card(t("metric_recorded_expenses", lang), str(rec_count), icon="🧾", color="#f77f00")

        st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # 5. Today's Operations & Tasks Widget
    # ------------------------------------------------------------------
    if farm_id:
        calendar_tasks = api_client.get_farm_calendar(farm_id)
        pending_tasks = [tk for tk in calendar_tasks if tk.get("status") == "PENDING"]

        if pending_tasks:
            st.subheader(f"📋 {t('todays_tasks_title', lang)}")
            t_cols = st.columns(min(3, len(pending_tasks)))
            for idx, task in enumerate(pending_tasks[:3]):
                with t_cols[idx]:
                    st.markdown(
                        f"""
                        <div style="background: #ffffff; border-radius: 16px; padding: 1rem; border: 1px solid #e2ece6; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                            <div style="font-size: 0.75rem; font-weight: 700; color: #2a9d8f; text-transform: uppercase;">[{task.get('activity_type')}]</div>
                            <strong style="color: #1b4332; font-size: 0.95rem;">{task.get('title')}</strong>
                            <div style="font-size: 0.8rem; color: #5c6f64; margin-top: 0.25rem;">📅 Due: {task.get('scheduled_date')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if st.button(f"✅ Mark Done", key=f"dash_task_{task['id']}"):
                        api_client.update_activity_status(task['id'], "COMPLETED")
                        st.rerun()

            st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # 6. Recent AI Scan History
    # ------------------------------------------------------------------
    st.subheader(f"🕘 {t('recent_scans', lang)}")
    recent_history = api_client.get_history(limit=4)

    if not recent_history:
        st.markdown(
            f"""
            <div class="organic-card" style="text-align: center; padding: 2.5rem 1.5rem;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">🌴</div>
                <h3 style="color: #1b4332; margin: 0;">{t("no_scans_yet", lang)}</h3>
                <p style="color: #5c6f64; margin-top: 0.5rem;">{t("no_scans_sub", lang)}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        for item in recent_history:
            ts = item.get("timestamp", "").replace("T", " ")[:16]
            fname = item.get("filename", "")
            disease_raw = item.get("primary_disease", "Healthy")
            status_raw = item.get("status", "Healthy")
            
            disease = t(disease_raw, lang)
            status = t(status_raw, lang)
            conf = item.get("max_confidence", 0.0) * 100
            block_name = item.get("block_name")
            
            badge_class = "badge-healthy" if status_raw == "Healthy" else "badge-diseased"

            block_info_html = f"<span style='font-size:0.8rem; color:#2a9d8f;'> 📍 {block_name}</span>" if block_name else ""

            st.markdown(
                f"""
                <div class="organic-card" style="padding: 1.1rem 1.5rem; margin-bottom: 0.85rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
                        <div>
                            <strong style="color: #1b4332; font-size: 1.1rem;">{fname}</strong>{block_info_html}
                            <div style="font-size: 0.825rem; color: #5c6f64;">Scanned on {ts}</div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 1.25rem;">
                            <span style="font-size: 0.95rem; font-weight: 700; color: #1b4332;">{disease} ({conf:.1f}%)</span>
                            <span class="{badge_class}">{status}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

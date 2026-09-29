"""
Phase 2 — Irrigation, Soil Management, Fertilizer Calendar & Farm Calendar View.
"""

import streamlit as st
from datetime import datetime, timedelta
from frontend.utils.api_client import api_client
from frontend.translations import t
from backend.constants import AGRONOMIC_DISCLAIMER


def render_farm_operations_view():
    lang = st.session_state.get("language", "en")
    user_id = st.session_state.get("user_id", 1)

    farm = api_client.get_farm(user_id)
    farm_id = farm["id"] if farm else 1

    st.markdown(
        f"""
<div style="margin-bottom: 1.5rem;">
    <h1 style="color: #1b4332; font-family: 'Outfit', sans-serif; margin-bottom: 0.25rem;">
        🌱 {t('nav_farm_operations', lang, default='Irrigation, Soil & Farm Calendar')}
    </h1>
    <p style="color: #5c6f64; font-size: 0.95rem; margin: 0;">
        {t('operations_subtitle', lang, default='Configure irrigation cycles, log soil health tests, review fertilizer guidance, and manage farm schedules.')}
    </p>
</div>
        """,
        unsafe_allow_html=True
    )

    # Mandatory Agronomic Disclaimer
    st.markdown(
        f"""
<div style="background-color: #f0fdf4; border-left: 4px solid #2a9d8f; padding: 0.85rem 1.1rem; border-radius: 8px; margin-bottom: 1.5rem;">
    <p style="margin: 0; color: #166534; font-size: 0.85rem; font-weight: 500;">
        <strong>ℹ️ Disclaimer:</strong> {AGRONOMIC_DISCLAIMER}
    </p>
</div>
        """,
        unsafe_allow_html=True
    )

    if not farm:
        st.warning(t('warning_setup_farm_first', lang, default="Please setup your Farm Profile first to enable operations logging."))

    tab1, tab2, tab3, tab4 = st.tabs([
        f"💧 {t('tab_irrigation', lang, default='Irrigation Planner')}",
        f"🌱 {t('tab_soil', lang, default='Soil Management')}",
        f"🌿 {t('tab_fertilizer', lang, default='Fertilizer Calendar')}",
        f"🗓️ {t('tab_calendar', lang, default='Farm Calendar')}"
    ])

    with tab1:
        _render_irrigation_tab(farm_id, lang)

    with tab2:
        _render_soil_tab(farm_id, lang)

    with tab3:
        _render_fertilizer_tab(farm_id, lang)

    with tab4:
        _render_calendar_tab(farm_id, lang)


# ---------------------------------------------------------------------------
# Tab 1: Irrigation Planner
# ---------------------------------------------------------------------------
def _render_irrigation_tab(farm_id: int, lang: str):
    st.markdown(
        f"""
<div style="background: white; border-radius: 16px; padding: 1.25rem; border: 1px solid #e2ece6; margin-bottom: 1.25rem;">
    <h3 style="color: #1b4332; margin-top: 0;">💧 {t('irrigation_title', lang, default='Irrigation Planner & Water Management')}</h3>
    <p style="color: #5c6f64; font-size: 0.88rem; margin: 0;">
        {t('irrigation_desc', lang, default='Set custom irrigation frequency and record water delivery per farm block.')}
    </p>
</div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(f"📝 {t('log_irrigation_heading', lang, default='Log Irrigation Event')}")
        with st.form("irrigation_form"):
            date_val = st.date_input(t('label_date', lang, default="Date"), datetime.today())
            block_name = st.text_input(t('label_block_name', lang, default="Block / Field Name"), value="Block A")
            qty = st.text_input(
                t('label_qty_duration', lang, default="Duration / Quantity (Optional)"),
                placeholder="e.g. 2.5 hours or 1200 Liters",
                help="Farmer-entered quantity only — no AI estimation."
            )
            freq_days = st.number_input(
                t('label_freq_days', lang, default="Irrigation Frequency (Days)"),
                min_value=1, max_value=30, value=7,
                help="Farmer-configured reminder interval."
            )
            notes = st.text_area(t('label_notes', lang, default="Notes / Weather Conditions"), placeholder="e.g. Drip irrigation operated during early morning.")

            submitted = st.form_submit_button(f"💾 {t('btn_save_irrigation', lang, default='Log Irrigation Event')}", use_container_width=True)
            if submitted:
                payload = {
                    "farm_id": farm_id,
                    "date": str(date_val),
                    "block_name": block_name.strip() or "Block A",
                    "duration_or_quantity": qty.strip() if qty else None,
                    "notes": notes.strip() if notes else None,
                    "status": "COMPLETED",
                    "frequency_days": freq_days
                }
                res = api_client.create_irrigation_record(payload)
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.success(t('msg_irrigation_logged', lang, default="Irrigation record logged!"))
                    st.rerun()

    with col2:
        st.subheader(f"📋 {t('irrigation_history_heading', lang, default='Irrigation History & Upcoming')}")
        records = api_client.get_irrigation_history(farm_id)

        if not records:
            st.info(t('no_irrigation_records', lang, default="No irrigation events logged yet. Use the form to record your first watering cycle."))
        else:
            latest = records[0]
            try:
                last_date = datetime.strptime(latest["date"], "%Y-%m-%d")
                next_date = last_date + timedelta(days=latest.get("frequency_days", 7))
                next_str = next_date.strftime("%Y-%m-%d")
            except Exception:
                next_str = "Scheduled based on frequency"

            st.markdown(
                f"""
<div style="background: #f8f6f0; border-radius: 12px; padding: 1rem; border: 1px solid #e2ece6; margin-bottom: 1rem;">
    <div style="font-size: 0.85rem; color: #5c6f64; font-weight: 600;">📅 NEXT SCHEDULED IRRIGATION REMINDER:</div>
    <div style="font-size: 1.3rem; font-weight: 800; color: #1b4332; margin-top: 0.2rem;">{next_str}</div>
    <div style="font-size: 0.8rem; color: #2a9d8f; margin-top: 0.2rem;">Configured interval: Every {latest.get('frequency_days', 7)} days</div>
</div>
                """,
                unsafe_allow_html=True
            )

            for item in records[:10]:
                status_color = "#2a9d8f" if item.get("status") == "COMPLETED" else "#e76f51"
                st.markdown(
                    f"""
<div style="background: white; border-radius: 12px; padding: 0.85rem 1rem; border: 1px solid #e2ece6; margin-bottom: 0.6rem; display: flex; justify-content: space-between; align-items: center;">
    <div>
        <strong style="color: #1b4332;">{item.get('block_name')}</strong> — <span style="color: #5c6f64;">{item.get('date')}</span>
        <div style="font-size: 0.82rem; color: #5c6f64;">{item.get('duration_or_quantity') or 'Watering logged'} | {item.get('notes') or ''}</div>
    </div>
    <span style="background: {status_color}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 700;">
        {item.get('status')}
    </span>
</div>
                    """,
                    unsafe_allow_html=True
                )


# ---------------------------------------------------------------------------
# Tab 2: Soil Management
# ---------------------------------------------------------------------------
def _render_soil_tab(farm_id: int, lang: str):
    st.markdown(
        f"""
<div style="background: white; border-radius: 16px; padding: 1.25rem; border: 1px solid #e2ece6; margin-bottom: 1.25rem;">
    <h3 style="color: #1b4332; margin-top: 0;">🌱 {t('soil_title', lang, default='Soil Health Management & Agronomic Evaluation')}</h3>
    <p style="color: #5c6f64; font-size: 0.88rem; margin: 0;">
        {t('soil_desc', lang, default='Log soil test values to compare against standard defensible agronomic ranges.')}
    </p>
</div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(f"🧪 {t('log_soil_heading', lang, default='Log Soil Test Results')}")
        with st.form("soil_form"):
            date_val = st.date_input(t('label_date', lang, default="Test Date"), datetime.today())
            ph = st.number_input("Soil pH", min_value=3.0, max_value=11.0, value=6.5, step=0.1, help="Optimal range: 5.5 - 7.5")
            n = st.number_input("Nitrogen (N kg/ha)", min_value=0.0, max_value=1000.0, value=180.0, step=10.0)
            p = st.number_input("Phosphorus (P kg/ha)", min_value=0.0, max_value=500.0, value=18.0, step=1.0)
            k = st.number_input("Potassium (K kg/ha)", min_value=0.0, max_value=1000.0, value=220.0, step=10.0)
            oc = st.number_input("Organic Carbon (%)", min_value=0.0, max_value=10.0, value=0.75, step=0.05)
            notes = st.text_area(t('label_notes', lang, default="Soil Notes"), placeholder="e.g. Collected from top 0-30cm basin soil.")

            submitted = st.form_submit_button(f"💾 {t('btn_save_soil', lang, default='Save Soil Test')}", use_container_width=True)
            if submitted:
                payload = {
                    "farm_id": farm_id,
                    "date": str(date_val),
                    "ph": ph,
                    "nitrogen": n,
                    "phosphorus": p,
                    "potassium": k,
                    "organic_carbon": oc,
                    "notes": notes.strip() if notes else None
                }
                res = api_client.create_soil_test(payload)
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.success(t('msg_soil_saved', lang, default="Soil test logged successfully!"))
                    st.rerun()

    with col2:
        st.subheader(f"📊 {t('soil_eval_heading', lang, default='Static Agronomic Evaluation')}")
        soil_history = api_client.get_soil_history(farm_id)

        if soil_history:
            latest = soil_history[0]
            ph_val = latest.get("ph", 6.5)
            n_val = latest.get("nitrogen", 180.0)
            p_val = latest.get("phosphorus", 18.0)
            k_val = latest.get("potassium", 220.0)
            oc_val = latest.get("organic_carbon", 0.75)
            st.caption(f"Showing evaluation for latest test recorded on {latest.get('date')}")
        else:
            ph_val, n_val, p_val, k_val, oc_val = 6.5, 180.0, 18.0, 220.0, 0.75
            st.caption("Showing evaluation for standard benchmark values (No test logged yet)")

        interps = api_client.get_soil_interpretations(ph_val, n_val, p_val, k_val, oc_val)

        for key, info in interps.items():
            st.markdown(
                f"""
<div style="background: white; border-radius: 12px; padding: 0.85rem 1rem; border: 1px solid #e2ece6; margin-bottom: 0.6rem;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <strong style="color: #1b4332;">{info['label']}: {info['value']} {info['unit']}</strong>
        <span style="background: {info['status_color']}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: 700;">
            {info['evaluation']}
        </span>
    </div>
    <div style="font-size: 0.8rem; color: #5c6f64; margin-top: 0.3rem;">
        Optimal Range: <strong>{info['optimal_range']} {info['unit']}</strong> | <em>Reference: {info['reference']}</em>
    </div>
</div>
                """,
                unsafe_allow_html=True
            )


# ---------------------------------------------------------------------------
# Tab 3: Fertilizer Calendar
# ---------------------------------------------------------------------------
def _render_fertilizer_tab(farm_id: int, lang: str):
    st.markdown(
        f"""
<div style="background: white; border-radius: 16px; padding: 1.25rem; border: 1px solid #e2ece6; margin-bottom: 1.25rem;">
    <h3 style="color: #1b4332; margin-top: 0;">🌿 {t('fertilizer_title', lang, default='Fertilizer & Nutrient Activity Guidance')}</h3>
    <p style="color: #5c6f64; font-size: 0.88rem; margin: 0;">
        {t('fertilizer_desc', lang, default='Pre-written recommended agronomic activity schedule based on palm tree age brackets.')}
    </p>
</div>
        """,
        unsafe_allow_html=True
    )

    templates = api_client.get_fertilizer_templates()
    age_brackets = list(templates.keys()) if templates else ["0-3 years", "3-6 years", "6+ years"]

    selected_age = st.selectbox(
        f"🌴 {t('select_age_bracket', lang, default='Select Tree Age Bracket')}",
        options=age_brackets,
        index=2
    )

    activities = templates.get(selected_age, [])

    st.markdown(f"#### Recommended Agronomic Schedule for **{selected_age}** Palms:")

    for idx, act in enumerate(activities):
        st.markdown(
            f"""
<div style="background: white; border-radius: 14px; padding: 1.1rem; border: 1px solid #e2ece6; margin-bottom: 0.85rem; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h4 style="color: #1b4332; margin: 0; font-size: 1.05rem;">{act['name']}</h4>
        <span style="background: #e8f5e9; color: #2e7d32; font-weight: 700; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem;">
            📅 {act['recommended_period']}
        </span>
    </div>
    <p style="color: #5c6f64; margin: 0.4rem 0 0.2rem 0; font-size: 0.88rem;"><strong>Agronomic Reason:</strong> {act['reason']}</p>
    <p style="color: #2a9d8f; margin: 0; font-size: 0.84rem;">📌 <strong>Application Method:</strong> {act['notes']}</p>
</div>
            """,
            unsafe_allow_html=True
        )

        btn_col1, btn_col2 = st.columns([1, 3])
        with btn_col1:
            if st.button(f"➕ Add to Calendar", key=f"add_fert_{idx}_{selected_age}"):
                payload = {
                    "farm_id": farm_id,
                    "activity_type": "fertilizer",
                    "title": act['name'],
                    "age_bracket": selected_age,
                    "scheduled_date": datetime.today().strftime("%Y-%m-%d"),
                    "status": "PENDING",
                    "notes": f"Period: {act['recommended_period']} | {act['notes']}"
                }
                res = api_client.create_farm_activity(payload)
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.success("Added to Farm Calendar!")


# ---------------------------------------------------------------------------
# Tab 4: Farm Calendar
# ---------------------------------------------------------------------------
def _render_calendar_tab(farm_id: int, lang: str):
    st.markdown(
        f"""
<div style="background: white; border-radius: 16px; padding: 1.25rem; border: 1px solid #e2ece6; margin-bottom: 1.25rem;">
    <h3 style="color: #1b4332; margin-top: 0;">🗓️ {t('calendar_title', lang, default='Integrated Plantation Task Calendar')}</h3>
    <p style="color: #5c6f64; font-size: 0.88rem; margin: 0;">
        {t('calendar_desc', lang, default='Unified operational schedule combining fertilizer applications, irrigation tasks, soil audits, and weed management.')}
    </p>
</div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader(f"➕ {t('add_task_heading', lang, default='Add Custom Task')}")
        with st.form("custom_task_form"):
            title = st.text_input(t('label_task_title', lang, default="Task Title"), placeholder="e.g. Basin weed removal & mulching")
            act_type = st.selectbox(
                t('label_task_type', lang, default="Task Type"),
                options=["fertilizer", "irrigation", "soil", "pest", "weed", "general"]
            )
            scheduled_date = st.date_input(t('label_scheduled_date', lang, default="Scheduled Date"), datetime.today())
            notes = st.text_area(t('label_notes', lang, default="Notes"), placeholder="e.g. Inspect block B trees after rain.")

            submitted = st.form_submit_button(f"💾 {t('btn_add_task', lang, default='Save Scheduled Task')}", use_container_width=True)
            if submitted:
                if not title.strip():
                    st.error("Please provide a task title.")
                else:
                    payload = {
                        "farm_id": farm_id,
                        "activity_type": act_type,
                        "title": title.strip(),
                        "scheduled_date": str(scheduled_date),
                        "status": "PENDING",
                        "notes": notes.strip() if notes else None
                    }
                    res = api_client.create_farm_activity(payload)
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.success(t('msg_task_saved', lang, default="Task added to calendar!"))
                        st.rerun()

    with col2:
        st.subheader(f"📋 {t('scheduled_tasks_heading', lang, default='Scheduled Operations')}")
        activities = api_client.get_farm_calendar(farm_id)

        filter_status = st.radio("Filter Tasks", options=["All", "PENDING", "COMPLETED"], horizontal=True)

        filtered = [
            a for a in activities
            if filter_status == "All" or a.get("status") == filter_status
        ]

        if not filtered:
            st.info(t('no_tasks_found', lang, default="No activities scheduled yet. Add tasks using the form or from the Fertilizer Calendar."))
        else:
            for act in filtered:
                is_done = act.get("status") == "COMPLETED"
                status_color = "#2a9d8f" if is_done else "#e76f51"
                btn_label = "↩ Mark Pending" if is_done else "✅ Mark Complete"

                st.markdown(
                    f"""
<div style="background: white; border-radius: 12px; padding: 0.9rem 1.1rem; border: 1px solid #e2ece6; margin-bottom: 0.65rem;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #5c6f64;">
                [{act.get('activity_type').upper()}]
            </span>
            <strong style="color: #1b4332; font-size: 1rem; margin-left: 6px;">{act.get('title')}</strong>
        </div>
        <span style="background: {status_color}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: 700;">
            {act.get('status')}
        </span>
    </div>
    <div style="font-size: 0.83rem; color: #5c6f64; margin-top: 0.35rem;">
        📅 Scheduled: <strong>{act.get('scheduled_date')}</strong> {f'| Completed: {act.get("completed_at")}' if is_done else ''}
    </div>
    {f'<div style="font-size: 0.8rem; color: #2a9d8f; margin-top: 0.2rem;">{act.get("notes")}</div>' if act.get("notes") else ''}
</div>
                    """,
                    unsafe_allow_html=True
                )

                t_col1, t_col2 = st.columns([1, 3])
                with t_col1:
                    if st.button(btn_label, key=f"toggle_act_{act['id']}"):
                        new_status = "PENDING" if is_done else "COMPLETED"
                        api_client.update_activity_status(act['id'], new_status)
                        st.rerun()

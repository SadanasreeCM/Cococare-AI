"""
Phase 3 — Finance & Growth View (Expense Tracker & Block Growth Timeline).
"""

import streamlit as st
from datetime import datetime
from frontend.utils.api_client import api_client
from frontend.translations import t
from frontend.components.charts import render_expense_breakdown_chart
from backend.constants import AGRONOMIC_DISCLAIMER, EXPENSE_CATEGORIES, PALM_VARIETIES


def render_finance_growth_view():
    lang = st.session_state.get("language", "en")
    user_id = st.session_state.get("user_id", 1)

    farm = api_client.get_farm(user_id)
    farm_id = farm["id"] if farm else 1

    st.markdown(
        f"""
<div style="margin-bottom: 1.5rem;">
    <h1 style="color: #1b4332; font-family: 'Outfit', sans-serif; margin-bottom: 0.25rem;">
        💰 {t('nav_finance_growth', lang, default='Plantation Finance & Growth Tracker')}
    </h1>
    <p style="color: #5c6f64; font-size: 0.95rem; margin: 0;">
        {t('finance_growth_subtitle', lang, default='Manage farm investments, expense breakdowns, block-wise growth timelines, and crop yields.')}
    </p>
</div>
        """,
        unsafe_allow_html=True
    )

    # Mandatory Disclaimer Banner
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
        st.warning(t('warning_setup_farm_first', lang, default="Please setup your Farm Profile first to enable finance and growth tracking."))

    tab1, tab2, tab3 = st.tabs([
        f"💰 {t('tab_expense_tracker', lang, default='Expense Tracker')}",
        f"🌴 {t('tab_growth_tracker', lang, default='Growth & Block Tracker')}",
        f"✅ {t('tab_todays_tasks', lang, default='Today Tasks & Operations')}"
    ])

    with tab1:
        _render_expense_tab(farm_id, lang)

    with tab2:
        _render_growth_tab(farm_id, lang)

    with tab3:
        _render_todays_tasks_tab(farm_id, lang)


# ---------------------------------------------------------------------------
# Tab 1: Expense Tracker
# ---------------------------------------------------------------------------
def _render_expense_tab(farm_id: int, lang: str):
    st.markdown(
        f"""
<div style="background: white; border-radius: 16px; padding: 1.25rem; border: 1px solid #e2ece6; margin-bottom: 1.25rem;">
    <h3 style="color: #1b4332; margin-top: 0;">💰 {t('expense_tracker_title', lang, default='Farm Expense Tracker & Budgeting')}</h3>
    <p style="color: #5c6f64; font-size: 0.88rem; margin: 0;">
        {t('expense_tracker_desc', lang, default='Record capital and operational expenditures to track cost per acre.')}
    </p>
</div>
        """,
        unsafe_allow_html=True
    )

    summary = api_client.get_expense_summary(farm_id)
    total_inv = summary.get("total_investment", 0.0)
    monthly_exp = summary.get("monthly_expense", 0.0)
    breakdown = summary.get("category_breakdown", {})

    # Display KPI Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(
            label=f"💵 {t('metric_total_investment', lang, default='Total Farm Investment')}",
            value=f"₹{total_inv:,.2f}"
        )
    with m2:
        st.metric(
            label=f"📅 {t('metric_monthly_expense', lang, default='This Month Expenses')}",
            value=f"₹{monthly_exp:,.2f}"
        )
    with m3:
        st.metric(
            label=f"📊 {t('metric_recorded_expenses', lang, default='Recorded Expenses Count')}",
            value=f"{summary.get('expense_count', 0)}"
        )

    st.markdown("<hr style='margin: 1.25rem 0; border: none; border-top: 1px dashed #e2ece6;'>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(f"📝 {t('log_expense_heading', lang, default='Log New Expense')}")
        with st.form("expense_form"):
            amount = st.number_input(
                f"{t('label_expense_amount', lang, default='Amount (₹)')} *",
                min_value=1.0, max_value=10000000.0, value=1500.0, step=500.0
            )
            category = st.selectbox(
                f"{t('label_expense_category', lang, default='Category')} *",
                options=EXPENSE_CATEGORIES
            )
            date_val = st.date_input(t('label_date', lang, default="Expense Date"), datetime.today())
            notes = st.text_area(t('label_notes', lang, default="Notes / Invoice Details"), placeholder="e.g. Organic neem cake fertilizer purchase.")

            submitted = st.form_submit_button(f"💾 {t('btn_save_expense', lang, default='Save Expense')}", use_container_width=True)
            if submitted:
                payload = {
                    "farm_id": farm_id,
                    "category": category,
                    "amount": float(amount),
                    "date": str(date_val),
                    "notes": notes.strip() if notes else None
                }
                res = api_client.create_expense(payload)
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.success(t('msg_expense_saved', lang, default="Expense record saved!"))
                    st.rerun()

    with col2:
        st.subheader(f"📊 {t('expense_chart_heading', lang, default='Category Breakdown')}")
        render_expense_breakdown_chart(breakdown)

    st.markdown("<hr style='margin: 1.5rem 0; border: none; border-top: 1px dashed #e2ece6;'>", unsafe_allow_html=True)

    st.subheader(f"📋 {t('expense_history_heading', lang, default='Expense Audit Log')}")
    expenses = api_client.get_expenses(farm_id)

    if not expenses:
        st.info(t('no_expenses_recorded', lang, default="No expenses logged yet. Use the form above to add your first expense."))
    else:
        for exp in expenses:
            exp_id = exp["id"]
            st.markdown(
                f"""
<div style="background: white; border-radius: 12px; padding: 0.85rem 1rem; border: 1px solid #e2ece6; margin-bottom: 0.6rem; display: flex; justify-content: space-between; align-items: center;">
    <div>
        <strong style="color: #1b4332;">{exp.get('category')}</strong> — <span style="color: #2a9d8f; font-weight: 700;">₹{exp.get('amount'):,.2f}</span>
        <div style="font-size: 0.82rem; color: #5c6f64;">📅 {exp.get('date')} {f'| {exp.get("notes")}' if exp.get("notes") else ''}</div>
    </div>
</div>
                """,
                unsafe_allow_html=True
            )
            del_col1, del_col2 = st.columns([1, 5])
            with del_col1:
                if st.button(f"🗑️ Delete", key=f"del_exp_{exp_id}"):
                    api_client.delete_expense(exp_id)
                    st.rerun()


# ---------------------------------------------------------------------------
# Tab 2: Growth & Block Tracker
# ---------------------------------------------------------------------------
def _render_growth_tab(farm_id: int, lang: str):
    st.markdown(
        f"""
<div style="background: white; border-radius: 16px; padding: 1.25rem; border: 1px solid #e2ece6; margin-bottom: 1.25rem;">
    <h3 style="color: #1b4332; margin-top: 0;">🌴 {t('growth_tracker_title', lang, default='Plantation Blocks & Tree Growth Timeline')}</h3>
    <p style="color: #5c6f64; font-size: 0.88rem; margin: 0;">
        {t('growth_tracker_desc', lang, default='Divide your plantation into blocks, monitor tree height progression, and record nut yield observations.')}
    </p>
</div>
        """,
        unsafe_allow_html=True
    )

    blocks = api_client.get_farm_blocks(farm_id)

    with st.expander(f"➕ {t('create_block_expander', lang, default='Add New Plantation Block')}"):
        with st.form("create_block_form"):
            b_name = st.text_input(t('label_block_name', lang, default="Block Name"), placeholder="e.g. North Plot - Hybrid Block")
            b_trees = st.number_input(t('label_tree_count', lang, default="Tree Count"), min_value=1, max_value=10000, value=50)
            b_variety = st.selectbox(t('label_variety', lang, default="Palm Variety"), options=PALM_VARIETIES)
            b_date = st.date_input(t('label_planting_date', lang, default="Planting Date"), datetime.today())
            b_status = st.selectbox(t('label_status', lang, default="Block Status"), options=["Active", "Nursery", "Re-planting", "Under Observation"])
            b_notes = st.text_area(t('label_notes', lang, default="Notes"), placeholder="e.g. Drip irrigated, loamy soil.")

            b_submit = st.form_submit_button(f"💾 {t('btn_save_block', lang, default='Create Block')}", use_container_width=True)
            if b_submit:
                if not b_name.strip():
                    st.error("Please provide a Block Name.")
                else:
                    payload = {
                        "farm_id": farm_id,
                        "block_name": b_name.strip(),
                        "tree_count": b_trees,
                        "variety": b_variety,
                        "planting_date": str(b_date),
                        "status": b_status,
                        "notes": b_notes.strip() if b_notes else None
                    }
                    res = api_client.create_farm_block(payload)
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.success("Plantation block created!")
                        st.rerun()

    if not blocks:
        st.info(t('no_blocks_created', lang, default="No plantation blocks created yet. Click 'Add New Plantation Block' above to initialize your field plots."))
        return

    block_options = {b["id"]: f"🌴 {b['block_name']} ({b['tree_count']} trees — {b.get('variety')})" for b in blocks}
    selected_block_id = st.selectbox(
        f"🔍 {t('select_block_label', lang, default='Select Plantation Block to Monitor')}",
        options=list(block_options.keys()),
        format_func=lambda bid: block_options[bid]
    )

    selected_block = next((b for b in blocks if b["id"] == selected_block_id), blocks[0])

    # Display Block Card
    st.markdown(
        f"""
<div style="background: white; border-radius: 14px; padding: 1.1rem; border: 1px solid #e2ece6; margin: 1rem 0;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h3 style="color: #1b4332; margin: 0;">🌴 {selected_block.get('block_name')}</h3>
        <span style="background: #e8f5e9; color: #2e7d32; font-weight: 700; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem;">
            ● {selected_block.get('status')}
        </span>
    </div>
    <div style="display: flex; gap: 2rem; margin-top: 0.6rem; color: #5c6f64; font-size: 0.9rem;">
        <div>🌴 Trees: <strong>{selected_block.get('tree_count')}</strong></div>
        <div>🧬 Variety: <strong>{selected_block.get('variety')}</strong></div>
        <div>📅 Planted: <strong>{selected_block.get('planting_date') or 'N/A'}</strong></div>
    </div>
    {f'<div style="font-size: 0.83rem; color: #5c6f64; margin-top: 0.4rem;">{selected_block.get("notes")}</div>' if selected_block.get("notes") else ''}
</div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(f"📝 {t('log_growth_heading', lang, default='Log Growth & Yield Observation')}")
        with st.form("growth_form"):
            g_date = st.date_input(t('label_date', lang, default="Observation Date"), datetime.today())
            g_height = st.number_input(t('label_height', lang, default="Avg Tree Height (meters)"), min_value=0.0, max_value=30.0, value=3.5, step=0.5)
            g_yield = st.number_input(t('label_yield', lang, default="Avg Yield (Nuts per tree)"), min_value=0.0, max_value=300.0, value=15.0, step=1.0)
            g_notes = st.text_area(t('label_notes', lang, default="Field Observations"), placeholder="e.g. Canopy greening healthy, early flowering spathe opening.")

            g_submit = st.form_submit_button(f"💾 {t('btn_save_growth', lang, default='Log Observation')}", use_container_width=True)
            if g_submit:
                if not g_notes.strip():
                    st.error("Please provide observation notes.")
                else:
                    payload = {
                        "block_id": selected_block_id,
                        "date": str(g_date),
                        "observation_notes": g_notes.strip(),
                        "tree_height_m": g_height,
                        "yield_nuts_per_tree": g_yield
                    }
                    res = api_client.create_growth_record(payload)
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.success("Growth observation recorded!")
                        st.rerun()

    with col2:
        st.subheader(f"📈 {t('growth_timeline_heading', lang, default='Block Growth Timeline')}")
        timeline = api_client.get_growth_timeline(selected_block_id)

        if not timeline:
            st.info("No growth observations recorded for this block yet.")
        else:
            for rec in timeline:
                st.markdown(
                    f"""
<div style="background: white; border-radius: 12px; padding: 0.9rem 1rem; border: 1px solid #e2ece6; margin-bottom: 0.65rem;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <strong style="color: #1b4332;">📅 {rec.get('date')}</strong>
        <span style="color: #2a9d8f; font-weight: 600; font-size: 0.85rem;">
            📏 {rec.get('tree_height_m') or 0}m height | 🥥 {rec.get('yield_nuts_per_tree') or 0} nuts/tree
        </span>
    </div>
    <div style="font-size: 0.85rem; color: #5c6f64; margin-top: 0.35rem;">
        {rec.get('observation_notes')}
    </div>
</div>
                    """,
                    unsafe_allow_html=True
                )


# ---------------------------------------------------------------------------
# Tab 3: Today's Tasks Dashboard Widget
# ---------------------------------------------------------------------------
def _render_todays_tasks_tab(farm_id: int, lang: str):
    st.markdown(
        f"""
<div style="background: white; border-radius: 16px; padding: 1.25rem; border: 1px solid #e2ece6; margin-bottom: 1.25rem;">
    <h3 style="color: #1b4332; margin-top: 0;">✅ {t('todays_tasks_title', lang, default='Today Operations & Task Manager')}</h3>
    <p style="color: #5c6f64; font-size: 0.88rem; margin: 0;">
        {t('todays_tasks_desc', lang, default='View and complete plantation tasks scheduled for today across irrigation, fertilizer, and soil care.')}
    </p>
</div>
        """,
        unsafe_allow_html=True
    )

    activities = api_client.get_farm_calendar(farm_id)
    today_str = datetime.utcnow().strftime("%Y-%m-%d")

    today_tasks = [a for a in activities if a.get("scheduled_date") == today_str or a.get("status") == "PENDING"]

    if not today_tasks:
        st.success(t('all_tasks_completed_msg', lang, default="🎉 All tasks up to date! No pending operations for today."))
    else:
        st.markdown(f"#### Operations Requiring Attention ({len(today_tasks)} items):")
        for act in today_tasks:
            is_done = act.get("status") == "COMPLETED"
            status_color = "#2a9d8f" if is_done else "#e76f51"

            st.markdown(
                f"""
<div style="background: white; border-radius: 12px; padding: 0.95rem 1.1rem; border: 1px solid #e2ece6; margin-bottom: 0.65rem;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #5c6f64;">
                [{act.get('activity_type').upper()}]
            </span>
            <strong style="color: #1b4332; font-size: 1.02rem; margin-left: 6px;">{act.get('title')}</strong>
        </div>
        <span style="background: {status_color}; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: 700;">
            {act.get('status')}
        </span>
    </div>
    <div style="font-size: 0.83rem; color: #5c6f64; margin-top: 0.35rem;">
        📅 Scheduled: <strong>{act.get('scheduled_date')}</strong> {f'| Notes: {act.get("notes")}' if act.get("notes") else ''}
    </div>
</div>
                """,
                unsafe_allow_html=True
            )
            col_b1, col_b2 = st.columns([1, 3])
            with col_b1:
                if st.button(f"{'↩ Mark Pending' if is_done else '✅ Mark Completed'}", key=f"today_act_{act['id']}"):
                    new_status = "PENDING" if is_done else "COMPLETED"
                    api_client.update_activity_status(act['id'], new_status)
                    st.rerun()

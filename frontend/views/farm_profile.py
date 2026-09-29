"""
Farm Setup, Farm Profile & Coconut Farm Planner View.
"""

import streamlit as st
import math
from frontend.utils.api_client import api_client
from frontend.translations import t
from backend.constants import (
    SOIL_TYPES,
    WATER_SOURCES,
    IRRIGATION_METHODS,
    AGRONOMIC_DISCLAIMER,
    DEFAULT_TREE_SPACING_METERS,
    SQ_METERS_PER_ACRE,
    SQ_METERS_PER_HECTARE
)


def render_farm_profile_view():
    lang = st.session_state.get("language", "en")
    user_id = st.session_state.get("user_id", 1) # Default demo user_id if not logged in

    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="color: #1b4332; font-family: 'Outfit', sans-serif; margin-bottom: 0.25rem;">
                🌴 {t('nav_farm_management', lang, default='Farm Profile & Planner')}
            </h1>
            <p style="color: #5c6f64; font-size: 0.95rem; margin: 0;">
                {t('farm_management_subtitle', lang, default='Manage your plantation details and calculate optimal planting density.')}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Disclaimer Banner
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

    farm = api_client.get_farm(user_id)

    tab1, tab2 = st.tabs([
        f"📋 {t('tab_farm_profile', lang, default='Farm Profile')}",
        f"📐 {t('tab_farm_planner', lang, default='Coconut Farm Planner')}"
    ])

    with tab1:
        _render_farm_profile_tab(farm, user_id, lang)

    with tab2:
        _render_farm_planner_tab(farm, lang)


def _render_farm_profile_tab(farm: dict, user_id: int, lang: str):
    is_editing = st.session_state.get("editing_farm", False) or (farm is None)

    if farm is None and not is_editing:
        st.info(t('no_farm_setup_msg', lang, default="No farm profile found. Please set up your farm details below."))
        is_editing = True

    if is_editing:
        st.markdown(
            f"""
            <div style="background: white; border-radius: 16px; padding: 1.5rem; border: 1px solid #e2ece6; margin-bottom: 1.5rem;">
                <h3 style="color: #1b4332; margin-top: 0;">🛠️ {t('farm_setup_wizard_title', lang, default='Farm Setup Wizard')}</h3>
                <p style="color: #5c6f64; font-size: 0.88rem;">
                    {t('farm_setup_wizard_desc', lang, default='Enter your farm metrics below to personalize recommendations.')}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("farm_setup_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input(
                    f"{t('label_farm_name', lang, default='Farm Name')} *",
                    value=farm.get("name", "") if farm else ""
                )
                location = st.text_input(
                    f"{t('label_location', lang, default='Location / Region')} *",
                    value=farm.get("location", "") if farm else ""
                )
                land_area = st.number_input(
                    f"{t('label_land_area', lang, default='Total Land Area')} *",
                    min_value=0.1, max_value=10000.0,
                    value=float(farm.get("land_area", 1.0)) if farm else 2.5,
                    step=0.5
                )
                land_unit = st.selectbox(
                    f"{t('label_land_unit', lang, default='Land Unit')}",
                    options=["acres", "hectares"],
                    index=0 if (not farm or farm.get("land_unit") == "acres") else 1
                )
                soil_type = st.selectbox(
                    f"{t('label_soil_type', lang, default='Soil Type (Fixed Reference)')} *",
                    options=SOIL_TYPES,
                    index=SOIL_TYPES.index(farm.get("soil_type", "loamy")) if (farm and farm.get("soil_type") in SOIL_TYPES) else 1,
                    help="Select your predominant soil type from standard classification."
                )

            with col2:
                water_source = st.selectbox(
                    f"{t('label_water_source', lang, default='Water Source')}",
                    options=WATER_SOURCES,
                    index=WATER_SOURCES.index(farm.get("water_source", "Borewell")) if (farm and farm.get("water_source") in WATER_SOURCES) else 1
                )
                irrigation_method = st.selectbox(
                    f"{t('label_irrigation_method', lang, default='Irrigation Method')}",
                    options=IRRIGATION_METHODS,
                    index=IRRIGATION_METHODS.index(farm.get("irrigation_method", "Drip")) if (farm and farm.get("irrigation_method") in IRRIGATION_METHODS) else 0
                )
                existing_trees = st.number_input(
                    f"{t('label_existing_trees', lang, default='Number of Existing Trees')}",
                    min_value=0, max_value=50000,
                    value=int(farm.get("existing_trees", 0)) if farm else 150,
                    step=5
                )
                planting_date = st.text_input(
                    f"{t('label_planting_date', lang, default='Planting Date / Year (Optional)')}",
                    value=farm.get("planting_date", "") if farm else ""
                )
                soil_test_info = st.text_area(
                    f"{t('label_soil_test_info', lang, default='Soil Test Notes (Optional)')}",
                    value=farm.get("soil_test_info", "") if farm else ""
                )

            submit_col, cancel_col = st.columns([1, 1])
            with submit_col:
                submitted = st.form_submit_button(f"💾 {t('btn_save_farm', lang, default='Save Farm Profile')}", use_container_width=True)
            with cancel_col:
                if farm:
                    cancel = st.form_submit_button(f"❌ {t('btn_cancel', lang, default='Cancel')}", use_container_width=True)
                    if cancel:
                        st.session_state["editing_farm"] = False
                        st.rerun()

            if submitted:
                if not name.strip() or not location.strip():
                    st.error("Please fill in both Farm Name and Location.")
                else:
                    payload = {
                        "user_id": user_id,
                        "name": name.strip(),
                        "location": location.strip(),
                        "land_area": land_area,
                        "land_unit": land_unit,
                        "soil_type": soil_type,
                        "water_source": water_source,
                        "irrigation_method": irrigation_method,
                        "existing_trees": existing_trees,
                        "planting_date": planting_date.strip() if planting_date else None,
                        "soil_test_info": soil_test_info.strip() if soil_test_info else None,
                    }
                    if farm:
                        res = api_client.update_farm(farm["id"], payload)
                    else:
                        res = api_client.create_farm(payload)

                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.success(t('msg_farm_saved', lang, default="Farm profile saved successfully!"))
                        st.session_state["editing_farm"] = False
                        st.rerun()
    else:
        # Render Profile View Cards matching design system
        col_btn1, col_btn2 = st.columns([4, 1])
        with col_btn2:
            if st.button(f"✏️ {t('btn_edit_profile', lang, default='Edit Profile')}", use_container_width=True):
                st.session_state["editing_farm"] = True
                st.rerun()

        card_col1, card_col2, card_col3 = st.columns(3)

        with card_col1:
            st.markdown(
                f"""
<div style="background: white; border-radius: 16px; padding: 1.4rem; border: 1px solid #e2ece6; box-shadow: 0 4px 12px rgba(0,0,0,0.03); min-height: 180px;">
    <div style="color: #2a9d8f; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
        🏡 {t('card_farm_identity', lang, default='Farm Identity')}
    </div>
    <h2 style="color: #1b4332; margin: 0 0 0.4rem 0; font-size: 1.4rem;">{farm.get('name')}</h2>
    <p style="color: #5c6f64; margin: 0; font-size: 0.95rem;">📍 <strong>{t('label_location', lang, default='Location')}:</strong> {farm.get('location')}</p>
    <p style="color: #5c6f64; margin: 0.4rem 0 0 0; font-size: 0.95rem;">📅 <strong>{t('label_established', lang, default='Established')}:</strong> {farm.get('planting_date') or 'N/A'}</p>
</div>
                """,
                unsafe_allow_html=True
            )

        with card_col2:
            st.markdown(
                f"""
<div style="background: white; border-radius: 16px; padding: 1.4rem; border: 1px solid #e2ece6; box-shadow: 0 4px 12px rgba(0,0,0,0.03); min-height: 180px;">
    <div style="color: #2a9d8f; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
        📐 {t('card_land_soil', lang, default='Land & Soil Profile')}
    </div>
    <p style="color: #1b4332; margin: 0; font-size: 1.2rem; font-weight: 700;">{farm.get('land_area')} {farm.get('land_unit')}</p>
    <p style="color: #5c6f64; margin: 0.4rem 0 0 0; font-size: 0.95rem;">🌱 <strong>{t('label_soil_type', lang, default='Soil Type')}:</strong> <span style="text-transform: capitalize;">{farm.get('soil_type')}</span></p>
    <p style="color: #5c6f64; margin: 0.3rem 0 0 0; font-size: 0.85rem; opacity: 0.8;">{farm.get('soil_test_info') or 'No soil test notes added.'}</p>
</div>
                """,
                unsafe_allow_html=True
            )

        with card_col3:
            st.markdown(
                f"""
<div style="background: white; border-radius: 16px; padding: 1.4rem; border: 1px solid #e2ece6; box-shadow: 0 4px 12px rgba(0,0,0,0.03); min-height: 180px;">
    <div style="color: #2a9d8f; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
        💧 {t('card_water_trees', lang, default='Irrigation & Crop Density')}
    </div>
    <p style="color: #1b4332; margin: 0; font-size: 1.2rem; font-weight: 700;">🌴 {farm.get('existing_trees')} {t('label_trees', lang, default='Trees')}</p>
    <p style="color: #5c6f64; margin: 0.4rem 0 0 0; font-size: 0.95rem;">💧 <strong>{t('label_water_source', lang, default='Water Source')}:</strong> {farm.get('water_source')}</p>
    <p style="color: #5c6f64; margin: 0.3rem 0 0 0; font-size: 0.95rem;">🌧️ <strong>{t('label_irrigation_method', lang, default='Irrigation')}:</strong> {farm.get('irrigation_method')}</p>
</div>
                """,
                unsafe_allow_html=True
            )


def _render_farm_planner_tab(farm: dict, lang: str):
    st.markdown(
        f"""
        <div style="background: white; border-radius: 16px; padding: 1.5rem; border: 1px solid #e2ece6; margin-bottom: 1.5rem;">
            <h3 style="color: #1b4332; margin-top: 0;">📐 {t('planner_title', lang, default='Coconut Plantation Density Calculator')}</h3>
            <p style="color: #5c6f64; font-size: 0.88rem;">
                {t('planner_desc', lang, default='Calculate required seedling counts based on land dimensions and standard tree spacing formula.')}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_in1, col_in2, col_in3 = st.columns(3)

    default_area = float(farm.get("land_area", 2.5)) if farm else 2.5
    default_unit = farm.get("land_unit", "acres") if farm else "acres"
    default_trees = int(farm.get("existing_trees", 0)) if farm else 0

    with col_in1:
        land_area = st.number_input(
            f"{t('planner_land_area', lang, default='Land Area')}",
            min_value=0.1, max_value=10000.0, value=default_area, step=0.5
        )
        land_unit = st.selectbox(
            f"{t('planner_unit', lang, default='Unit')}",
            options=["acres", "hectares"],
            index=0 if default_unit == "acres" else 1
        )

    with col_in2:
        spacing = st.number_input(
            f"{t('planner_spacing', lang, default='Tree Spacing (meters x meters)')}",
            min_value=5.0, max_value=12.0, value=DEFAULT_TREE_SPACING_METERS, step=0.5,
            help="Typical industry-standard spacing is 7.5m x 7.5m (adjustable)."
        )
        st.caption(f"ℹ️ {t('planner_spacing_note', lang, default='Typical spacing: 7.5m × 7.5m (adjustable)')}")

    with col_in3:
        existing_trees = st.number_input(
            f"{t('planner_existing_trees', lang, default='Existing Tree Count')}",
            min_value=0, max_value=50000, value=default_trees, step=10
        )

    # ------------------------------------------------------------------
    # Mathematical Formula Calculation (Pure Math — Zero AI Hallucination)
    # ------------------------------------------------------------------
    sqm_per_unit = SQ_METERS_PER_ACRE if land_unit == "acres" else SQ_METERS_PER_HECTARE
    total_area_sqm = land_area * sqm_per_unit
    area_per_tree_sqm = spacing * spacing
    calculated_capacity = int(total_area_sqm // area_per_tree_sqm)
    needed_seedlings = max(0, calculated_capacity - existing_trees)

    # Grid dimension estimation (rows & columns)
    side_length_m = math.sqrt(total_area_sqm)
    rows = max(1, int(side_length_m // spacing))
    cols = max(1, int(calculated_capacity // rows))

    st.markdown("<hr style='margin: 1.5rem 0; border: none; border-top: 1px dashed #e2ece6;'>", unsafe_allow_html=True)

    # Display Metrics Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label=f"📐 {t('metric_total_area', lang, default='Total Area (m²)')}",
            value=f"{total_area_sqm:,.0f} m²"
        )
    with m2:
        st.metric(
            label=f"🌴 {t('metric_calculated_capacity', lang, default='Estimated Capacity')}",
            value=f"{calculated_capacity:,}",
            help=f"Formula: Total Area ({total_area_sqm:,.0f} m²) ÷ Spacing Area ({area_per_tree_sqm:.2f} m²)"
        )
    with m3:
        st.metric(
            label=f"🌱 {t('metric_existing_trees', lang, default='Existing Trees')}",
            value=f"{existing_trees:,}"
        )
    with m4:
        st.metric(
            label=f"🛒 {t('metric_needed_seedlings', lang, default='Required Seedlings')}",
            value=f"{needed_seedlings:,}",
            delta=f"-{existing_trees:,}" if existing_trees > 0 else None,
            help="Formula: Estimated Capacity - Existing Trees"
        )

    # Transparency Formula Box
    st.markdown(
        f"""
        <div style="background: #f8f6f0; border-radius: 12px; padding: 1rem 1.25rem; border: 1px solid #e2ece6; margin: 1.25rem 0;">
            <span style="font-weight: 700; color: #1b4332; font-size: 0.9rem;">🔢 Transparent Calculation Formula:</span>
            <code style="background: white; padding: 4px 8px; border-radius: 4px; color: #2a9d8f; font-weight: 600;">
                Calculated Trees = Total Land Area ({total_area_sqm:,.1f} m²) ÷ Tree Area ({spacing}m × {spacing}m = {area_per_tree_sqm:.2f} m²) = {calculated_capacity} trees
            </code>
            <p style="margin: 0.4rem 0 0 0; color: #5c6f64; font-size: 0.8rem;">
                * Note: All values are math-based estimates. Actual planting density may vary depending on field boundaries and access roads.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Visual Planting Grid (CSS grid proportional representation)
    st.markdown(
        f"#### 🗺️ {t('visual_grid_title', lang, default='Simulated Plantation Layout Grid')}"
    )

    max_icons = min(100, calculated_capacity) # Display max 100 icons for clean responsiveness
    grid_cols = min(10, cols)

    grid_items = ""
    for i in range(max_icons):
        is_existing = i < min(existing_trees, max_icons)
        bg_color = "#2a9d8f" if is_existing else "#e2ece6"
        icon = "🌴" if is_existing else "🌱"
        tooltip = f"Existing Tree #{i+1}" if is_existing else f"Planned Seedling Slot #{i+1}"
        grid_items += f"""
        <div title="{tooltip}" style="background-color: {bg_color}; border-radius: 8px; display: flex; align-items: center; justify-content: center; height: 38px; font-size: 1.2rem; transition: transform 0.2s;">
            {icon}
        </div>
        """

    st.markdown(
        f"""
        <div style="background: white; border-radius: 16px; padding: 1.25rem; border: 1px solid #e2ece6;">
            <div style="display: flex; gap: 1.5rem; margin-bottom: 0.8rem; font-size: 0.85rem; color: #5c6f64;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="display: inline-block; width: 14px; height: 14px; background: #2a9d8f; border-radius: 3px;"></span>
                    Existing Tree (🌴)
                </div>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="display: inline-block; width: 14px; height: 14px; background: #e2ece6; border-radius: 3px;"></span>
                    Planned Seedling (🌱)
                </div>
                <div style="margin-left: auto; font-weight: 600;">
                    Showing layout matrix (approx {rows} rows × {cols} columns)
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat({grid_cols}, 1fr); gap: 8px; background: #f8f6f0; padding: 12px; border-radius: 12px;">
                {grid_items}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

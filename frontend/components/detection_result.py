import streamlit as st
from typing import Dict, Any
from frontend.translations import t
from frontend.utils.api_client import api_client


def render_detection_result(result: Dict[str, Any]):
    """Renders comprehensive organic AI detection result report in active session language."""
    if not result:
        st.error("No detection data available.")
        return

    lang = st.session_state.get("language", "en")

    status_raw = result.get("status", "Healthy")
    primary_disease_raw = result.get("primary_disease", "Healthy")
    
    status = t(status_raw, lang)
    primary_disease = t(primary_disease_raw, lang)

    total_dets = result.get("total_detections", 0)
    max_conf = result.get("max_confidence", 0.0) * 100
    detections = result.get("detections", [])
    disease_details = result.get("disease_details", {})
    warning = result.get("warning")

    # Status Alert Banner
    if status_raw == "Healthy":
        st.markdown(
            f"""
            <div style="background: #d8f3dc; border-left: 6px solid #2d6a4f; border-radius: 20px; padding: 1.5rem; margin-bottom: 1.75rem;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="font-size: 2.2rem;">🌿</span>
                    <div>
                        <h3 style="margin: 0; color: #1b4332; font-size: 1.4rem;">{t("tree_healthy", lang)}</h3>
                        <p style="margin: 0.35rem 0 0 0; color: #2d6a4f; font-size: 0.95rem;">
                            {t("tree_healthy_sub", lang)}
                        </p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        title_txt = t("disease_detected_title", lang, disease=primary_disease)
        sub_txt = t("disease_detected_sub", lang, count=total_dets, conf=max_conf)
        st.markdown(
            f"""
            <div style="background: #ffe5ec; border-left: 6px solid #d90429; border-radius: 20px; padding: 1.5rem; margin-bottom: 1.75rem;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="font-size: 2.2rem;">⚠️</span>
                    <div>
                        <h3 style="margin: 0; color: #9d0208; font-size: 1.4rem;">{title_txt}</h3>
                        <p style="margin: 0.35rem 0 0 0; color: #b7094c; font-size: 0.95rem;">
                            {sub_txt}
                        </p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if warning:
        st.warning(f"ℹ Note: {warning}")

    # Layout Columns
    col_img, col_info = st.columns([1.1, 1], gap="large")

    with col_img:
        st.subheader(f"🖼 {t('ai_annotated_img', lang)}")
        annotated_url = result.get("annotated_image_url")
        original_url = result.get("original_image_url")
        
        if annotated_url:
            st.image(annotated_url, caption=f"Annotated ({total_dets} detections)", use_container_width=True)
        elif original_url:
            st.image(original_url, caption="Original Uploaded Image", use_container_width=True)

    with col_info:
        st.subheader(f"🔍 {t('prediction_breakdown', lang)}")
        
        if not detections:
            st.info("No disease bounding boxes detected above current threshold.")
        else:
            for idx, det in enumerate(detections, 1):
                raw_c_name = det.get("class_name", "Unknown")
                c_name = t(raw_c_name.title(), lang)
                conf = det.get("confidence", 0.0) * 100
                sev = det.get("severity", "Medium")
                
                badge_class = "badge-diseased" if sev == "High" else "badge-warning" if sev == "Medium" else "badge-healthy"
                
                st.markdown(
                    f"""
                    <div class="organic-card" style="padding: 1.1rem; margin-bottom: 0.85rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-weight: 800; font-size: 1.05rem; color: #1b4332;">#{idx}. {c_name}</span>
                            <span class="{badge_class}">{t('confidence', lang)}: {conf:.1f}%</span>
                        </div>
                        <div style="font-size: 0.9rem; color: #5c6f64;">
                            <div>{t('confidence', lang)}: <strong style="color: #1b4332;">{conf:.1f}%</strong> ({t('high_certainty', lang) if conf >= 70 else 'Standard'})</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # Action to scan another leaf
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    if st.button(f"🔄 {t('scan_another_leaf', lang)}", use_container_width=True):
        if "last_detection_result" in st.session_state:
            del st.session_state["last_detection_result"]
        st.session_state.current_page = "Disease Detection"
        st.rerun()

    # Detailed Botanical Information & Fungicide Guide
    st.markdown("---")
    st.subheader(f"📖 {t('disease_info_actions', lang)}")

    for cls_name, info in disease_details.items():
        disp_name = info.get("display_name", t(cls_name.title(), lang))
        sci_name = info.get("scientific_name", "")
        sev_level = info.get("severity", "Medium")
        sev_color = info.get("severity_color", "#2a9d8f")
        description = info.get("description", "")
        treatment = info.get("treatment", "")

        with st.expander(f"🌴 {disp_name} ({sci_name})", expanded=True):
            st.markdown(
                f"""
                <div style="background: #ffffff; border-left: 5px solid {sev_color}; border-radius: 16px; padding: 1.1rem; margin-bottom: 1rem;">
                    <h4 style="margin: 0 0 0.35rem 0; color: #1b4332;">{disp_name}</h4>
                    <p style="margin: 0; font-size: 0.95rem; color: #1f2923;">{description}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_symptom, col_action = st.columns(2, gap="medium")
            
            with col_symptom:
                st.markdown(f"#### 🚨 {t('prediction_breakdown', lang)}")
                for s in info.get("symptoms", []):
                    st.markdown(f"- {s}")

            with col_action:
                st.markdown(f"#### 🛠 {t('recommended_treatment', lang)}")
                st.markdown(f"1. {treatment}")
                for a in info.get("recommended_action", []):
                    if a != treatment:
                        st.markdown(f"- {a}")

    # Phase 4: Link Scan to Farm Block & Notes
    det_id = result.get("detection_id") or result.get("id")
    if det_id:
        st.markdown("---")
        st.subheader(f"📌 {t('link_scan_to_block', lang)}")
        
        user = st.session_state.get("user", {})
        user_id = user.get("id", 1) if isinstance(user, dict) else 1
        farm = api_client.get_farm(user_id)
        
        blocks = []
        if farm and isinstance(farm, dict) and farm.get("id"):
            farm_id = farm.get("id")
            blocks = api_client.get_farm_blocks(farm_id)
        
        block_options = {"None": None}
        for b in blocks:
            b_name = b.get("block_name", f"Block #{b.get('id')}")
            block_options[b_name] = b.get("id")
            
        col_blk, col_note = st.columns([1, 1.5])
        with col_blk:
            selected_block_label = st.selectbox(
                t("select_block_optional", lang),
                options=list(block_options.keys()),
                key=f"det_block_select_{det_id}"
            )
            selected_block_id = block_options[selected_block_label]
        
        with col_note:
            notes_input = st.text_input(
                t("farmer_notes_ph", lang),
                key=f"det_notes_input_{det_id}"
            )
            
        if st.button(f"💾 {t('btn_save_link', lang)}", key=f"det_save_btn_{det_id}"):
            res = api_client.link_detection_to_block(det_id, selected_block_id, notes_input)
            if res.get("id") or res.get("success") or res.get("status_code") == 200:
                st.success(f"✓ {t('msg_link_saved', lang)}")
            else:
                st.error("Failed to link scan record.")


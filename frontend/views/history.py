import streamlit as st
from frontend.components.navbar import render_header
from frontend.components.detection_result import render_detection_result
from frontend.utils.api_client import api_client
from frontend.translations import t

def render_history_view():
    """Renders the Organic Detection History page."""
    lang = st.session_state.get("language", "en")

    render_header(
        f"🕘 {t('scan_history', lang)}",
        t("history_subtitle", lang)
    )

    # Filter Controls
    c_search, c_filter, c_clear = st.columns([2, 1.5, 1])

    with c_search:
        search_query = st.text_input(
            f"🔍 {t('nav_history', lang)}",
            placeholder=t("search_logs_ph", lang)
        )
    with c_filter:
        filter_options = [
            t("filter_all", lang),
            t("filter_healthy", lang),
            t("filter_disease", lang)
        ]
        selected_filter_label = st.selectbox(
            t("filter_by_category", lang),
            options=filter_options
        )
        
        # Map label back to English backend status filter
        if selected_filter_label == t("filter_healthy", lang):
            status_filter = "Healthy"
        elif selected_filter_label == t("filter_disease", lang):
            status_filter = "Diseased"
        else:
            status_filter = None

    with c_clear:
        st.markdown("<div style='margin-top: 1.8rem;'></div>", unsafe_allow_html=True)
        if st.button(f"🗑 {t('clear_all', lang)}", use_container_width=True):
            res = api_client.clear_all_history()
            if res.get("success"):
                st.success("Cleared all detection history.")
                st.rerun()
            else:
                st.error(f"Error: {res.get('message')}")

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Fetch History Records
    history_records = api_client.get_history(
        limit=100,
        search=search_query,
        status_filter=status_filter
    )

    if not history_records:
        st.markdown(
            f"""
            <div class="organic-card" style="text-align: center; padding: 3rem 1.5rem;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">🌴</div>
                <h3 style="color: #1b4332; margin: 0;">{t("no_scans_yet", lang)}</h3>
                <p style="color: #5c6f64; margin-top: 0.5rem;">{t("no_scans_sub", lang)}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    st.markdown(f"Displaying **{len(history_records)}** scan record(s):")

    for item in history_records:
        det_id = item.get("id")
        ts = item.get("timestamp", "").replace("T", " ")[:16]
        fname = item.get("filename", "")
        disease_raw = item.get("primary_disease", "Healthy")
        status_raw = item.get("status", "Healthy")
        
        disease = t(disease_raw, lang)
        status = t(status_raw, lang)
        conf = item.get("max_confidence", 0.0) * 100
        annotated_url = item.get("annotated_image_url")
        
        badge_class = "badge-healthy" if status_raw == "Healthy" else "badge-diseased"

        with st.expander(f"📅 {ts} — {fname} ({disease} - {conf:.1f}%)", expanded=False):
            col_info, col_img, col_act = st.columns([1.5, 1, 0.8])
            
            with col_info:
                st.markdown(f"• **Scan ID:** `{det_id}`")
                st.markdown(f"• **{t('filename', lang)}** `{fname}`")
                st.markdown(f"• **Timestamp:** {ts}")
                st.markdown(f"• **Diagnosis:** <span class='{badge_class}'>{disease}</span>", unsafe_allow_html=True)
                st.markdown(f"• **{t('confidence', lang)}:** `{conf:.1f}%`")
                st.markdown(f"• **Detections:** `{item.get('total_detections', 0)}`")
                
                block_name = item.get("block_name")
                notes = item.get("farmer_notes")
                if block_name:
                    st.markdown(f"• **Farm Block:** 📍 **{block_name}**")
                if notes:
                    st.markdown(f"• **Notes:** *{notes}*")


            with col_img:
                if annotated_url:
                    st.image(annotated_url, caption="Annotated Bounding Boxes", width=180)

            with col_act:
                if st.button(f"🔎 {t('inspect_record', lang)}", key=f"view_{det_id}", use_container_width=True):
                    detail = api_client.get_history_detail(det_id)
                    if detail:
                        st.session_state["selected_history_detail"] = detail
                        st.rerun()

                if st.button(f"🗑 {t('delete', lang)}", key=f"del_{det_id}", use_container_width=True):
                    del_res = api_client.delete_history_item(det_id)
                    if del_res.get("success"):
                        st.success(f"Deleted record #{det_id}")
                        st.rerun()
                    else:
                        st.error("Failed to delete record.")

    # Inspection detail section
    if "selected_history_detail" in st.session_state:
        st.markdown("<hr style='margin: 2.5rem 0; border: none; border-top: 1px dashed #e2ece6;'>", unsafe_allow_html=True)
        st.subheader(f"📋 Inspection View — Scan #{st.session_state['selected_history_detail']['id']}")
        if st.button("✖ Close Inspection View"):
            del st.session_state["selected_history_detail"]
            st.rerun()
        
        render_detection_result(st.session_state["selected_history_detail"])

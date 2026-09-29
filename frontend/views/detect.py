import time
import streamlit as st
from frontend.components.navbar import render_header
from frontend.components.detection_result import render_detection_result
from frontend.utils.api_client import api_client
from frontend.translations import t

def render_detect_view():
    """Renders the Organic Biophilic AI Disease Detection page."""
    lang = st.session_state.get("language", "en")

    render_header(
        f"🌿 {t('nav_detect', lang)} — {t('scan_a_leaf', lang)}",
        t("upload_leaf_photo", lang)
    )

    # Configuration Control Bar
    col_conf, col_info = st.columns([1, 1.2], gap="large")

    with col_conf:
        confidence_pct = st.slider(
            t("target_confidence", lang),
            min_value=10,
            max_value=95,
            value=50,
            step=5,
            help="Filters predictions below this confidence level."
        )
        confidence_val = confidence_pct / 100.0

    with col_info:
        st.markdown(
            f"""
            <div style="background: #fdfcf7; border: 1px solid #e2ece6; border-radius: 20px; padding: 1rem 1.25rem; font-size: 0.875rem; color: #5c6f64;">
                <strong style="color: #1b4332;">💡 {t("tips_header", lang)}</strong><br>
                {t("tips_body", lang)}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Organic File Uploader Card
    uploaded_file = st.file_uploader(
        f"🌴 {t('upload_leaf_photo', lang)} ({t('drag_drop_click', lang)})",
        type=["jpg", "jpeg", "png", "webp"],
        help="Upload image payload for AI object detection."
    )

    # Option to camera capture if camera input is available
    camera_photo = st.camera_input(f"📷 {t('take_photo', lang)}")
    active_file = uploaded_file or camera_photo

    if active_file is not None:
        file_bytes = active_file.getvalue()
        file_name = active_file.name if hasattr(active_file, "name") and active_file.name else "camera_capture.jpg"
        
        c_prev, c_act = st.columns([1.1, 1], gap="large")
        
        with c_prev:
            st.markdown(f"#### {t('uploaded_preview', lang)}")
            st.markdown(
                """
                <div class="organic-image-frame">
                """,
                unsafe_allow_html=True
            )
            st.image(file_bytes, caption=f"File: {file_name}", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c_act:
            st.markdown(f"### 🌴 {t('payload_details', lang)}")
            st.markdown(f"• **{t('filename', lang)}** `{file_name}`")
            st.markdown(f"• **{t('payload_size', lang)}** `{len(file_bytes)/1024:.1f} KB`")
            st.markdown(f"• **{t('target_confidence', lang)}** `{confidence_pct}%`")
            
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

            if st.button(f"🌿 {t('analyze_btn', lang)}", use_container_width=True):
                status_placeholder = st.empty()
                
                with status_placeholder.container():
                    st.markdown(
                        f"""
                        <div class="organic-card" style="border-color: #74c69d; padding: 1.5rem;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌴</div>
                            <h4 style="color: #1b4332; margin-top: 0;">{t('analyzing', lang)}</h4>
                            <div style="font-size: 0.95rem; color: #2d6a4f; margin-bottom: 0.4rem;">✓ Uploading image payload</div>
                            <div style="font-size: 0.95rem; color: #2d6a4f; margin-bottom: 0.4rem;">⚙ Running Roboflow object detection model...</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # Call API with active language
                result = api_client.detect_disease(
                    file_bytes=file_bytes,
                    filename=file_name,
                    confidence=confidence_val,
                    language=lang
                )

                status_placeholder.empty()

                if not result.get("success"):
                    st.error(f"⚠️ Analysis failed: {result.get('error', 'Unknown error')}")
                else:
                    st.success("✓ AI Diagnosis Complete!")
                    st.session_state["last_detection_result"] = result

    # Display results
    if "last_detection_result" in st.session_state:
        st.markdown("<hr style='margin: 2.5rem 0; border: none; border-top: 1px dashed #e2ece6;'>", unsafe_allow_html=True)
        render_detection_result(st.session_state["last_detection_result"])

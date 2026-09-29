"""
CoconutCare Chatbot Component — Multilingual chat UI powered by Groq Llama 3.3.

Renders a full chat interface with:
 - Language-aware greeting, placeholder, and button text
 - Conversation history maintained in session state
 - Messages sent to /api/chat with the active language code and optional scan context
"""

import streamlit as st
from frontend.utils.api_client import api_client
from frontend.translations import t


def render_chatbot_view():
    """Renders the multilingual CoconutCare AI chatbot interface."""
    lang = st.session_state.get("language", "en")

    # Page header
    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="margin: 0; font-size: 2.2rem; color: #1b4332; font-weight: 700;">
                🌴 {t("assistant_title", lang)}
            </h1>
            <p style="margin-top: 0.25rem; font-size: 1.05rem; color: #5c6f64;">
                {t("greeting", lang)}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Initialize chat history in session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Display conversation history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    if prompt := st.chat_input(
        t("placeholder", lang),
        key="chatbot_input",
    ):
        # Add user message to history and display it
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Build OpenAI / Groq compatible history for context
        chat_history = []
        for msg in st.session_state.chat_messages[:-1]:  # exclude current message
            role = "user" if msg["role"] == "user" else "assistant"
            chat_history.append({"role": role, "content": msg["content"]})

        # Extract recent scan context if available
        user_context = None
        if st.session_state.get("last_detection_result"):
            res = st.session_state["last_detection_result"]
            disease = res.get("disease_name", res.get("disease", "Unknown"))
            conf = res.get("confidence", 0)
            user_context = f"Detection result: {disease} (Confidence: {conf:.1%})"
        elif st.session_state.get("selected_history_detail"):
            res = st.session_state["selected_history_detail"]
            disease = res.get("disease_name", res.get("disease", "Unknown"))
            user_context = f"Inspection record: {disease}"

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner(t("thinking", lang)):
                response = api_client.send_chat_message(
                    message=prompt,
                    language=lang,
                    history=chat_history,
                    user_context=user_context,
                )

            if response.get("success"):
                reply_text = response["reply"]
                st.write(reply_text)
                st.session_state.chat_messages.append(
                    {"role": "assistant", "content": reply_text}
                )
            else:
                reason = response.get("reply", "Unknown error")
                print(f"Chat error: {reason}")
                error_msg = f"{t('chat_error', lang)} ({reason})"
                st.error(error_msg)
                st.session_state.chat_messages.append(
                    {"role": "assistant", "content": error_msg}
                )

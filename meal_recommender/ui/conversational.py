import streamlit as st

from llm.preference_extractor import (
    GeminiConfigurationError,
    GeminiTemporarilyUnavailableError,
    INITIAL_ASSISTANT_MESSAGE,
    collect_preferences,
    to_backend_preferences,
)
from recommender.recommender import get_recommendations


def render_retry_controls():
    st.warning(
        "Gemini is temporarily busy. Your message is saved, so you can try "
        "the same request again in a moment."
    )

    retry_column, discard_column = st.columns([1, 1])

    retry_requested = retry_column.button(
        "Try again",
        type="primary",
        key="retry_chat_message",
    )

    if discard_column.button(
        "Discard message",
        key="discard_chat_message",
    ):
        if (
            st.session_state.chat_messages
            and st.session_state.chat_messages[-1]["role"] == "user"
        ):
            st.session_state.chat_messages.pop()

        st.session_state.chat_retry_pending = False
        st.rerun()

    return retry_requested


def render_conversational_interface():
    st.subheader("Conversational interface")

    if not st.session_state.chat_messages:
        st.session_state.chat_messages.append(
            {"role": "assistant", "content": INITIAL_ASSISTANT_MESSAGE}
        )

    chat_history = st.container()

    with chat_history:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    retry_pending = st.session_state.chat_retry_pending

    if retry_pending:
        should_process_message = render_retry_controls()

        if not should_process_message:
            return
    else:
        user_message = st.chat_input("Tell me what you feel like eating.")

        if not user_message:
            return

        st.session_state.chat_messages.append(
            {"role": "user", "content": user_message}
        )

        with chat_history:
            with st.chat_message("user"):
                st.write(user_message)

    with chat_history:
        with st.spinner("Thinking..."):
            try:
                llm_result = collect_preferences(st.session_state.chat_messages)
            except GeminiTemporarilyUnavailableError:
                st.session_state.chat_retry_pending = True
                st.rerun()
            except GeminiConfigurationError:
                st.error(
                    "The Gemini API key is missing or was rejected. "
                    "Check GEMINI_API_KEY in the .env file, then restart the app."
                )
                return
            except Exception:
                st.error(
                    "The chat assistant could not process this message. "
                    "Please try again."
                )
                return

    st.session_state.chat_retry_pending = False

    assistant_message = llm_result["assistant_message"]

    st.session_state.chat_messages.append(
        {"role": "assistant", "content": assistant_message}
    )

    with chat_history:
        with st.chat_message("assistant"):
            st.write(assistant_message)

    if llm_result["ready_to_recommend"]:
        preferences = to_backend_preferences(llm_result["preferences"])

        st.session_state.last_preferences = preferences
        st.session_state.results = get_recommendations(preferences, top_n=18)
        st.session_state.selected_recipe = None
        st.rerun()

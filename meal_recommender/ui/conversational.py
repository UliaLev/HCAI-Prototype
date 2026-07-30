import streamlit as st

from llm.preference_extractor import collect_preferences, to_backend_preferences
from recommender.recommender import get_recommendations


def render_conversational_interface():
    st.subheader("Conversational interface")

    if not st.session_state.chat_messages:
        greeting = (
            "Hi! I can help collect your meal preferences. "
            "What kind of recipes are you in the mood for?"
        )
        st.session_state.chat_messages.append(
            {"role": "assistant", "content": greeting}
        )

    chat_history = st.container()

    with chat_history:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    user_message = st.chat_input("Tell me what you feel like eating.")

    if not user_message:
        return

    st.session_state.chat_messages.append(
        {"role": "user", "content": user_message}
    )

    with chat_history:
        with st.chat_message("user"):
            st.write(user_message)

        with st.spinner("Thinking..."):
            try:
                llm_result = collect_preferences(st.session_state.chat_messages)
            except Exception as error:
                st.error(
                    "The chat assistant could not process the message. "
                    "Check your Gemini API key and connection."
                )
                st.exception(error)
                return

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

import os

import streamlit as st

from ui.conversational import render_conversational_interface
from ui.recipe_views import render_recommendations
from ui.traditional import render_traditional_interface

from dotenv import load_dotenv

def apply_global_styles():
    st.markdown(
        """
        <style>
        :root {
            --app-bg: #F7FAF7;
            --surface: #FFFFFF;
            --text: #1F2A24;
            --muted: #5F6F66;
            --primary: #2F7D5C;
            --border: #DDE7DF;
        }

        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"] {
            background-color: var(--app-bg) !important;
            color: var(--text) !important;
        }

        [data-testid="stHeader"] {
            background: transparent !important;
        }

        h1, h2, h3, h4, h5, h6, p, span, label, div {
            color: var(--text);
        }

        .main .block-container,
        [data-testid="stMainBlockContainer"] {
            max-width: 1120px;
            padding-top: 2rem;
            padding-bottom: 3rem;
            margin-left: auto;
            margin-right: auto;
        }

        .recipe-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 1rem;
            align-items: stretch;
        }

        .recipe-card {
            min-height: 430px;
            height: 100%;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            background: var(--surface);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .recipe-card img {
            width: 100%;
            height: 180px;
            object-fit: cover;
            border-radius: 6px;
            margin-bottom: 0.75rem;
        }

        [class*="_recipe_card_"] [data-testid="stImage"] img {
            width: 100%;
            height: 250px;
            object-fit: cover;
            border-radius: 6px;
        }

        .recipe-card-title {
            font-size: 1.05rem;
            font-weight: 700;
            line-height: 1.35;
            min-height: 4.25rem;
            display: -webkit-box;
            -webkit-box-orient: vertical;
            -webkit-line-clamp: 3;
            overflow: hidden;
        }

        .recipe-card-meta {
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.4;
            min-height: 2.6rem;
            display: -webkit-box;
            -webkit-box-orient: vertical;
            -webkit-line-clamp: 2;
            overflow: hidden;
        }

        .recipe-card-explanation {
            height: 10.5rem;
            min-height: 10.5rem;
            padding: 0.85rem 1rem;
            border-radius: 8px;
            background: #E5F1FA;
            line-height: 1.5;
            overflow-y: auto;
            box-sizing: border-box;
        }

        .recipe-card-explanation summary {
            cursor: pointer;
            list-style: none;
        }

        .recipe-card-explanation summary::-webkit-details-marker {
            display: none;
        }

        .recipe-card-explanation-label {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.5rem;
            color: var(--text);
            font-weight: 700;
        }

        .recipe-card-explanation-label::after {
            content: "⌄";
            color: var(--primary);
            font-size: 1.2rem;
            line-height: 1;
        }

        .recipe-card-explanation[open] .recipe-card-explanation-label::after {
            content: "⌃";
        }

        .recipe-card-explanation-preview {
            margin-top: 0.45rem;
            color: var(--text);
            font-weight: 400;
            display: -webkit-box;
            -webkit-box-orient: vertical;
            -webkit-line-clamp: 4;
            overflow: hidden;
        }

        .recipe-card-explanation[open] .recipe-card-explanation-preview {
            display: none;
        }

        .recipe-card-explanation-full {
            margin-top: 0.65rem;
            color: var(--text);
        }

        .recipe-detail {
            max-width: 800px;
            margin: 0 auto;
        }

        .filter-panel {
            max-width: 980px;
            margin: 0 auto;
        }

        .center-image img {
            display: block;
            margin-left: auto;
            margin-right: auto;
            border-radius: 8px;
        }

        section[data-testid="stSidebar"],
        div[data-testid="stPopoverBody"],
        div[data-testid="stExpander"],
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: var(--surface) !important;
            color: var(--text) !important;
        }

        div[data-testid="stPopoverBody"] {
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            box-shadow: 0 16px 42px rgba(31, 42, 36, 0.14) !important;
            padding: 1rem !important;
            max-height: min(40vh, 320px) !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            width: min(620px, calc(100vw - 2rem)) !important;
        }

        div[data-testid="stPopoverBody"] > div {
            overflow: visible !important;
        }

        div[data-testid="stPopover"] button,
        div[data-testid="stPopover"] button:hover,
        div[data-testid="stPopover"] button:focus,
        div[data-testid="stPopover"] button:active {
            background-color: var(--surface) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }

        div[data-testid="stPopover"] button p,
        div[data-testid="stPopover"] button span {
            color: var(--text) !important;
        }

        button[data-testid="baseButton-secondary"],
        button[data-testid="baseButton-secondary"]:hover,
        button[data-testid="baseButton-secondary"]:focus,
        button[data-testid="baseButton-secondary"]:active {
            background-color: var(--surface) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            box-shadow: none !important;
        }

        button[data-testid="baseButton-secondary"] p,
        button[data-testid="baseButton-secondary"] span {
            color: var(--text) !important;
        }

        div[data-baseweb="popover"],
        div[data-baseweb="menu"],
        div[data-baseweb="select"] {
            z-index: 9999 !important;
        }

        div[data-baseweb="popover"] {
            max-width: calc(100vw - 2rem) !important;
        }

        div[data-baseweb="select"] > div,
        input,
        textarea {
            background-color: var(--surface) !important;
            color: var(--text) !important;
            border-color: var(--border) !important;
        }

        div[data-baseweb="tag"] {
            background-color: #E7F1EB !important;
            color: var(--text) !important;
        }

        div[data-testid="stCheckbox"] label {
            align-items: flex-start;
            gap: 0.45rem;
            padding: 0.1rem 0;
        }

        div[data-testid="stCheckbox"] p {
            line-height: 1.25;
        }

        div.stButton > button {
            background-color: var(--surface) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
        }

        div.stButton > button[kind="primary"],
        div.stButton > button[data-testid="baseButton-primary"] {
            background-color: var(--primary) !important;
            color: #FFFFFF !important;
            border-color: var(--primary) !important;
        }

        div.stButton > button:hover {
            border-color: var(--primary) !important;
            color: var(--primary) !important;
        }

        div.stButton > button[kind="primary"] p,
        div.stButton > button[kind="primary"] span,
        div.stButton > button[data-testid="baseButton-primary"] p,
        div.stButton > button[data-testid="baseButton-primary"] span {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }

        div[data-testid="stPopoverBody"] div.stButton > button {
            width: 30px !important;
            height: 30px !important;
            min-height: 30px !important;
            padding: 0 !important;
            border-radius: 999px !important;
            background: transparent !important;
            border-color: transparent !important;
            box-shadow: none !important;
        }

        div[data-testid="stPopoverBody"] div.stButton > button p {
            color: var(--primary) !important;
            font-size: 1.45rem !important;
            line-height: 1 !important;
            margin: 0 !important;
        }

        .filter-help {
            color: var(--muted);
            font-size: 0.9rem;
            margin-bottom: 0.75rem;
        }

        .checkbox-list-note {
            color: var(--muted);
            font-size: 0.85rem;
            margin-top: 0.25rem;
            margin-bottom: 0.75rem;
        }

        .importance-label {
            margin-top: 1.4rem;
            margin-bottom: 0.7rem;
            font-weight: 600;
            color: var(--text);
        }

        .rating-value {
            color: var(--muted);
            font-size: 0.85rem;
            margin-top: 0.25rem;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

load_dotenv()


def init_session_state():
    if "results" not in st.session_state:
        st.session_state.results = []

    if "selected_recipe" not in st.session_state:
        st.session_state.selected_recipe = None

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    if "last_preferences" not in st.session_state:
        st.session_state.last_preferences = None

    if "chosen_meals" not in st.session_state:
        st.session_state.chosen_meals = []




def main():
    st.set_page_config(
        page_title="Meal Recommender",
        page_icon="🍽️",
        layout="wide",
    )

    apply_global_styles()

    init_session_state()

    st.title("Meal Recommender")
    st.caption(
        "Compare a traditional filter interface with a conversational interface."
    )

    traditional_tab, conversational_tab = st.tabs(
        ["Traditional filters", "Chat assistant"]
    )

    with traditional_tab:
        render_traditional_interface()
        render_recommendations("traditional")

    with conversational_tab:
        render_conversational_interface()
        render_recommendations("conversational")


if __name__ == "__main__":
    main()

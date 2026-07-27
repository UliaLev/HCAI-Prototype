import streamlit as st

from recommender.recommender import get_recommendations
from ui.options import get_all_filter_options


def importance_dots(label, key, default=3):
    state_key = f"{key}_importance"

    if state_key not in st.session_state:
        st.session_state[state_key] = default

    st.markdown(
        f'<div class="importance-label">{label}</div>',
        unsafe_allow_html=True,
    )

    columns = st.columns(5, gap="small")

    for value, column in enumerate(columns, start=1):
        is_active = value <= st.session_state[state_key]
        button_label = chr(9679) if is_active else chr(9675)

        with column:
            if st.button(
                button_label,
                key=f"{state_key}_button_{value}",
                help=f"Set importance to {value} out of 5",
                use_container_width=True,
            ):
                st.session_state[state_key] = value
                st.rerun()

    return st.session_state[state_key]


def checkbox_filter_options(title, options, key, column_count=1):
    selected = []

    st.markdown(
        '<div class="filter-help">Select one or more options.</div>',
        unsafe_allow_html=True,
    )

    if column_count <= 1:
        for option in options:
            checkbox_key = f"{key}_{option}"

            if st.checkbox(option, key=checkbox_key):
                selected.append(option)
    else:
        checkbox_columns = st.columns(column_count)

        for index, option in enumerate(options):
            checkbox_key = f"{key}_{option}"

            with checkbox_columns[index % column_count]:
                if st.checkbox(option, key=checkbox_key):
                    selected.append(option)

    if selected:
        st.markdown(
            f'<div class="checkbox-list-note">{len(selected)} selected</div>',
            unsafe_allow_html=True,
        )

    return selected


def multi_filter_popover(title, options, key, importance_label=None, column_count=1):
    with st.popover(title, use_container_width=True):
        selected = checkbox_filter_options(title, options, key, column_count)

        importance = importance_dots(
            importance_label or f"How important is {title.lower()}?",
            key,
        )

    return {
        "val": selected,
        "importance": importance,
    }


def render_traditional_interface():
    st.subheader("Traditional filter interface")

    options = get_all_filter_options()

    st.write("Choose the filters that matter for this meal.")

    row1 = st.columns(3, gap="medium")
    row2 = st.columns(3, gap="medium")
    row3 = st.columns(3, gap="medium")

    with row1[0]:
        cuisine = multi_filter_popover(
            "Cuisine",
            options["cuisine"],
            "cuisine",
            "How important is cuisine?",
        )

    with row1[1]:
        include_ingredients = multi_filter_popover(
            "Ingredients to Include",
            options["ingredient"],
            "include_ingredients",
            "How important are included ingredients?",
            column_count=2,
        )

    with row1[2]:
        with st.popover("Ingredients to Exclude", use_container_width=True):
            exclude_ingredients = checkbox_filter_options(
                "Ingredients to Exclude",
                options["ingredient"],
                "exclude_ingredients",
                column_count=2,
            )
            st.markdown(
                '<div class="filter-help">Recipes containing these ingredients will be removed.</div>',
                unsafe_allow_html=True,
            )

    with row2[0]:
        meal = multi_filter_popover(
            "Meal Type",
            options["meal"],
            "meal",
            "How important is meal type?",
        )

    with row2[1]:
        recipe_type = multi_filter_popover(
            "Recipe Type",
            options["type"],
            "recipe_type",
            "How important is recipe type?",
        )

    with row2[2]:
        simple_cooking = multi_filter_popover(
            "Simple Cooking",
            options["simple_cooking"],
            "simple_cooking",
            "How important is cooking style?",
        )

    with row3[0]:
        special = multi_filter_popover(
            "Dietary Consideration",
            options["special"],
            "special",
            "How important is this dietary consideration?",
        )

    with row3[1]:
        with st.popover("Cooking Time", use_container_width=True):
            use_cooking_time = st.checkbox(
                "Use cooking time filter",
                key="use_cooking_time",
            )

            cooking_time = st.slider(
                "Maximum cooking time in minutes",
                min_value=10,
                max_value=120,
                value=30,
                step=5,
                disabled=not use_cooking_time,
            )

            cooking_time_importance = importance_dots(
                "How important is cooking time?",
                "cooking_time",
            )

    with row3[2]:
        st.empty()

    submitted = st.button(
        "Recommend meals",
        use_container_width=True,
        type="primary",
    )

    if submitted:
        preferences = {
            "cuisine": cuisine,
            "ingredient": include_ingredients,
            "exclude_ingredients": {
                "val": exclude_ingredients,
                "importance": None,
            },
            "meal": meal,
            "type": recipe_type,
            "simple_cooking": simple_cooking,
            "special": special,
            "cooking_time": {
                "val": cooking_time if use_cooking_time else None,
                "importance": cooking_time_importance if use_cooking_time else None,
            },
        }

        st.session_state.last_preferences = preferences
        st.session_state.results = get_recommendations(preferences, top_n=18)
        st.session_state.selected_recipe = None
        st.rerun()

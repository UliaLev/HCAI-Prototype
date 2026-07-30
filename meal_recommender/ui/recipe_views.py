from html import escape
from pathlib import Path

import streamlit as st


APP_DIR = Path(__file__).resolve().parents[1]


def safe_text(value, fallback="Not available"):
    if value in [None, "", [], {}]:
        return fallback

    if isinstance(value, list):
        return ", ".join(str(item) for item in value)

    return str(value)


def get_image_path(recipe):
    filename = recipe.get("image_filename")

    if not filename:
        return None

    filename = str(filename).strip()
    filename_path = Path(filename)
    filenames = [filename]

    if not filename_path.suffix:
        filenames.extend(
            [
                f"{filename}.jpg",
                f"{filename}.jpeg",
                f"{filename}.png",
                f"{filename}.webp",
            ]
        )

    candidates = [
        base / candidate
        for base in [
            APP_DIR / "data" / "images",
            APP_DIR.parent / "data" / "raw" / "images" / "images",
        ]
        for candidate in filenames
    ]

    for path in candidates:
        if path.exists():
            return path

    return None


def get_recipe_key(recipe):
    return safe_text(
        recipe.get("id") or recipe.get("recipe_id") or recipe.get("title"),
        "Untitled recipe",
    )


def is_chosen_meal(recipe):
    recipe_key = get_recipe_key(recipe)
    return any(
        get_recipe_key(chosen_recipe) == recipe_key
        for chosen_recipe in st.session_state.chosen_meals
    )


def add_chosen_meal(recipe):
    if not is_chosen_meal(recipe):
        st.session_state.chosen_meals.append(recipe)


def remove_chosen_meal(recipe):
    recipe_key = get_recipe_key(recipe)
    st.session_state.chosen_meals = [
        chosen_recipe
        for chosen_recipe in st.session_state.chosen_meals
        if get_recipe_key(chosen_recipe) != recipe_key
    ]


def render_chosen_meals(key_prefix):
    st.subheader("Meals chosen:")

    if not st.session_state.chosen_meals:
        st.caption("No meals chosen yet.")
        return

    for index, recipe in enumerate(st.session_state.chosen_meals):
        title = safe_text(recipe.get("title"), "Untitled recipe")
        cooking_time = safe_text(recipe.get("cooking_time"), "Time not listed")
        meal_columns = st.columns([5, 2, 1])

        with meal_columns[0]:
            st.write(f"**{title}**")

        with meal_columns[1]:
            st.caption(f"{cooking_time} minutes")

        with meal_columns[2]:
            if st.button(
                "Remove",
                key=f"{key_prefix}_remove_chosen_meal_{index}",
                width="stretch",
            ):
                remove_chosen_meal(recipe)
                st.rerun()

    if st.button(
        "Clear chosen meals",
        key=f"{key_prefix}_clear_chosen_meals",
    ):
        st.session_state.chosen_meals = []
        st.rerun()


def render_recipe_card(item, index, key_prefix):
    recipe = item["recipe"]
    tags = recipe.get("tags") or {}
    image_path = get_image_path(recipe)
    chosen = is_chosen_meal(recipe)
    title = safe_text(recipe.get("title"), "Untitled recipe")
    cuisine = safe_text(tags.get("cuisine_grouped"), "Cuisine not listed")
    cooking_time = safe_text(recipe.get("cooking_time"), "Time not listed")
    explanation = item.get("explanation") or {}
    explanation_text = safe_text(
        explanation.get("sentence"),
        "Recommended based on your selected preferences.",
    )

    with st.container(
        border=True,
        height=790,
        key=f"{key_prefix}_recipe_card_{index}",
    ):
        if image_path:
            st.image(str(image_path), width="stretch")

        st.markdown(
            (
                f'<div class="recipe-card-title" title="{escape(title)}">'
                f"{escape(title)}</div>"
            ),
            unsafe_allow_html=True,
        )

        meta = f"{cuisine} · {cooking_time} minutes"
        st.markdown(
            (
                f'<div class="recipe-card-meta" title="{escape(meta)}">'
                f"{escape(meta)}</div>"
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                '<details class="recipe-card-explanation">'
                "<summary>"
                '<span class="recipe-card-explanation-label">'
                "Why this recipe?"
                "</span>"
                '<span class="recipe-card-explanation-preview">'
                f"{escape(explanation_text)}"
                "</span>"
                "</summary>"
                '<div class="recipe-card-explanation-full">'
                f"{escape(explanation_text)}"
                "</div>"
                "</details>"
            ),
            unsafe_allow_html=True,
        )

        if st.button(
            "View recipe",
            key=f"{key_prefix}_view_recipe_{index}",
            width="stretch",
        ):
            st.session_state.selected_recipe = recipe
            st.rerun()

        if st.button(
            "Chosen" if chosen else "Add to chosen meals",
            key=f"{key_prefix}_choose_recipe_{index}",
            disabled=chosen,
            width="stretch",
        ):
            add_chosen_meal(recipe)
            st.rerun()

def render_recipe_detail(recipe, key_prefix):
    st.markdown('<div class="recipe-detail">', unsafe_allow_html=True)

    if st.button("Back to recommendations", key=f"{key_prefix}_back_to_results"):
        st.session_state.selected_recipe = None
        st.rerun()

    st.header(safe_text(recipe.get("title"), "Untitled recipe"))

    image_path = get_image_path(recipe)
    if image_path:
        st.markdown('<div class="center-image">', unsafe_allow_html=True)
        st.image(str(image_path), width=520)
        st.markdown("</div>", unsafe_allow_html=True)

    tags = recipe.get("tags") or {}

    col1, col2, col3 = st.columns(3)
    col1.metric("Cooking time", safe_text(recipe.get("cooking_time"), "N/A"))
    col2.metric("Meal", safe_text(recipe.get("primary_meal"), "N/A"))
    col3.metric("Cuisine", safe_text(tags.get("cuisine"), "N/A"))

    st.subheader("Description")
    st.write(safe_text(recipe.get("description"), "No description available."))

    st.subheader("Ingredients")
    render_bullets(recipe.get("ingredients"))

    st.subheader("Preparation")
    instructions = recipe.get("instructions") or recipe.get("instructions_flat")
    render_numbered_instructions(instructions)

    st.subheader("Detailed tags")

    cuisine = safe_text(tags.get("cuisine"), "Not available")
    ingredient_grouped = safe_text(tags.get("ingredient_grouped"), "Not available")
    recipe_type = safe_text(tags.get("type"), "Not available")
    type_grouped = safe_text(tags.get("type_grouped"), "Not available")
    simple = safe_text(tags.get("simple-cooking"), "Not available")
    special = safe_text(tags.get("special-consideration"), "Not available")

    st.write(f"**Detailed cuisine:** {cuisine}")
    st.write(f"**Ingredients:** {ingredient_grouped}")
    st.write(f"**Recipe type:** {recipe_type}, {type_grouped}")
    st.write(f"**Simple cooking:** {simple}")
    st.write(f"**Special considerations:** {special}")

    st.markdown("</div>", unsafe_allow_html=True)

def render_bullets(items):
    values = items if isinstance(items, list) else [items]

    for item in values:
        if item:
            st.markdown(f"- {item}")


def render_numbered_instructions(instructions):
    if isinstance(instructions, dict):
        ordered_items = sorted(
            instructions.items(),
            key=lambda item: int(item[0]) if str(item[0]).isdigit() else str(item[0]),
        )
        values = [text for _, text in ordered_items]
    elif isinstance(instructions, list):
        values = instructions
    elif isinstance(instructions, str):
        values = [instructions]
    else:
        values = []

    if not values:
        st.write("Instructions not available.")
        return

    for index, step in enumerate(values, start=1):
        st.markdown(f"{index}. {step}")

def render_recommendations(key_prefix):
    render_chosen_meals(key_prefix)

    if st.session_state.selected_recipe:
        render_recipe_detail(st.session_state.selected_recipe, key_prefix)
        return

    results = st.session_state.results

    if not results:
        st.info("Choose preferences and click Recommend meals.")
        return

    st.divider()
    st.header("Recommended recipes")

    for row_start in range(0, len(results), 3):
        columns = st.columns(3)
        row_items = results[row_start : row_start + 3]

        for offset, (column, item) in enumerate(zip(columns, row_items)):
            index = row_start + offset
            with column:
                render_recipe_card(item, index, key_prefix)

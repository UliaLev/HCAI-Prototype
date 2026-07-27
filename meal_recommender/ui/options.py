from pathlib import Path

import streamlit as st

from recommender.loader import load_recipes


APP_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = APP_DIR / "data" / "recipes_group_preprocessed.json"


@st.cache_data
def load_recipe_data():
    return load_recipes(DATA_PATH)


def get_tag_options(recipes, tag_name):
    values = set()

    for recipe in recipes:
        tags = recipe.get("tags") or {}
        tag_values = tags.get(tag_name) or []

        for value in tag_values:
            values.add(value)

    return sorted(values)


def get_primary_meal_options(recipes):
    values = {
        recipe.get("primary_meal")
        for recipe in recipes
        if recipe.get("primary_meal")
    }

    return sorted(values)


def get_all_filter_options():
    recipes = load_recipe_data()

    return {
        "cuisine": get_tag_options(recipes, "cuisine_grouped"),
        "ingredient": get_tag_options(recipes, "ingredient_grouped"),
        "meal": get_primary_meal_options(recipes),
        "type": get_tag_options(recipes, "type_grouped"),
        "simple_cooking": get_tag_options(recipes, "simple-cooking"),
        "special": get_tag_options(recipes, "special-consideration"),
    }
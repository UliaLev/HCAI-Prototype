import random
from pathlib import Path

from . import explain
from . import loader
from . import profile
from . import ranker
from . import scorer


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "recipes_group_preprocessed.json"


def get_discovery_result(recipe, primary_cuisine):
    return {
        "recipe": recipe,
        "score": 0,
        "matched_attributes": [],
        "explanation": {
            "list": "Discovery Mode",
            "sentence": (
                f"Recommended to introduce you to "
                f"{primary_cuisine} cuisine."
            ),
        },
    }


def get_diverse_discovery(recipes, count=10, recipes_per_cuisine=2):
    diverse_results = []
    recipes_by_cuisine = {}

    shuffled_recipes = recipes.copy()
    random.shuffle(shuffled_recipes)

    for recipe in shuffled_recipes:
        cuisines = recipe.get("tags", {}).get("cuisine_grouped", [])
        primary_cuisine = cuisines[0] if cuisines else "Other"
        recipes_by_cuisine.setdefault(primary_cuisine, []).append(recipe)

    cuisine_names = list(recipes_by_cuisine.keys())
    random.shuffle(cuisine_names)

    for cuisine_name in cuisine_names:
        for recipe in recipes_by_cuisine[cuisine_name][:recipes_per_cuisine]:
            diverse_results.append(get_discovery_result(recipe, cuisine_name))

            if len(diverse_results) >= count:
                return diverse_results

    selected_ids = {id(item["recipe"]) for item in diverse_results}

    for recipe in shuffled_recipes:
        if id(recipe) in selected_ids:
            continue

        cuisines = recipe.get("tags", {}).get("cuisine_grouped", [])
        primary_cuisine = cuisines[0] if cuisines else "Other"
        diverse_results.append(get_discovery_result(recipe, primary_cuisine))

        if len(diverse_results) >= count:
            break

    return diverse_results


def get_recommendations(user_preferences, filepath=DATA_PATH, top_n=18):
    recipes = loader.load_recipes(filepath)

    def is_empty_value(value):
        return value is None or value == "Any" or value == "" or value == []

    is_empty = all(
        is_empty_value(pref.get("val"))
        for key, pref in user_preferences.items()
        if key != "exclude_ingredients"
    )

    if is_empty:
        return get_diverse_discovery(recipes, count=top_n)

    user_profile = profile.create_profile(user_preferences)
    scored_list = scorer.score_all(recipes, user_profile)
    top_results = ranker.rank_recipes(scored_list, top_n=top_n)

    for item in top_results:
        item["explanation"] = explain.generate_explanation(
            item["recipe"],
            user_profile,
        )

    return top_results

# --- TEST THE ORCHESTRATOR ---
if __name__ == "__main__":
    # Simulate user input from a UI
    mock_preferences = {
        "cuisine": {"val": "Asian", "importance": "Strongly Agree"},
        "meal": {"val": "Dinner", "importance": "Agree"},
        "ingredient": {"val": "Poultry", "importance": "Unsure"}
    }

    print("Running recommendation engine...\n")
    results = get_recommendations(mock_preferences)

    for i, res in enumerate(results, 1):
        recipe = res['recipe']
        print(f"{i}. {recipe['title']} (Score: {res['score']})")
        print(f"   {res['explanation']['sentence']}\n")

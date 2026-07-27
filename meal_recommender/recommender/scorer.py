def as_list(value):
    if value in [None, "", [], {}]:
        return []

    if isinstance(value, list):
        return value

    return [value]


def has_any_match(selected_values, recipe_values):
    selected = set(as_list(selected_values))
    available = set(as_list(recipe_values))
    return bool(selected.intersection(available))


def matching_values(selected_values, recipe_values):
    selected = set(as_list(selected_values))
    available = set(as_list(recipe_values))
    return sorted(selected.intersection(available))

def score_recipe(recipe, profile):
    score = 0
    matched_attributes = []
    tags = recipe.get("tags", {})
    base_points = 2

    excluded = profile.get("exclude_ingredients", {}).get("value")
    recipe_ingredients = tags.get("ingredient_grouped") or []

    if has_any_match(excluded, recipe_ingredients):
        return {
            "score": -1,
            "matched_attributes": ["Excluded ingredient"],
            "excluded": True,
        }

    user_meal_data = profile.get("meal", {})
    user_meal_values = user_meal_data.get("value")
    user_meal_weight = user_meal_data.get("weight", 0)
    recipe_meal = recipe.get("primary_meal")

    if has_any_match(user_meal_values, recipe_meal):
        matches = matching_values(user_meal_values, recipe_meal)
        points = base_points * user_meal_weight
        score += points
        matched_attributes.append(f"Meal: {', '.join(matches)} (+{points})")

    user_time_data = profile.get("cooking_time", {})
    user_time_val = user_time_data.get("value")
    user_time_weight = user_time_data.get("weight", 0)
    recipe_time = recipe.get("cooking_time")

    if user_time_val and recipe_time:
        try:
            if float(recipe_time) <= float(user_time_val):
                points = base_points * user_time_weight
                score += points
                matched_attributes.append(f"Cooking Time (+{points})")
        except (ValueError, TypeError):
            pass

    criteria = [
        ("cuisine", "cuisine_grouped", "Cuisine"),
        ("ingredient", "ingredient_grouped", "Ingredient"),
        ("type", "type_grouped", "Type"),
        ("simple_cooking", "simple-cooking", "Simple Cooking"),
        ("special", "special-consideration", "Special Consideration"),
    ]

    for prof_key, json_key, label in criteria:
        user_data = profile.get(prof_key, {})
        user_values = user_data.get("value")
        user_weight = user_data.get("weight", 0)
        recipe_values = tags.get(json_key)

        if has_any_match(user_values, recipe_values):
            matches = matching_values(user_values, recipe_values)
            points = base_points * user_weight
            score += points
            matched_attributes.append(
                f"{label}: {', '.join(matches)} (+{points})"
            )

    return {
        "score": score,
        "matched_attributes": matched_attributes,
        "excluded": False,
    }

def score_all(recipes, profile):
    scored_recipes = []

    for recipe in recipes:
        result = score_recipe(recipe, profile)

        if result.get("excluded"):
            continue

        scored_recipes.append(
            {
                "recipe": recipe,
                "score": result["score"],
                "matched_attributes": result["matched_attributes"],
            }
        )

    scored_recipes.sort(key=lambda x: x["score"], reverse=True)
    return scored_recipes

# --- Testing with Weights ---
if __name__ == "__main__":
    test_recipe = {
        "title": "Asian Chicken Noodles",
        "primary_meal": "Dinner",
        "cooking_time": 20,
        "tags": {
            "cuisine_grouped": ["Asian"],
            "ingredient_grouped": ["Poultry"]
        }
    }

    # New Profile Structure: Value + Likert Weight (1-5)
    test_profile = {
        "cuisine": {"value": "Asian", "weight": 5},        # High Priority: 2 * 5 = 10
        "meal": {"value": "Dinner", "weight": 2},           # Low Priority:  2 * 2 = 4
        "cooking_time": {"value": 30, "weight": 3},        # Neutral:       2 * 3 = 6
        "ingredient": {"value": "Poultry", "weight": 4}    # Important:     2 * 4 = 8
    }

    result = score_recipe(test_recipe, test_profile)
    
    print(f"Results for: {test_recipe['title']}")
    print(f"Total Score: {result['score']}") # Expected: 10 + 4 + 6 + 8 = 28
    print(f"Details: {', '.join(result['matched_attributes'])}")

    '''
    The Importance Scale (Unipolar)

In social science research, this is often preferred over Likert for determining weights. It measures the absolute "weight" an individual gives to a specific attribute.

    Labels:

       1.  Not at all important

       2.  Slightly important

       3.  Moderately important

       4.  Very important

       5.  Extremely important
    '''
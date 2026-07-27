from recommender.scorer import has_any_match, matching_values


def generate_explanation(recipe, profile):
    """
    Analyzes a recipe against a profile to produce a human-readable 
    list of matches and a summary sentence.
    """
    matches = []
    tags = recipe.get('tags', {})

    # 1. Logic to identify matches (Independent of points)
    
    # Meal
    user_meal = profile.get("meal", {}).get("value")
    recipe_meal = recipe.get("primary_meal")
    if has_any_match(user_meal, recipe_meal):
        matched_meals = matching_values(user_meal, recipe_meal)
        matches.append(f"{', '.join(matched_meals)} meal")

    # Cuisine
    user_cuisine = profile.get("cuisine", {}).get("value")
    recipe_cuisine = tags.get("cuisine_grouped") or []
    if has_any_match(user_cuisine, recipe_cuisine):
        matched_cuisines = matching_values(user_cuisine, recipe_cuisine)
        matches.append(f"{', '.join(matched_cuisines)} cuisine")

    # Ingredient
    user_ing = profile.get("ingredient", {}).get("value")
    recipe_ingredients = tags.get("ingredient_grouped") or []
    if has_any_match(user_ing, recipe_ingredients):
        matched_ingredients = matching_values(user_ing, recipe_ingredients)
        matches.append(f"{', '.join(matched_ingredients)} ingredient group")

    # Type
    user_type = profile.get("type", {}).get("value")
    recipe_types = tags.get("type_grouped") or []
    if has_any_match(user_type, recipe_types):
        matched_types = matching_values(user_type, recipe_types)
        matches.append(f"{', '.join(matched_types)} category")

    # Simple Cooking
    user_simple = profile.get("simple_cooking", {}).get("value")
    recipe_simple = tags.get("simple-cooking") or []
    if has_any_match(user_simple, recipe_simple):
        matched_simple = matching_values(user_simple, recipe_simple)
        matches.append(f"{', '.join(matched_simple)} cooking style")

    # Special Consideration
    user_special = profile.get("special", {}).get("value")
    recipe_special = tags.get("special-consideration") or []
    if has_any_match(user_special, recipe_special):
        matched_special = matching_values(user_special, recipe_special)
        matches.append(f"{', '.join(matched_special)} dietary preference")

    # Cooking Time
    user_time = profile.get('cooking_time', {}).get('value')
    recipe_time = recipe.get('cooking_time')
    if user_time and recipe_time:
        try:
            if float(recipe_time) <= float(user_time):
                matches.append(f"cooking time (under {user_time} mins)")
        except (ValueError, TypeError):
            pass

    # 2. Format the Output
    if not matches:
        return {
            "list": "No specific matches found.",
            "sentence": "Recommended based on general variety."
        }

    # Create the Checkbox list
    checkbox_list = "Matches:\n" + "\n".join([f"[x] {m}" for m in matches])

    # Create the Summary Sentence
    if len(matches) == 1:
        sentence = f"Recommended because it matches your selected {matches[0]}."
    else:
        # Joining list with commas and an 'and' for the last item
        # Example: "Asian cuisine, Poultry ingredient group and Dinner meal"
        all_but_last = ", ".join(matches[:-1])
        sentence = f"Recommended because it matches your selected {all_but_last} and {matches[-1]}."

    return {
        "list": checkbox_list,
        "sentence": sentence
    }



# --- TEST ---
if __name__ == "__main__":
    # Example data
    mock_recipe = {
        "primary_meal": "Dinner",
        "tags": {
            "cuisine_grouped": ["Asian"],
            "ingredient_grouped": ["Poultry"]
        }
    }
    mock_profile = {
        "cuisine": {"value": "Asian"},
        "ingredient": {"value": "Poultry"},
        "meal": {"value": "Dinner"}
    }

    explanation = generate_explanation(mock_recipe, mock_profile)
    print(explanation["list"])
    print("\n" + explanation["sentence"])

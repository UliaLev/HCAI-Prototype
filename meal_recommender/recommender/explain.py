def generate_explanation(recipe, profile):
    """
    Analyzes a recipe against a profile to produce a human-readable 
    list of matches and a summary sentence.
    """
    matches = []
    tags = recipe.get('tags', {})

    # 1. Logic to identify matches (Independent of points)
    
    # Meal
    user_meal = profile.get('meal', {}).get('value')
    if user_meal and user_meal == recipe.get('primary_meal'):
        matches.append(f"{user_meal} meal")

    # Cuisine
    user_cuisine = profile.get('cuisine', {}).get('value')
    if user_cuisine and user_cuisine in (tags.get('cuisine_grouped') or []):
        matches.append(f"{user_cuisine} cuisine")

    # Ingredient
    user_ing = profile.get('ingredient', {}).get('value')
    if user_ing and user_ing in (tags.get('ingredient_grouped') or []):
        matches.append(f"{user_ing} ingredient group")

    # Type
    user_type = profile.get('type', {}).get('value')
    if user_type and user_type in (tags.get('type_grouped') or []):
        matches.append(f"{user_type} category")

    # Simple Cooking
    user_simple = profile.get('simple_cooking', {}).get('value')
    if user_simple and user_simple in (tags.get('simple-cooking') or []):
        matches.append(f"{user_simple} cooking style")

    # Special Consideration
    user_special = profile.get('special', {}).get('value')
    if user_special and user_special in (tags.get('special-consideration') or []):
        matches.append(f"{user_special} requirement")

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

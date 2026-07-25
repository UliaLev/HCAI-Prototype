def score_recipe(recipe, profile):
    """
    Scores a recipe based on user profile using multiplication:
    Score = Base Points (2) * Likert Weight (1-5)
    """
    score = 0
    matched_attributes = []
    tags = recipe.get('tags', {})
    BASE_POINTS = 2

    # 1. Handle Primary Meal
    # profile['meal'] is now a dict: {"value": "Dinner", "weight": 5}
    user_meal_data = profile.get('meal', {})
    user_meal_val = user_meal_data.get('value')
    user_meal_weight = user_meal_data.get('weight', 0)
    
    recipe_meal = recipe.get('primary_meal')

    if user_meal_val and recipe_meal:
        if user_meal_val == recipe_meal:
            points = BASE_POINTS * user_meal_weight
            score += points
            matched_attributes.append(f"Meal (+{points})")

    # 2. Handle Cooking Time
    user_time_data = profile.get('cooking_time', {})
    user_time_val = user_time_data.get('value')
    user_time_weight = user_time_data.get('weight', 0)
    
    recipe_time = recipe.get('cooking_time')

    if user_time_val and recipe_time:
        try:
            if float(recipe_time) <= float(user_time_val):
                points = BASE_POINTS * user_time_weight
                score += points
                matched_attributes.append(f"Cooking Time (+{points})")
        except (ValueError, TypeError):
            pass

    # 3. Handle Tags (Cuisine, Ingredient, Type, etc.)
    criteria = [
        ('cuisine', 'cuisine_grouped', 'Cuisine'),
        ('ingredient', 'ingredient_grouped', 'Ingredient'),
        ('type', 'type_grouped', 'Type'),
        ('simple_cooking', 'simple-cooking', 'Simple Cooking'),
        ('special', 'special-consideration', 'Special Consideration')
    ]

    for prof_key, json_key, label in criteria:
        user_data = profile.get(prof_key, {})
        user_val = user_data.get('value')
        user_weight = user_data.get('weight', 0)
        
        recipe_list = tags.get(json_key)

        if user_val and recipe_list:
            if user_val in recipe_list:
                points = BASE_POINTS * user_weight
                score += points
                matched_attributes.append(f"{label} (+{points})")

    return {
        "score": score,
        "matched_attributes": matched_attributes
    }

def score_all(recipes, profile):
    scored_recipes = []
    for recipe in recipes:
        result = score_recipe(recipe, profile)
        scored_recipes.append({
            "recipe": recipe,
            "score": result['score'],
            "matched_attributes": result['matched_attributes']
        })
    # Optional: Sort them here or in ranker.py
    scored_recipes.sort(key=lambda x: x['score'], reverse=True)
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
# profile.py

IMPORTANCE_WEIGHTS = {
    "Not at all important": 1,
    "Slightly important": 2,
    "Moderately important": 3,
    "Very important": 4,
    "Extremely important": 5
}

def _normalize_preference(preference):
    """
    Standardizes user input.
    Rule: If a value is selected but no importance is given, default weight is 1.
    If no value is selected, weight is 0.
    """
    if not preference:
        return {"value": None, "weight": 0}

    # Extract the value (handles both 'val' or 'value' keys)
    val = preference.get("val") or preference.get("value")
    
    # Handle 'Any' or empty selections
    if val is None or val == "Any" or val == "":
        return {"value": None, "weight": 0}

    # Extract the importance
    importance_label = preference.get("importance")
    
    # Logic: If importance_label is missing or None, .get() returns 1 (our default)
    # If importance_label exists in IMPORTANCE_WEIGHTS, it returns 1-5
    weight = IMPORTANCE_WEIGHTS.get(importance_label, 1)

    return {
        "value": val,
        "weight": weight
    }

def create_profile(user_preferences=None, **kwargs):
    """
    Creates a standardized profile. 
    Can accept a single dictionary or individual keyword arguments.
    """
    if user_preferences is None:
        user_preferences = kwargs

    # We map every attribute through the normalization function
    return {
        "cuisine": _normalize_preference(user_preferences.get("cuisine")),
        "meal": _normalize_preference(user_preferences.get("meal")),
        "ingredient": _normalize_preference(user_preferences.get("ingredient")),
        "type": _normalize_preference(user_preferences.get("type") or user_preferences.get("recipe_type")),
        "simple_cooking": _normalize_preference(user_preferences.get("simple_cooking")),
        "special": _normalize_preference(user_preferences.get("special")),
        "cooking_time": _normalize_preference(user_preferences.get("cooking_time"))
    }

if __name__ == "__main__":
    # TEST 1: Value selected, but importance is missing (Should be Weight 1)
    test_1 = {"cuisine": {"val": "Asian"}}
    
    # TEST 2: Value selected with importance (Should be Weight 5)
    test_2 = {"cuisine": {"val": "Asian", "importance": "Extremely important"}}
    
    # TEST 3: No value selected (Should be Weight 0)
    test_3 = {"cuisine": {"val": "Any"}}

    print("Test 1 (Default):", create_profile(test_1)["cuisine"])
    print("Test 2 (Scale):  ", create_profile(test_2)["cuisine"])
    print("Test 3 (Ignore): ", create_profile(test_3)["cuisine"])
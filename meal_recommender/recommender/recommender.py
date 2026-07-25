import random
from . import loader
from . import profile
from . import scorer
from . import ranker
from . import explain
from pathlib import Path

def get_diverse_discovery(recipes, count=10):
    """
    Returns 10 recipes from different cuisines to give the user a diverse start.
    """
    diverse_results = []
    seen_cuisines = set()
    
    # Shuffle the list so the discovery feels fresh every time
    shuffled_recipes = recipes.copy()
    random.shuffle(shuffled_recipes)

    for r in shuffled_recipes:
        cuisines = r.get('tags', {}).get('cuisine_grouped', [])
        # Get the first cuisine in the list, or "Generic" if none
        primary_cuisine = cuisines[0] if cuisines else "Other"

        if primary_cuisine not in seen_cuisines:
            diverse_results.append({
                "recipe": r,
                "score": 0,
                "matched_attributes": [],
                "explanation": {
                    "list": "Discovery Mode",
                    "sentence": f"Recommended to introduce you to {primary_cuisine} cuisine."
                }
            })
            seen_cuisines.add(primary_cuisine)

        if len(diverse_results) >= count:
            break
            
    return diverse_results

# to make callable from the streamlit app
filepath = Path(__file__).resolve().parent.parent / "data" / "recipes_group_preprocessed.json"

def get_recommendations(user_preferences, filepath=filepath, top_n=10):
    recipes = loader.load_recipes(filepath)

    # CHECK: Is the user preference dictionary empty?
    # We check if every value is None or "Any"
    is_empty = all(
        pref.get('val') is None or pref.get('val') == "Any" 
        for pref in user_preferences.values()
    )

    if is_empty:
        return get_diverse_discovery(recipes, count=top_n)

    # If NOT empty, proceed with normal logic
    user_profile = profile.create_profile(user_preferences)
    scored_list = scorer.score_all(recipes, user_profile)
    top_results = ranker.rank_recipes(scored_list, top_n=top_n)

    for item in top_results:
        item['explanation'] = explain.generate_explanation(item['recipe'], user_profile)

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
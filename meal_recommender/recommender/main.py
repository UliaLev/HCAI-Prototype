import sys
import recommender

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def main():
    # 1. Hardcode your test preferences
    # Using the structure: {"val": "Choice", "importance": "Scale"}

    '''user_preferences = {
        "cuisine": {"val": "Asian", "importance": "Strongly Agree"},
        "ingredient": {"val": "Poultry", "importance": "Agree"},
        "meal": {"val": "Dinner", "importance": "Unsure"},
        "cooking_time": {"val": 30, "importance": "Strongly Agree"}
    }
'''
    user_preferences = {
        "cuisine": {"val": None},
        "meal": {"val": None}
    }

    # 2. Call the Orchestratorad -> Profile -> Score -> Rank -> Explain
    results = recommender.get_recommendations(user_preferences, top_n=5)

    # 3. Print the results
    if not results:
        print("No recipes found matching your criteria.")
    else:
        for i, item in enumerate(results, 1):
            recipe = item['recipe']
            score = item['score']
            explanation = item['explanation']

            print(f"{i}. {recipe['title'].upper()}")
            print(f"   SCORE: {score}")
            print(f"   {explanation['list']}")
            print(f"   EXPLANATION: {explanation['sentence']}")
            print("-" * 50)

if __name__ == "__main__":
    main()

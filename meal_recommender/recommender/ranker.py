
def rank_recipes(scored_recipes, top_n=10):
     # Sort by score in descending order
    scored_recipes.sort(key=lambda item: item['score'], reverse=True)
    return scored_recipes[:top_n]


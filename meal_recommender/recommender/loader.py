# load_recipes(filepath)
'''
open the JSON file
load it into memory
return a list of recipes
'''
import json

filepath = "../data/recipes_group_preprocessed.json"

def normalize(value):
    """Converts empty-ish values (empty strings, empty lists, None) to None."""
    if value in [None, "", " ", [], {}]:
        return None
    return value


def load_recipes(filepath):
    with open(filepath, "r", encoding='utf-8') as f:
        data = json.load(f)

        for recipe in data:
            # Normalize the recipe attributes
            recipe['title'] = normalize(recipe.get('title'))
            recipe['cooking_time'] = normalize(recipe.get('cooking_time'))
            recipe['primary_meal'] = normalize(recipe.get('primary_meal'))
            recipe['cooking_time'] = normalize(recipe.get('cooking_time'))
            
            # Normalize the nested 'tags' dictionary
            tags = recipe.get('tags', {})
            for key in tags:
                tags[key] = normalize(tags.get(key))

        return data


def inspect_recipe(recipe):
    """Prints specific attributes of a single recipe."""
    print(f"RECIPE")
    print(f"Title: {recipe.get('title')}")
    print(f"Cooking Time:{recipe.get('cooking_time')} minutes")
    print(f"Meal (Primary): {recipe.get('primary_meal')}")
    
    #  nested inside the tags dictionary
    tags = recipe.get('tags', {})
    
    print(f"Cuisine Grouped: {tags.get('cuisine_grouped')}")
    print(f"Ingredient Grouped: {tags.get('ingredient_grouped')}")
    print(f"Type Grouped: {tags.get('type_grouped')}")
    
    # Note: JSON keys use hyphens '-' instead of underscores '_'
    print(f"Simple Cooking: {tags.get('simple-cooking')}")
    print(f"Special Consideration: {tags.get('special-consideration')}")


if __name__ == "__main__":
    filepath = "../data/recipes_group_preprocessed.json"
    recipes = load_recipes(filepath)
    
    if recipes:
        # Inspect the first recipe in the list
        inspect_recipe(recipes[0])
'''
if __name__ == "__main__":
    recipes = load_recipes(filepath)
    print(f"Successfully loaded {len(recipes)} recipes.")
    '''
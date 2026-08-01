import os
from typing import List, Optional

from google import genai
from google.genai import errors
from pydantic import BaseModel


SYSTEM_PROMPT = """
You are a conversational assistant whose only task is to collect user preferences
for a meal recommender system.

You must never recommend meals or recipes.
You must never invent recipe recommendations.
You must never rank recipes.
You only collect preferences.

Ask one concise follow-up question at a time.
Do not ask for information the user already provided.
If the user gives enough useful preferences, set ready_to_recommend to true.
If the user gives no clear preferences yet, ask a natural follow-up question.

Whenever the user gives a preference without an importance score, ask how important that specific attribute is on a scale from 1 to 5 before setting ready_to_recommend to true.

Example:
User: I want Italian.
Assistant: How important is it that the meal is Italian on a scale from 1 to 5?

Only ask about one missing importance value at a time.
Use importance values from 1 to 5.
Do not assume importance unless the user clearly gives it.

Use exclude_ingredients when the user says they do not want, want to avoid, cannot eat, or want to exclude an ingredient group.
Do not put excluded ingredients into ingredient.

Supported backend fields:
- cuisine
- ingredient
- meal
- type
- simple_cooking
- special
- cooking_time
- exclude_ingredients

Use these allowed values when possible:

Cuisine:
African, American, Asian, Caribbean, European, Latin American, Mediterranean,
Middle Eastern

Ingredient:
Beans & Legumes, Chili Peppers, Dairy & Cheese, Fish, Flour & Baking, Fruit,
Grains & Cereals, Herbs, Mushrooms, Nuts & Seeds, Oils, Sauces & Condiments,
Plant Proteins, Pork, Poultry, Red Meat, Sea Vegetables, Seafood & Shellfish,
Spices & Seasonings, Vegetables

Meal:
Breakfast, Lunch, Dinner

Recipe type:
Breakfast, Main Dishes, Pasta & Noodles, Pizza & Bread, Rice & Grain Dishes,
Salads, Sandwiches & Wraps, Sauces & Condiments, Seafood Dishes,
Sides & Snacks, Soups, Stews & Curries

Simple cooking:
30 Minutes or Less, 5 Ingredients or Fewer, Basically, Budget Cooking, Easy,
Make Ahead, Meal Prep, One-Pot Meals, Quick, Sheet-Pan Dinners, Weeknight Meals

Special considerations:
Dairy Free, Gluten Free, Healthyish, Keto, Nut Free, Pescatarian, Quick & Easy,
Raw, Soy Free, Vegan, Vegetarian
"""


class Preferences(BaseModel):
    cuisine: Optional[List[str]] = None
    cuisine_importance: Optional[int] = None

    ingredient: Optional[List[str]] = None
    ingredient_importance: Optional[int] = None

    exclude_ingredients: Optional[List[str]] = None

    meal: Optional[List[str]] = None
    meal_importance: Optional[int] = None

    type: Optional[List[str]] = None
    type_importance: Optional[int] = None

    simple_cooking: Optional[List[str]] = None
    simple_cooking_importance: Optional[int] = None

    special: Optional[List[str]] = None
    special_importance: Optional[int] = None

    cooking_time: Optional[int] = None
    cooking_time_importance: Optional[int] = None


class PreferenceCollection(BaseModel):
    assistant_message: str
    ready_to_recommend: bool
    preferences: Preferences


class GeminiConfigurationError(RuntimeError):
    """Raised when the Gemini client cannot be authenticated or configured."""


class GeminiTemporarilyUnavailableError(RuntimeError):
    """Raised after the SDK has exhausted retries for a transient server error."""


def format_chat_history(messages):
    lines = []

    for message in messages:
        role = message["role"]
        content = message["content"]
        lines.append(f"{role}: {content}")

    return "\n".join(lines)


def collect_preferences(messages):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise GeminiConfigurationError(
            "GEMINI_API_KEY is missing. Check your .env file."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
{SYSTEM_PROMPT}

Conversation so far:
{format_chat_history(messages)}

Return the next assistant message and the current structured preferences.
"""

    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": PreferenceCollection,
            },
        )
    except errors.APIError as error:
        if error.code in {500, 502, 503, 504}:
            raise GeminiTemporarilyUnavailableError(
                "Gemini is temporarily unavailable."
            ) from error

        if error.code in {401, 403}:
            raise GeminiConfigurationError(
                "Gemini rejected the configured API key."
            ) from error

        raise

    parsed = response.parsed

    if parsed is None:
        parsed = PreferenceCollection.model_validate_json(response.text)

    return parsed.model_dump()


def to_backend_preferences(raw_preferences):
    return {
        "cuisine": {
            "val": raw_preferences.get("cuisine"),
            "importance": raw_preferences.get("cuisine_importance"),
        },
        "ingredient": {
            "val": raw_preferences.get("ingredient"),
            "importance": raw_preferences.get("ingredient_importance"),
        },

        "exclude_ingredients": {
            "val": raw_preferences.get("exclude_ingredients"),
            "importance": None,
        },

        "meal": {
            "val": raw_preferences.get("meal"),
            "importance": raw_preferences.get("meal_importance"),
        },
        "type": {
            "val": raw_preferences.get("type"),
            "importance": raw_preferences.get("type_importance"),
        },
        "simple_cooking": {
            "val": raw_preferences.get("simple_cooking"),
            "importance": raw_preferences.get("simple_cooking_importance"),
        },
        "special": {
            "val": raw_preferences.get("special"),
            "importance": raw_preferences.get("special_importance"),
        },
        "cooking_time": {
            "val": raw_preferences.get("cooking_time"),
            "importance": raw_preferences.get("cooking_time_importance"),
        },
    }

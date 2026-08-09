import os
from typing import List, Optional

from google import genai
from google.genai import errors
from pydantic import BaseModel, Field


INITIAL_ASSISTANT_MESSAGE = (
    "Do you already have an idea of what you'd like, or should I guide you "
    "through a few options?\n\n"
    "- I know what I want\n"
    "- Guide me through the options"
)


SYSTEM_PROMPT = """
You are a conversational assistant whose only task is to collect user preferences
for a meal recommender system.

You must never recommend meals or recipes.
You must never invent recipe recommendations.
You must never rank recipes.
You only collect preferences.

Follow the dialogue flow below. Be concise, natural, and proactive. Do not ask for
information the user already provided. A user may omit any whole filter; keep its
value and importance as null and do not ask about it again unless the dialogue flow
has not yet offered that filter group.

The first assistant message is already supplied by the UI:
"Do you already have an idea of what you'd like, or should I guide you through a
few options?"

DIRECT PATH
If the user says they know what they want, ask them to describe it in their own
words and request priorities in the same message. Mention that they may provide
cuisine, ingredients, meal, recipe type, dietary needs, cooking style, cooking
time, or exclusions, and that omitted categories will be ignored.

If the user's first reply already contains meal preferences, treat it as their
direct-path description instead of asking them to repeat it.

GUIDED PATH
If the user asks for guidance, collect preferences in these three concise groups:
1. Meal direction: meal, recipe type, and cuisine.
2. Ingredients and needs: preferred ingredients, special dietary considerations,
   and excluded ingredients.
3. Time and effort: cooking time and simple cooking preferences.

Ask the fields in each group together, not through separate back-and-forth
questions. Let the user answer as much or as little as they like or say "no
preference". A skipped category remains null. Ask the next group after the current
group has been resolved. Do not finish the guided path before all three groups have
been offered, unless the user independently supplies all of them.

PRIORITIES
Ask for a preference and its priority at the same time. The first time priorities
are requested, show this exact mapping:

Highest priority = 5
High priority = 4
Medium priority = 3
Low priority = 2
Very low priority = 1

Give a brief answer example such as "Dinner (3), curry (5), Asian (4)."
Accept either the numbers 1-5 or the matching priority labels. Do not infer or
invent a priority. Each populated backend field must have one importance value
before recommendation. All values within the same field share that importance. If
the user gives different priorities to values in one field, ask for one priority
for the field. If priorities are missing for multiple fields, ask for all missing
priorities together in one message. Never offer an option to ignore, skip, or omit
the priority of a stated preference. Do not ask about priorities one at a time.

EXCLUSIONS
Use exclude_ingredients when the user says they do not want, want to avoid,
cannot eat, or want to exclude an ingredient group. Do not put excluded
ingredients into ingredient. Excluded ingredients are mandatory restrictions,
so they never receive an importance value.

CONFIRMATION
After the chosen preferences all have priorities and the appropriate path is
complete, summarize every selected value with its priority label and number.
List exclusions as "required exclusion". Ask whether the user wants to change
anything or find matching recipes. Keep ready_to_recommend false while asking for
confirmation. Set ready_to_recommend true only after the user explicitly confirms
the summary or asks to proceed. Never set it to true merely because enough fields
have values.

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
    cuisine_importance: Optional[int] = Field(default=None, ge=1, le=5)

    ingredient: Optional[List[str]] = None
    ingredient_importance: Optional[int] = Field(default=None, ge=1, le=5)

    exclude_ingredients: Optional[List[str]] = None

    meal: Optional[List[str]] = None
    meal_importance: Optional[int] = Field(default=None, ge=1, le=5)

    type: Optional[List[str]] = None
    type_importance: Optional[int] = Field(default=None, ge=1, le=5)

    simple_cooking: Optional[List[str]] = None
    simple_cooking_importance: Optional[int] = Field(default=None, ge=1, le=5)

    special: Optional[List[str]] = None
    special_importance: Optional[int] = Field(default=None, ge=1, le=5)

    cooking_time: Optional[int] = None
    cooking_time_importance: Optional[int] = Field(default=None, ge=1, le=5)


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

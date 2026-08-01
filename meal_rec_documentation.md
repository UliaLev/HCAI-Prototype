# Meal Recommender – Technical Documentation

## 1. Project Overview

The **Meal Recommender** is a web application developed with Streamlit for recommending recipes. Users can enter their meal preferences through two different interfaces:

1. a traditional filter interface,
2. a conversational chat interface.

Both interfaces use the same rule-based recommendation algorithm. The chat does not generate recipe recommendations. It only translates natural language into the structured preference format that is also used by the traditional filter interface.

By default, the application recommends up to 18 recipes. Each recommendation includes a short explanation, key recipe information, and a detailed view.

## 2. Technologies Used

The main dependencies are:

- **Python** as the programming language
- **Streamlit** for the web interface
- **Pandas** for data preparation in the notebooks
- **Google Gemini** for extracting preferences from chat messages
- **Pydantic** for validating the structured Gemini response
- **python-dotenv** for loading the Gemini API key
- **JSON** as the data format for the prepared recipe dataset

The recommendation algorithm itself does not require a machine-learning model. It is a transparent, rule-based content-based recommender system.

## 3. Project Structure

```text
Prototypes/
├── meal_recommender/
│   ├── app.py
│   ├── data/
│   │   └── recipes_group_preprocessed.json
│   ├── llm/
│   │   └── preference_extractor.py
│   ├── recommender/
│   │   ├── loader.py
│   │   ├── profile.py
│   │   ├── scorer.py
│   │   ├── ranker.py
│   │   ├── explain.py
│   │   └── recommender.py
│   └── ui/
│       ├── traditional.py
│       ├── conversational.py
│       ├── options.py
│       └── recipe_views.py
├── preparing_data/
│   ├── create_clean_subset.ipynb
│   ├── more_cleaning.ipynb
│   ├── attributes_grouping.ipynb
│   ├── recipes_test.ipynb
│   └── unique_grouped_values.ipynb
├── data/
│   ├── raw/
│   └── processed/
├── .streamlit/
│   └── config.toml
└── requirements.txt
```

## 4. Architecture and Layers

The application is divided into several logically separated layers.

### 4.1 Presentation Layer

The presentation layer consists of `app.py` and the modules in the `ui/` directory.

Its tasks are:

- displaying the filter and chat interfaces
- collecting user input
- displaying recommendations
- showing recipe details
- managing the selected meals
- managing the Streamlit session state
- passing structured preferences to the recommender

`app.py` is the entry point. The file configures the Streamlit page, loads global CSS rules, and creates the two main tabs:

- **Traditional filter**
- **Chat assistant**

### 4.2 State and Application Layer

Streamlit reruns the script whenever users interact with it. Persistent values are therefore stored in `st.session_state`.

The application manages, among other things:

- `results`: current recommendations
- `selected_recipe`: the detail view currently open
- `chat_messages`: the previous chat history
- `chat_retry_pending`: the status of a failed Gemini call - had to be added because of several cases of failed calls and therefore having to restart the application
- `last_preferences`: the most recently used preferences
- `chosen_meals`: recipes saved by the user

The two interfaces share these states. A result list generated through the filter interface is therefore generally also available in the chat tab and vice versa.

### 4.3 LLM Integration Layer

The file `llm/preference_extractor.py` connects the chat interface to Google Gemini.

Gemini has a clearly limited task:

- identifying preferences from natural language
- asking for missing importance ratings
- identifying exclusions
- converting the information into a defined JSON schema

According to the system prompt, Gemini is not allowed to invent, select, or rank recipes. The actual recommendation remains entirely with the rule-based recommender.

A structured response can, for example, contain the following values:

```json
{
  "cuisine": ["Asian"],
  "cuisine_importance": 5,
  "ingredient": ["Poultry"],
  "ingredient_importance": 3,
  "cooking_time": 30,
  "cooking_time_importance": 4
}
```

Pydantic validates this response. `to_backend_preferences()` then converts it into the shared backend format:

```json
{
  "cuisine": {
    "val": ["Asian"],
    "importance": 5
  },
  "ingredient": {
    "val": ["Poultry"],
    "importance": 3
  },
  "cooking_time": {
    "val": 30,
    "importance": 4
  }
}
```

A valid `GEMINI_API_KEY` in a `.env` file is required for the chat interface.

### 4.4 Recommendation and Domain Layer

The files under `recommender/` contain the actual recommendation logic.

| File             | Task                                                  |
| ---------------- | ----------------------------------------------------- |
| `loader.py`      | Loading and normalizing the recipe data               |
| `profile.py`     | Standardizing user preferences and importance ratings |
| `scorer.py`      | Calculating the score for each recipe                 |
| `ranker.py`      | Sorting and limiting the results                      |
| `explain.py`     | Generating understandable explanations                |
| `recommender.py` | Coordinating the entire process                       |

### 4.5 Data Layer

The recommender reads the prepared recipes from:

```text
meal_recommender/data/recipes_group_preprocessed.json
```

The loader replaces empty values such as empty strings, empty lists, or empty objects with `None`. This allows the recommendation logic to handle missing data more consistently.

### 4.6 Data Preparation Layer

The notebooks under `preparing_data/` generate the dataset used by the application from the raw dataset. The preparation is performed offline and is not executed each time the application starts.
Original dataset: [Recipe Dataset with Images, Tags, and Ratings](https://www.kaggle.com/datasets/seungyeonhan1/recipe-dataset-with-images-tags-and-ratings/data)

```text
Raw data
  → Remove unsuitable recipes and attributes
  → Further cleaning
  → Group detailed tags
  → JSON dataset for the application
```

## 5. User Interfaces

### 5.1 Traditional Filter Interface

The traditional interface is located in `ui/traditional.py`.

It offers filters for:

- cuisine or geographical region
- preferred ingredient groups
- ingredient groups to exclude
- meal: breakfast, lunch, or dinner
- recipe type
- simple or everyday preparation methods
- diets and special requirements
- maximum cooking time

The available options are not all hard-coded in the UI code. `ui/options.py` reads the values available in the recipe dataset, removes duplicates, and sorts them. This means that the filter interface generally adapts to the available data.

#### Importance of a Preference

For almost every filter, an importance value between 1 and 5 can be selected:

5. Highest priority
6. High priority
7. Medium priority
8. Low priority
9. Very low priority

The importance is represented in the interface by five selectable dots. The default value is 3.

Exclusions do not receive a weight. They function as hard constraint filters: recipes containing an excluded ingredient group are removed entirely.

The cooking time is optional. The selected maximum time is only passed to the recommender once the cooking-time filter has been activated.

### 5.2 Chat Interface

The chat interface is located in `ui/conversational.py`.

Users can express their requests in natural language, for example:

> I would like an Asian dinner with poultry that takes no more than 30 minutes.

Gemini extracts the relevant fields. When a preference is mentioned without an importance value, the assistant asks for a rating between 1 and 5. It should always ask for only one missing importance value at a time.

As soon as enough information is available, Gemini sets `ready_to_recommend` to `true`. The preferences are then passed to the same recommender used by the traditional interface.

The chat interface also handles the following error cases:

- a missing or invalid Gemini API key
- temporary server errors
- retrying a failed request
- discarding the last user message
- other processing errors

### 5.3 Shared Results View

The results view is implemented in `ui/recipe_views.py` and is used by both input interfaces.

The recommendations are displayed in a three-column grid. A recipe card contains:

- the recipe image, if it is available locally
- title
- grouped cuisine
- cooking time
- a short recommendation explanation
- a button for the detailed view
- a button for saving the meal

The detailed view displays:

- title and image
- cooking time
- primary meal
- detailed cuisine
- description
- ingredients
- numbered preparation steps
- detailed and grouped tags

Saved meals are stored in a shared list. Individual meals can be removed, or the entire list can be cleared.

## 6. Recommendation Algorithm

### 6.1 Type of Recommender

The algorithm is a **weighted, rule-based content-based recommender**.

Content-based means that the properties of a recipe are compared with the stated preferences. Ratings from other users are not used. It is therefore not collaborative filtering.

The algorithm does not learn from previous interactions. Every recommendation is calculated directly from the current preferences and the tags in the dataset.

### 6.2 Overall Process

The function `get_recommendations()` in `recommender/recommender.py` coordinates the process:

1. load the recipe dataset
2. check whether active preferences are available
3. use discovery mode if necessary
4. normalize user input
5. remove recipes with excluded ingredient groups
6. calculate a score for every remaining recipe
7. sort recipes in descending order by score
8. select the first 18 results
9. generate an explanation for every result

### 6.3 Normalization of the User Profile

`profile.py` standardizes the input from both user interfaces.

Each preference is converted into the following form:

```json
{
  "value": ["Asian"],
  "weight": 5
}
```

The following rules apply:

- No selection means `value = null` and `weight = 0`.
- `"Any"`, an empty string, or an empty list are treated as not selected.
- A selected preference without an importance value receives a default weight of 1.
- Valid importance values are between 1 and 5.
- Both single values and lists are supported.

### 6.4 Hard Exclusion Logic

Before points are calculated, the recommender checks excluded ingredient groups.

Thefollowing applies to a recipe `r`:

```text
Exclusion(r) =
    1, if intersection of excluded groups and recipe groups is not empty
    0, otherwise
```

When there is a match, the recipe is not simply given a lower score but is removed entirely from the candidate list.

The check is performed against `ingredient_grouped`. It therefore works at group level, for example:

- `Poultry`
- `Red Meat`
- `Dairy & Cheese`
- `Nuts & Seeds`

Excluding `Dairy & Cheese` therefore removes all recipes assigned to this group in the dataset. The individual ingredient lines of the recipe are not searched as text.

### 6.5 Scored Criteria

Up to seven criteria are checked for every recipe that is not excluded:

1. cuisine
2. preferred ingredient group
3. meal
4. recipe type
5. simple preparation method
6. special dietary requirement
7. maximum cooking time

For categories with several possible values, a set intersection is calculated. A criterion counts as fulfilled as soon as at least one selected value appears in the recipe.

For cooking time, the following applies:

```text
Criteria fulfilled if recipe time ≤ preferred maximum time
```

### 6.6 Score Calculation

A fulfilled criteria receives two base points multiplied by its importance.

For a criteria `k`:

```text
Points(k) = 2 × Weight(k) × Match(k)
```

Where:

- `Weight(k)` is a value from 0 to 5,
- `Match(k) = 1` if the criteria is fulfilled,
- `Match(k) = 0` if the criteria is not fulfilled.

The total score is:

```text
Score(Recipe) = Sum of all criteria: 2 × Weight × Match
```

A single criterion can therefore contribute the following number of points:

| Importance | Points when matched |
| ---------: | ------------------: |
|          1 |                   2 |
|          2 |                   4 |
|          3 |                   6 |
|          4 |                   8 |
|          5 |                  10 |

If all seven criteria are selected with a weight of 5 and fulfilled, the theoretical maximum score is 70 points.

Multiple matches within the same category do not increase the score further. For example, if both `Asian` and `European` are selected and a recipe belongs to both groups, the “cuisine” category is still scored only once.

### 6.7 Example Calculation

Suppose a person enters the following preferences:

- Asian cuisine, importance 5
- poultry, importance 4
- dinner, importance 2
- maximum 30 minutes, importance 3

A recipe fulfills all four conditions.

```text
Asian cuisine:  2 × 5 = 10 points
Poultry:         2 × 4 =  8 points
Dinner:          2 × 2 =  4 points
Cooking time:    2 × 3 =  6 points
Total score:              28 points
```

Another recipe that only fulfills Asian cuisine and dinner receives 14 points and is therefore ranked lower.

### 6.8 Sorting and Selection

All recipes that are not excluded are sorted in descending order by score. By default, the first 18 entries are then returned.

Recipes with a score of 0 generally remain in the candidate list. If too few recipes have positive matches, results without a direct match may therefore also appear.

For identical scores, the stable Python sort essentially preserves the original order of the dataset. Outside discovery mode, there is no additional diversity logic and no random tie-breaking.

### 6.9 Discovery Mode

If no positive preference has been entered, the application uses a discovery mode.

The process is:

1. shuffle recipes randomly
2. group recipes by their first grouped cuisine
3. shuffle the order of cuisines randomly
4. initially select no more than two recipes per cuisine
5. fill the remaining places with additional random recipes

The results receive a score of 0 and a short explanation stating which cuisine is being introduced.

Discovery mode is intended to create a more varied selection when no preferences have been entered yet. Because random functions are used without a fixed seed, the selection may change when the process is run again.

In the current code, exclusions alone are not considered a positive preference when deciding whether to use discovery mode. If only ingredients are excluded, discovery mode is therefore activated and the exclusion check is not performed.

### 6.10 Generating Explanations

`explain.py` checks again which selected properties match a recipe.

Possible parts of an explanation include:

- matching meal
- matching cuisine
- matching ingredient group
- matching recipe type
- matching preparation method
- matching diet
- maximum cooking time satisfied

A short natural-language explanation is composed from these matches. The explanation mentions the matches but not their weights. Importance therefore affects the order of recipes but is not directly shown in the visible explanation.

## 7. Preparation of the Recipe Dataset

### 7.1 Source Data

The data preparation expects the raw file:

```text
data/raw/recipes_images.json
```

The raw data contains recipe information, nested tags, and filenames for recipe images.
The original raw dataset was obtained from [Kaggle](https://www.kaggle.com/datasets/seungyeonhan1/recipe-dataset-with-images-tags-and-ratings/data).
It is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International licence (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/).

The cleaned dataset currently used by the application contains:

- **1,809 recipes**
- 115 breakfast recipes
- 579 lunch recipes
- 1,115 dinner recipes

The images are stored separately and linked to the recipes through `image_filename`.

### 7.2 First Cleaning Step

The notebook `create_clean_subset.ipynb` performs the main cleaning process.

First, unnecessary top-level fields are removed:

- `ratings`
- `servings`
- `publish_date`

The following categories are removed from the nested `tags` object:

- `technique`
- `equipment`
- `source`
- `cne-video-tags`
- `occasion`

As a result, the later dataset contains only properties that are relevant for display or recommendation.

### 7.3 Checking Required Fields

A recipe is retained only if the following information is available:

- a non-empty title
- ingredients
- preparation instructions
- image filename

The preparation steps may be provided as a dictionary, list, or text. For the quality check, they are temporarily combined into `instructions_flat`.

### 7.4 Determining the Primary Meal

A primary meal is derived from the original `meal` tags.

The permitted values are:

- `Breakfast`
- `Lunch`
- `Dinner`

The function checks the values in this order and uses the first available match as `primary_meal`. Recipes without one of these three meals are removed.

### 7.5 Removing Unsuitable Recipe Types

Beverages, alcohol, desserts, and various side dishes or incomplete dishes are removed using exclusion lists.

The check uses:

- individual words from the recipe title
- entries in the original `type` tag

Excluded categories include, for example, cocktails, alcoholic drinks, coffee, tea, soft drinks, cakes, cookies, ice cream, dips, sauces, and marinades.

The implementation uses simple title and exact type-tag values.

### 7.6 Limiting the Number of Ingredients

Recipes are retained only if they contain between 3 and 15 ingredients:

```text
MIN_INGREDIENTS = 3
MAX_INGREDIENTS = 15
```

This is intended to exclude both incomplete and very complex recipes from the prototype. The calculated number of ingredients is stored as `ing_count` in the final dataset.

### 7.7 Minimum Instruction Length

For lunch and dinner recipes, the combined preparation instructions must contain at least 150 characters:

```text
MIN_INSTRUCTION_LENGTH = 150
```

This rule does not apply to breakfast recipes. Short breakfast instructions may therefore remain in the dataset.

A list of simple-cooking tags is also defined in the notebook. However, this list is not applied as an additional filter in the current cleaning step.

### 7.8 Removing Recipes Without a Cuisine Assignment

Recipes without at least one value in the original field `tags.cuisine` are removed. A cuisine assignment is required because the geographical grouping later serves as a central recommendation feature.

The result of this step is saved as an intermediate version:

```text
data/processed/recipes_final_dataset2.json
```

### 7.9 Second Cleaning Step

The notebook `more_cleaning.ipynb` loads the first cleaned dataset and removes temporary fields:

- `instructions_flat`
- `instr_len`

The original nested `meal` tag is also removed. The previously generated top-level property `primary_meal` remains.

The result is saved as:

```text
data/processed/double_cleaned_recipes.json
```

### 7.10 Grouping Detailed Tags

The notebook `attributes_grouping.ipynb` reduces the large number of detailed tags to manageable categories for the user interface and the recommender.

The original detailed tags are retained. Three additional fields are added:

- `cuisine_grouped`
- `ingredient_grouped`
- `type_grouped`

The assignment is based on manually defined mapping tables. Detailed values that are not included in the tables do not receive a grouped category.

#### Grouped Cuisines

The current 8 cuisine regions are:

- African
- American
- Asian
- Caribbean
- European
- Latin American
- Mediterranean
- Middle Eastern

Examples:

```text
Japanese → Asian
Thai → Asian
German → European
Italian → European
Mexican → Latin American
Lebanese → Middle Eastern
```

A recipe can be assigned to several grouped cuisines. An Italian-American recipe can, for example, belong to both `American` and `European`.

#### Grouped Ingredients

The current dataset contains 19 ingredient groups:

- Beans & Legumes
- Chili Peppers
- Dairy & Cheese
- Fish
- Flour & Baking
- Fruit
- Grains & Cereals
- Herbs
- Mushrooms
- Nuts & Seeds
- Oils, Sauces & Condiments
- Plant Proteins
- Pork
- Poultry
- Red Meat
- Sea Vegetables
- Seafood & Shellfish
- Spices & Seasonings
- Vegetables

Examples:

```text
Chicken Breast → Poultry
Salmon → Fish
Shrimp → Seafood & Shellfish
Parmesan → Dairy & Cheese
Tomato → Vegetables
Lentil → Beans & Legumes
Tofu → Plant Proteins
```

#### Grouped Recipe Types

The current dataset contains 9 grouped recipe types:

- Breakfast
- Main Dishes
- Pasta & Noodles
- Pizza & Bread
- Rice & Grain Dishes
- Salads
- Sandwiches & Wraps
- Seafood Dishes
- Soups, Stews & Curries

Examples:

```text
Spaghetti → Pasta & Noodles
Risotto → Rice & Grain Dishes
Curry → Soups, Stews & Curries
Taco → Sandwiches & Wraps
Pizza → Pizza & Bread
```

The fully grouped dataset is saved directly for use by the application:

```text
meal_recommender/data/recipes_group_preprocessed.json
```

### 7.11 Validation and Analysis Notebooks

`recipes_test.ipynb` is used to examine the available attributes and unique tag values.

`unique_grouped_values.ipynb` lists unique values in the grouped fields and is used as a plausibility check for the grouping.

These notebooks are analysis tools and are not part of the application's runtime path.

## 8. Structure of a Prepared Recipe

A simplified entry from the final dataset looks as follows:

```json
{
  "title": "Penne with Shrimp, Red Onion, and Goat Cheese",
  "description": null,
  "ingredients": [
    "1 pound whole grain penne",
    "Kosher salt",
    "1 1/4 pounds shrimp"
  ],
  "instructions": {
    "1": "Cook the penne...",
    "2": "Heat oil in a skillet..."
  },
  "cooking_time": 30,
  "image_filename": "ba-syn-penne-with-shrimp-red-onion-and-goat-cheese",
  "primary_meal": "Lunch",
  "ing_count": 10,
  "tags": {
    "type": ["Pasta", "Penne"],
    "cuisine": ["Italian American", "Italian", "European"],
    "ingredient": ["Shrimp", "Tomato", "Goat Cheese"],
    "simple-cooking": ["Quick", "Weeknight Meals"],
    "special-consideration": ["Nut Free"],
    "cuisine_grouped": ["American", "European"],
    "ingredient_grouped": [
      "Seafood & Shellfish",
      "Vegetables",
      "Dairy & Cheese"
    ],
    "type_grouped": ["Pasta & Noodles"]
  }
}
```

The detailed tags are retained for the detailed view. The grouped tags are mainly used for filtering, scoring, and explanations.

## 9. Starting the Application

First, install the dependencies from the project root:

```bash
python -m pip install -r requirements.txt
```

Then start the application from the `meal_recommender` directory:

```bash
cd meal_recommender
streamlit run app.py
```

No external service is required for the traditional filter interface.

For the chat interface, a `.env` file containing a Gemini API key must be available:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

## 10. Properties and Limitations of the Current System

The system has the following properties:

- fully transparent score calculation
- identical recommendation algorithm for both interfaces
- clear separation between preference collection and recommendation
- hard exclusions for unwanted ingredient groups
- weighted preferences between 1 and 5
- understandable explanations for recommendations
- random suggestions diversified by cuisine when no preferences are provided

At the same time, there are several limitations:

- There is no personalization across multiple sessions.
- The system does not learn from selected or rejected recipes.
- There is no collaborative filtering.
- Similar terms are not recognized semantically.
- Quality depends heavily on the manually created tag mappings.
- Unknown or ungrouped tags do not affect the score.
- Multiple matches within one category do not provide additional points.
- Visible explanations mention matches but not their weight or score.
- Exclusion-only preferences are not applied in the current discovery mode.
- The allowed values mentioned in the chat prompt and the categories actually available in the dataset should be kept synchronized whenever changes are made.

## 11. Summary

The Meal Recommender combines two different methods of collecting preferences with a shared, rule-based recommendation system.

The traditional interface collects structured information directly through filters. The chat interface uses Gemini to translate natural language into the same data format. All recipes are then scored based on their grouped properties.

The central score is based on a simple and transparent formula:

```text
Score = Sum of all criteria: 2 × Importance × Match
```

Excluded ingredient groups cause a recipe to be removed entirely. All remaining recipes are sorted by their weighted match and displayed with an understandable explanation.

The recipe dataset was cleaned in advance, limited to complete main meals, and standardized using manually defined categories for cuisines, ingredients, and recipe types. This allows the application to work with a manageable number of understandable filters even though the original recipe data contains much more detailed tags.

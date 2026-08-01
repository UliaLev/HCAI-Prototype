The Meal Recommender combines two different methods of collecting preferences with a shared, rule-based recommendation system.

The traditional interface collects structured information directly through filters. The chat interface uses Gemini to translate natural language into the same data format. All recipes are then scored based on their grouped properties.

The central score is based on a simple and transparent formula:

```text
Score = Sum of all criteria: 2 × Importance × Match
```

Excluded ingredient groups cause a recipe to be removed entirely. All remaining recipes are sorted by their weighted match and displayed with an understandable explanation.

The recipe dataset was cleaned in advance, limited to complete main meals, and standardized using manually defined categories for cuisines, ingredients, and recipe types. This allows the application to work with a manageable number of understandable filters even though the original recipe data contains much more detailed tags.

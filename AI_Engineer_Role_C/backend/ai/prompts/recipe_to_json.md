Convert the following recipe text into Recipe JSON

Rules: 
- `canonical`: the ingredient's canonical name in English, lowercase. Add its state after a comma
(e.g. "red lentils, dried", "tomatoes, strained").

- `unit`: only "g", "ml" or "piece". Convert tablespoons, tea glasses, etc. to approximate g/ml.

- `quantity`: amount for `servings` people, a number greater than 0.

- `id`: kebab-case slug from the title (e.g. "red-lentil-curry").

- Skip "to taste" ingredients such as salt and black pepper.

Recipe:
{recipe_text}


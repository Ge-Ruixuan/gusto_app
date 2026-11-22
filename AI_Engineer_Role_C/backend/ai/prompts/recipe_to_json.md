Convert the following recipe text into Recipe JSON

Rules: 
- `canonical`: the ingredient's canonical name in German,lowercase. Add its state after a comma
(e.g. "rote linsen, getrocknet", "tomaten, passiert").

- `unit`: only "g", "ml" or "stück". Convert tablespoons, tea glasses, etc. to approximate g/ml.

- `quantity`: amount for `servings` people, a number greater than 0.

- `id`: kebab-case slug from the title (e.g. "rote-linsen-curry").

- Skip "to taste" ingredients such as salt and black pepper.

Recipe:
{recipe_text}


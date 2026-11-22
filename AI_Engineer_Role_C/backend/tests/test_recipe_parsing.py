"""Goal: a valid Recipe object from a recipe text.

- Default tests use a fake model (no API key needed, runs in CI).
- Real API test: `pytest -m live` (requires ANTHROPIC_API_KEY).
"""

import json
import os
from pathlib import Path

import pytest

from backend.ai.llm_client import LLMOutputError, generate
from backend.ai.schemas import Recipe, Unit

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = json.loads((ROOT / "data/recipes/rote-linsen-curry.json").read_text())
PROMPT = (ROOT / "backend/ai/prompts/recipe_to_json.md").read_text()

RECIPE_TEXT = """Red-Lentils-Curry (Serves 2)
200 g dried red lentils, 400 ml coconut milk, 1 onion.
Sauté the onion, add the lentils and coconut milk, cook for 20 minutes."""

def test_sample_recipe_is_valid():
    r = Recipe.model_validate(SAMPLE)
    assert r.ingredients[0].unit is Unit.g

def test_generate_returns_recipe_with_fake_model():
    fake = lambda system, user: "```json\n" + json.dumps(SAMPLE) + "\n```"
    r = generate(PROMPT.format(recipe_text=RECIPE_TEXT), Recipe, call=fake)
    assert r.id == "rote-linsen-curry"

def test_generate_retries_after_invalid_json():
    answers = iter(["bu json değil", json.dumps(SAMPLE)])
    r = generate("x", Recipe, call=lambda s, u: next(answers))
    assert r.servings == 2

def test_generate_rejects_unkown_unit():
    bad = {**SAMPLE, "ingredients": [{"canonical": "milch", "quantity": 1, "unit": "tasse"}]}
    with pytest.raises(LLMOutputError):
        generate("x",Recipe,call=lambda s,u : json.dumps(bad))

@pytest.mark.live
@pytest.mark.skipif(not os.getenv("ANTROPIC_API_KEY"),reason="API key not exists")
def test_generate_live():
    r = generate(PROMPT.format(recipe_text=RECIPE_TEXT),Recipe)
    assert len(r.ingredients) >= 3
    assert all(i.unit in Unit for i in r.ingredients)




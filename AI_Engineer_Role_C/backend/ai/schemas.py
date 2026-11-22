"""Data models of the AI layer
Rules:
- Ingredient names are German and must be in lowercase: matches with the names.
- Units come from a fixed list: g,ml,stück.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel,ConfigDict,Field,field_vaidator

class Unit(str,Enum):
    g = "g"
    ml = "ml"
    stück = "stück"

class Ingredient(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canonical: str = Field(...,min_length=2,
                           description = "Canonical name of the ingredient in German, lowercase. Exp: 'rote linsen, getrocknet'",
                           )
    quantity: float = Field(...,gt=0,description="Quantity of the ingredient")
    unit: Unit

    @field_validator("canonical")
    @classmethod
    def normalize(cls,v: str)-> str:
        return " ".join(v.strip().lower().split())


class Recipe(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$", description="kebab-case slug")
    title: str = Field(...,min_length=2)
    servings: int = Field(...,ge=1,le=12)
    tags: list[str] = Field(default_factory=list)
    ingredients: list[Ingredient] = Field(...,min_length=1)
    steps: list[str] = Field(...,min_length=1)


class Match(BaseModel):
    """Week 7+ : Ingredient match with product."""

    model_config = ConfigDict(extra="forbid")

    canonical: str
    product_id: str | None = Field(None,description="None(If no match)")
    confidence: float = Field(...,ge=0,le=1)
    package_size: float | None = Field(None,gt=0)
    package_unit: Unit | None = None
    reason: str | None = Field(None,description="LLMs small reason for debug")



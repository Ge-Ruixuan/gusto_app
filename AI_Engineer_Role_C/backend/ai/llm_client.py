from __future__ import annotations

import json
import os
import re
from typing import Callable,TypeVar

from pydantic import BaseModel, ValidationError

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

T = TypeVar("T",bound=BaseModel)

MAX_RETRIES = 2
DEFAULT_MODEL = os.getenv("LLM_MODEL","claude-haiku-5-5")

class LLMOutputError(RuntimeError):
    """Raised when the LLM output is invalid or cannot be parsed."""

def _call_model(system:str, user:str, model: str = DEFAULT_MODEL) -> str:
    """"Returns raw text output from the LLM model."""
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=model,
        max_tokens = 2000,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


def _extract_json(text:str) -> str:
    """"Extracts the json block or body"""
    fanced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fanced:
        return fanced.group(1)
    start,end = text.find("{"),text.rfind("}")
    return text[start : end + 1] if start != -1 and end > start else text

def generate(prompt:str, schema:type[T], *, model:str = DEFAULT_MODEL, call: Callable[[str,str],str] | None=None,) -> T:
    """"Sends the prompt to model and varifies answer with 'schema' 
    'call': In testing, injecting to fake model (before going the real API)

    """
    call = call or (lambda s,u: _call_model(s,u,model))
    system = (
        "Returns only vaid JSON, don't write explanation. JSON must fulfill the schema:\n"
        + json.dumps(schema.model_json_schema(), ensure_ascii=False)
    )
    user = prompt
    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES):
        raw = call(system,user)
        try:
            return schema.model_validate_json(_extract_json(raw))
        except ValidationError as e:
            last_error = e
            user = (
                f"{prompt}\n\nResponse before invalid:\n{raw}\n\n"
                f"Error:\n{e}\n\nCorrect and return only JSON."
            )
    raise LLMOutputError(f"{MAX_RETRIES + 1} attempts failed: {last_error}")

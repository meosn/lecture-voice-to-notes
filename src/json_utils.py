"""
Helpers for parsing local model JSON output.
"""

import ast
import json
import re


def extract_json(text: str):
    """Extract and parse JSON from model output with common local-model fixes."""
    candidates = _json_candidates(text)
    last_error = None

    for candidate in candidates:
        for repaired in _repair_candidates(candidate):
            try:
                return json.loads(repaired)
            except json.JSONDecodeError as error:
                last_error = error
            try:
                return ast.literal_eval(repaired)
            except (ValueError, SyntaxError) as error:
                last_error = error

    raise ValueError(f"Could not parse JSON from model response: {last_error}")


def _json_candidates(text: str) -> list:
    candidates = []
    match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if match:
        candidates.append(match.group(1).strip())

    array_start = text.find("[")
    array_end = text.rfind("]")
    if array_start != -1 and array_end != -1 and array_end > array_start:
        candidates.append(text[array_start:array_end + 1].strip())

    object_start = text.find("{")
    object_end = text.rfind("}")
    if object_start != -1 and object_end != -1 and object_end > object_start:
        candidates.append(text[object_start:object_end + 1].strip())

    candidates.append(text.strip())
    return [candidate for index, candidate in enumerate(candidates) if candidate and candidate not in candidates[:index]]


def _repair_candidates(text: str) -> list:
    repaired = _escape_control_chars_in_strings(text)
    return [
        text,
        repaired,
        repaired.replace(",\n]", "\n]").replace(",\n}", "\n}"),
    ]


def _escape_control_chars_in_strings(text: str) -> str:
    output = []
    in_string = False
    escaped = False

    for char in text:
        if in_string:
            if escaped:
                output.append(char)
                escaped = False
            elif char == "\\":
                output.append(char)
                escaped = True
            elif char == '"':
                output.append(char)
                in_string = False
            elif char == "\n":
                output.append("\\n")
            elif char == "\r":
                output.append("\\r")
            elif char == "\t":
                output.append("\\t")
            else:
                output.append(char)
        else:
            output.append(char)
            if char == '"':
                in_string = True

    return "".join(output)

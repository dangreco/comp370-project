import re
from functools import reduce
from bs4 import Tag
from typing import Any

CHARACTER_BLACKLIST = [
    "",
    "THE END",
    "ALL",
    "WOMAN",
    "MAN",
    "BOY",
]

CHARACTER_FILTERS = [
    lambda x: x.startswith("INT."),
    lambda x: x.startswith("INT."),
    lambda x: "'S" in x,
]

CHARACTER_JOINS = [" AND ", "&", "+", "/", ","]


def sub(pat: str, rep: str):
    return lambda s: re.sub(pat, rep, s)


def clean_dialogue(s: str) -> str:
    return reduce(
        lambda acc, f: f(acc),
        [
            sub(r"\(.*\)", ""),  # actions/thoughts
            sub(r"\s+", " "),  # extra whitespace
        ],
        s,
    ).strip()


def is_character(title: str, node: Any) -> bool:
    # Characters are `b` tags
    if not isinstance(node, Tag) or node.name != "b":
        return False

    # Check blacklist
    name = node.text.strip()
    if name in CHARACTER_BLACKLIST + [title.upper()]:
        return False

    # Check filters
    for f in CHARACTER_FILTERS:
        if f(name):
            return False

    # Check previous sibling -- should be whitespace
    previous = node.previous_sibling
    if not isinstance(previous, Tag) or previous.text.strip():
        return False

    return True


def split_characters(s: str) -> list[str]:
    for join in CHARACTER_JOINS:
        s = s.replace(join, "&")

    characters = s.split("&")
    characters = [character.strip() for character in characters if character.strip()]

    return characters

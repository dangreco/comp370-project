import re
from functools import reduce
from bs4 import Tag
from bs4 import NavigableString
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


def clean_dialogue(s: str) -> str:
    return reduce(
        lambda acc, f: f(acc),
        [
            lambda x: re.sub(r"\(.*?\)", "", x),  # non-greedy parentheses removal
            lambda x: re.sub(r"\s+", " ", x),  # extra whitespace
        ],
        s,
    ).strip()


def extract_dialogue(title: str, siblings: Any) -> str:
    parts = []
    for sibling in siblings:
        if is_character(title, sibling):
            break
        elif isinstance(sibling, NavigableString):
            parts.append(sibling.strip())
    dialogue = " ".join(parts)
    dialogue = clean_dialogue(dialogue)
    return dialogue


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

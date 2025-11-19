"""
Utility functions for parsing and cleaning script text.

This module provides helper functions to clean dialogue text and
identify character names in the HTML structure of IMSDB scripts.
"""

import re
from bs4 import BeautifulSoup
from functools import reduce


def clean(s: str) -> str:
    """
    Clean and normalize dialogue text from scripts.

    Applies a series of transformations to remove stage directions,
    normalize whitespace, and fix punctuation issues.

    Args:
        s: Raw dialogue text from the script

    Returns:
        Cleaned and normalized dialogue text
    """
    return reduce(
        lambda s, f: f(s),
        [
            lambda s: re.sub(r"\s+", " ", s),  # remove whitespace
            lambda s: re.sub(r"\(.*\)", "", s),  # remove actions
            lambda s: re.sub(r"[:;-] ([,.])", r"\g<1>", s),  # remove weirdness
            lambda s: re.sub(
                r"(\.\.\..)", lambda m: m.group(0).lower(), s
            ),  # fix ellipsis
            lambda s: s.strip(),
        ],
        s,
    )


def is_character(title: str, element: BeautifulSoup):
    """
    Determine if a BeautifulSoup element represents a character name.

    Character names in IMSDB scripts follow specific formatting rules:
    they appear in bold, all uppercase, with an empty bold tag before them.

    Args:
        title: The episode title (used to filter out title text)
        element: BeautifulSoup element to check

    Returns:
        True if the element represents a character name, False otherwise
    """
    if not element:
        return False

    previous = element.previous_sibling

    p_text = previous.text.strip() if previous else ""
    c_text = element.text.strip()

    return all(
        [
            previous.name == "b",
            p_text == "",
            element.name == "b",
            c_text.isupper(),
            "(" not in c_text,
            ")" not in c_text,
            "!" not in c_text,
            c_text not in ["", title.upper(), "THE END"],
        ]
    )

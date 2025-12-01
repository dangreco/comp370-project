import re
import jellyfish
from typing import Optional
from typing import Callable
from functools import lru_cache
from dataclasses import dataclass

from comp370.nlp import NLTK
from comp370.client.fandom.models import Character as FCharacter
from .constants import COMMON_NAMES, TITLES, SUFFIXES


BLACKLIST: list[Callable[[str], bool]] = [
    lambda name: "standup" in name,
    lambda name: any(map(lambda c: c.isnumeric(), name)),
    lambda name: any(map(lambda c: c in name, ["#"])),
    lambda name: "ext." in name,
    lambda name: "int." in name,
    lambda name: "inside " in name,
    lambda name: "outside " in name,
    lambda name: "apartment" in name,
]


@dataclass
class Name:
    title: Optional[str]
    first: Optional[str]
    middle: Optional[list[str]]
    last: Optional[str]
    suffix: Optional[str]

    def similarity(self, other: "Name") -> float:
        """
        Calculate similarity score between two names (0-1, higher is better).
        Uses Jaro-Winkler for better name matching.
        """
        scores = []

        match (self.title, other.title):
            case (None, None):
                ()
            case (None, _):
                scores.append(0)
            case (_, None):
                scores.append(0)
            case (a, b):
                scores.append(1 if a == b else 0)

        match (self.suffix, other.suffix):
            case (None, None):
                ()
            case (None, _):
                scores.append(0)
            case (_, None):
                scores.append(0)
            case (a, b):
                scores.append(1 if a == b else 0)

        if self.first and other.first:
            scores.append(jellyfish.jaro_winkler_similarity(self.first, other.first))

        if self.last and other.last:
            scores.append(jellyfish.jaro_winkler_similarity(self.last, other.last))

        if self.middle and other.middle:
            scores_ = [
                jellyfish.jaro_winkler_similarity(a, b)
                for a, b in zip(self.middle, other.middle)
            ]
            scores.append(sum(scores_) / len(scores_))

        return sum(scores) / len(scores) if scores else 0.0

    def phonetic_match(self, other: "Name") -> bool:
        """Check if names sound similar using phonetic encoding."""
        if self.first and other.first:
            if jellyfish.metaphone(self.first) == jellyfish.metaphone(other.first):
                return True

        if self.last and other.last:
            if jellyfish.metaphone(self.last) == jellyfish.metaphone(other.last):
                return True

        return False

    @staticmethod
    @lru_cache(maxsize=None)
    def parse(name: str) -> Optional["Name"]:
        # Clean the name
        name = name.lower().strip()
        name = re.sub(r"\s+", " ", name)  # normalize whitespace
        name = name.replace("-", " ")
        name = re.sub(
            r"[^A-Za-z\s\.]",
            "",
            name,
            flags=re.IGNORECASE,
        )  # remove special chars

        # Check for title
        title = None
        for pat in TITLES:
            match = re.match(rf"^{pat}\.?\s+", name, re.IGNORECASE)
            if match:
                title = pat
                name = name[match.end() :].strip()
                break

        # Check for suffix
        suffix = None
        for pat in SUFFIXES:
            match = re.search(rf"\s+{pat}\.?\s*$", name, re.IGNORECASE)
            if match:
                suffix = pat
                name = name[: match.start()].strip()
                break

        # Remove non-name tags
        tokens = NLTK.word_tokenize(name)
        tags = list(NLTK.pos_tag(tokens))
        ok = ["NN", "NNP", "JJ"]

        # Remove junk
        while tags:
            if tags[0][1] in ok:
                break
            tags.pop(0)

        # Re-do tags
        tags = list(NLTK.pos_tag(list(map(lambda x: x[0], tags))))
        possible = []
        for word, tag in tags:
            if tag in ok:
                possible.append(word)
            else:
                break

        # Get clean name
        name = " ".join(possible)

        # Split into parts
        parts = [p for p in name.split() if p]  # filter empty strings

        if not parts:
            return None

        first = parts[0] if parts else None
        middle = parts[1:-1] if len(parts) > 2 else None
        last = parts[-1] if len(parts) > 1 else None

        return Name(
            title=title,
            first=first,
            middle=middle,
            last=last,
            suffix=suffix,
        )


class Resolver:
    def __init__(
        self,
        characters: list[FCharacter],
        popularity: dict[str, int],
    ):
        self.characters = {character.name: character for character in characters}
        self.popularity = popularity
        self.lut_exact = {name.lower(): char for name, char in self.characters.items()}
        self.lut_first = {}
        self.lut_last = {}
        for name, char in self.characters.items():
            parsed = Name.parse(name)
            if parsed:
                if parsed.first:
                    key = parsed.first.lower()
                    if key in self.lut_first:
                        self.lut_first[key] = None
                    elif key in self.lut_last:
                        self.lut_first[key] = None
                        self.lut_last[key] = None
                    else:
                        self.lut_first[key] = char
                if parsed.last:
                    key = parsed.last.lower()
                    if key in self.lut_last:
                        self.lut_last[key] = None
                    elif key in self.lut_first:
                        self.lut_first[key] = None
                        self.lut_last[key] = None
                    else:
                        self.lut_last[key] = char

    @lru_cache(maxsize=None)
    def resolve(self, name: str) -> Optional[tuple[float, FCharacter]]:
        name = name.lower().strip()
        if any(map(lambda f: f(name), BLACKLIST)):
            return None

        # Check for exact match first
        if name in self.lut_exact:
            return 1.0, self.lut_exact[name]

        # Check common names mapping
        if name in COMMON_NAMES:
            mapped_name = COMMON_NAMES[name]
            if mapped_name.lower() in self.lut_exact:
                return 1.0, self.lut_exact[mapped_name.lower()]

        # Parse the name
        this = Name.parse(name)
        if this is None:
            return None

        # Try single-name lookup
        if this.first and not this.last:
            if this.first in self.lut_first and self.lut_first[this.first] is not None:
                return 1.0, self.lut_first[this.first]
            if this.first in self.lut_last and self.lut_last[this.first] is not None:
                return 1.0, self.lut_last[this.first]

        # Find best match using similarity scores
        ranking = []
        for character in self.characters.values():
            other = Name.parse(character.name)
            if other is None:
                continue

            # Calculate similarity
            similarity = this.similarity(other)

            # Boost phonetic match
            if this.phonetic_match(other):
                similarity = min(1.0, similarity + 0.1)

            # Append similarity and character to ranking
            ranking.append((similarity, self.popularity[character.path], character))

        if not ranking:
            return None

        # Sort by similarity (desc), popularity (asc)
        ranking.sort(key=lambda x: (-x[0], x[1]))
        best_similarity, _, best_character = ranking[0]

        if best_similarity < 0.95:
            return None

        return None

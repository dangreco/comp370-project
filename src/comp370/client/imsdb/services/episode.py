import re

from .__service__ import Service
from ..models import Line
from ..utils import extract_dialogue, is_character, split_characters


class EpisodeService(Service):
    def get(self, title: str) -> list[Line]:
        path = f"/transcripts/Seinfeld-{title.replace(' ', '-')}.html"
        soup, cached = self.session.get(path)

        pre = soup.find("pre")
        assert pre is not None, "No pre element found"

        lines: list[Line] = []
        for node in pre.descendants:
            if is_character(title, node):
                number = len(lines) + 1
                dialogue = extract_dialogue(title, node.next_siblings)

                character = node.text.strip()
                for character in split_characters(character):
                    # Sometimes scripts refer back to previous character by one letter
                    if len(character) == 1:
                        line = next(
                            filter(lambda x: x.character[0] == character, lines[::-1]),
                            None,
                        )
                        if not line:
                            continue

                        character = line.character  # type:ignore

                    dialogue = re.sub(r"\(.*\)", "", dialogue)
                    dialogue = re.sub(r"\s+", " ", dialogue)

                    if dialogue == "":
                        continue

                    lines.append(
                        Line(
                            number=number,
                            character=character,
                            dialogue=dialogue,
                        )
                    )

        return lines

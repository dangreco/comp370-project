import os

import spacy


class SpaCy:
    dir: str | None

    @staticmethod
    def setup():
        SpaCy.dir = os.environ.get("DIR_SPACY", None)

    @staticmethod
    def load(model: str) -> spacy.Language:
        SpaCy.setup()
        path = f"{SpaCy.dir}/{model}" if SpaCy.dir is not None else model
        return spacy.load(path)

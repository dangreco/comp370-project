import os
from pathlib import Path

import nltk


class NLTK:
    @staticmethod
    def setup():
        dir = os.environ.get("DIR_NLTK", None)
        if dir is not None:
            for child in Path(dir).iterdir():
                if child.is_dir():
                    nltk.data.path.append(str(child))

    @staticmethod
    def word_tokenize(*args, **kwargs):
        NLTK.setup()
        return nltk.word_tokenize(*args, **kwargs)

    @staticmethod
    def pos_tag(*args, **kwargs):
        NLTK.setup()
        return nltk.pos_tag(*args, **kwargs)

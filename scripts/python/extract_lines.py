import signal
import argparse
import pandas as pd
from sqlalchemy import func
from typing import Optional


from comp370.db import Client as Db
from comp370.db import Season
from comp370.db import Episode
from comp370.db import Character
from comp370.db import Line

signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def extract(character: str, length: int, n: Optional[int] = None) -> pd.DataFrame:
    with Db().session() as db:
        query = (
            db.query(
                Season.number.label("season"),
                Episode.number.label("episode"),
                Line.number.label("number"),
                Line.dialogue.label("dialogue"),
            )
            .select_from(Character)
            .join(Line, Line.character_id == Character.id)
            .join(Episode, Episode.id == Line.episode_id)
            .join(Season, Season.id == Episode.season_id)
            .filter(Character.name == character)
            .filter(func.length(Line.dialogue) >= length)
            .order_by(Season.number.asc(), Episode.number.asc(), Line.number.asc())
        )

        result = query.all()
        df = pd.DataFrame(result, columns=["season", "episode", "number", "dialogue"])

        if n is None:
            return df

        if n <= len(df):
            return df.sample(n=n, replace=False, random_state=None)

        return df.sample(frac=1, random_state=None)


def main():
    parser = argparse.ArgumentParser(description="Extract lines of dialogue")
    parser.add_argument("character", help="Character name")
    parser.add_argument(
        "-l",
        "--length",
        type=int,
        default=15,
        help="Minimum dialogue length for a character",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output file name",
    )
    parser.add_argument(
        "-n",
        "--num-lines",
        type=int,
        default=None,
        help="Number of lines to sample",
    )
    args = parser.parse_args()

    df = extract(args.character, args.length, args.num_lines)
    if args.output:
        df.to_csv(args.output, index=False, sep="\t")
    else:
        print(df.to_string(index=False))


if __name__ == "__main__":
    main()

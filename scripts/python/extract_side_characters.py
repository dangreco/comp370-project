import signal
import argparse
import pandas as pd
from sqlalchemy import func

from comp370.db import Client as Db
from comp370.db import Character
from comp370.db import Line

# Main characters
EXCLUDE = [
    "Jerry Seinfeld",
    "George Costanza",
    "Elaine Benes",
    "Cosmo Kramer",
]


signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def extract(n: int, length: int) -> pd.DataFrame:
    with Db().session() as db:
        query = (
            db.query(
                Character.name.label("character"),
                func.count(Line.id).label("lines"),
            )
            .join(Line, Character.id == Line.character_id)
            .filter(func.length(Line.dialogue) >= length)
            .filter(Character.name.notin_(EXCLUDE))
            .group_by(Character.id, Character.name)
            .order_by(func.count(Line.id).desc())
            .limit(n)
        )

        result = query.all()
        return pd.DataFrame(result, columns=["character", "lines"])


def main():
    parser = argparse.ArgumentParser(description="Extract side characters")
    parser.add_argument(
        "-n",
        "--num-characters",
        type=int,
        default=3,
        help="Number of side characters to extract",
    )
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
    args = parser.parse_args()

    df = extract(args.num_characters, args.length)
    if args.output:
        df.to_csv(args.output, index=False, sep="\t")
    else:
        print(df.to_string(index=False))


if __name__ == "__main__":
    main()

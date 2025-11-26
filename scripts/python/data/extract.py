import argparse
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from comp370.constants import DIR_DATA
from comp370.db import Client as Db
from comp370.db import Season
from comp370.db import Episode
from comp370.db import Character
from comp370.db import Line
from comp370.db.tools.character import CharacterTool
from comp370.db.tools.character import CharacterType


def extract(
    db: Session,
    character: Character,
    minimum_length: str,
) -> pd.DataFrame:
    query = (
        db.query(
            Line.id.label("id"),
            Season.number.label("season"),
            Episode.number.label("episode"),
            Line.number.label("number"),
            Line.dialogue.label("dialogue"),
        )
        .select_from(Character)
        .join(Line, Line.character_id == Character.id)
        .join(Episode, Episode.id == Line.episode_id)
        .join(Season, Season.id == Episode.season_id)
        .filter(Character.id == character.id)
        .filter(func.length(Line.dialogue) >= minimum_length)
        .order_by(Season.number.asc(), Episode.number.asc(), Line.number.asc())
    )

    result = query.all()
    df = pd.DataFrame(
        result,
        columns=["id", "season", "episode", "number", "dialogue"],
    )

    return df


def main():
    parser = argparse.ArgumentParser(description="Extract lines of dialogue")
    parser.add_argument(
        "-n",
        "--num-characters",
        type=int,
        default=5,
        help="Minimum dialogue length for a character",
    )
    parser.add_argument(
        "-l",
        "--minimum-length",
        type=int,
        default=15,
        help="Minimum dialogue length for a character",
    )
    args = parser.parse_args()

    print("== EXTRACTING")
    with Db().session() as db:
        side = CharacterTool(db).get_characters(CharacterType.SIDE)
        ranked = CharacterTool(db).sort_characters_by_lines(side)

        if len(ranked) < args.num_characters:
            print(
                f"Warning: only found {len(ranked)} side characters, "
                f"less than the requested {args.num_characters}"
            )

        slugs = []
        for character, _ in ranked[: args.num_characters]:
            df = extract(db, character, args.minimum_length)
            slug = character.name.replace(" ", "_").lower()
            slugs.append(slug)
            output_file = DIR_DATA / "lines" / "extracted" / f"lines.{slug}.tsv"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_file, index=False, sep="\t")

        output_file = DIR_DATA / "characters.side.tsv"
        pd.DataFrame(slugs, columns=["slug"]).to_csv(output_file, index=False, sep="\t")


if __name__ == "__main__":
    main()

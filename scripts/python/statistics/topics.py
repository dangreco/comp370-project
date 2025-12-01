from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.progress import BarColumn
from rich.progress import TaskProgressColumn
from rich.progress import TimeElapsedColumn
from rich.progress import TimeRemainingColumn
import pandas as pd
from sqlalchemy import select
from sqlalchemy import func

from comp370.db import Client as Db
from comp370.db.models import Character
from comp370.db.models import Line
from comp370.db.models import Season
from comp370.db.models import Episode
from comp370.constants import DIR_DATA


def compute_topic_ratios(df_annotations, characters):
    """
    Compute per-season and overall topic ratios for each character.

    Args:
        df_annotations: DataFrame with columns: character, season_number, category (and others)
        characters: dict of character names
    """

    # Filter to only side characters
    df = df_annotations[df_annotations["character"].isin(characters.keys())].copy()

    # Get total lines per character per season from DB
    with Db().session() as db:
        stmt = (
            select(Character.name, Season.number, func.count(Line.id))
            .join(Line)
            .join(Line.episode)
            .join(Episode.season)
            .where(Character.name.in_(characters.keys()))
            .group_by(Character.id, Season.number)
        )

        season_totals = {}
        for char_name, season_num, count in db.execute(stmt):
            season_totals[(char_name, season_num)] = count

    # Get all unique categories/topics
    topics = df["category"].dropna().unique()

    results = []

    # Per-season topic ratios
    for char_name in characters.keys():
        char_df = df[df["character"] == char_name]

        if len(char_df) == 0:
            continue

        # Get unique seasons this character appears in
        seasons = sorted(char_df["season_number"].dropna().unique())

        for season in seasons:
            season_df = char_df[char_df["season_number"] == season]
            total_lines = season_totals.get((char_name, int(season)), 0)

            if total_lines == 0:
                continue

            for topic in topics:
                if topic in ["Miscellaneous", "UNKNOWN"]:
                    continue

                # Count lines with this topic/category
                topic_lines = len(season_df[season_df["category"] == topic])
                ratio = topic_lines / total_lines if total_lines > 0 else 0

                results.append(
                    {
                        "character": char_name,
                        "season": int(season),
                        "topic": topic,
                        "topic_lines": topic_lines,
                        "total_lines": total_lines,
                        "ratio": ratio,
                        "scope": "season",
                    }
                )

    # Overall topic ratios
    for char_name in characters.keys():
        char_df = df[df["character"] == char_name]
        total_lines = characters[char_name]

        if total_lines == 0:
            continue

        for topic in topics:
            if topic in ["Miscellaneous", "UNKNOWN"]:
                continue
            # Count lines with this topic/category across all seasons
            topic_lines = len(char_df[char_df["category"] == topic])
            ratio = topic_lines / total_lines if total_lines > 0 else 0

            results.append(
                {
                    "character": char_name,
                    "season": "overall",
                    "topic": topic,
                    "topic_lines": topic_lines,
                    "total_lines": total_lines,
                    "ratio": ratio,
                    "scope": "overall",
                }
            )

    df_results = pd.DataFrame(results)
    df_results["season_sort"] = df_results["season"].apply(
        lambda x: 999 if x == "overall" else int(x)
    )
    df_results = df_results.sort_values(["character", "season_sort", "topic"]).drop(
        "season_sort", axis=1
    )
    return df_results


def main():
    # Get side characters
    df_chars = pd.read_csv(DIR_DATA / "characters.side.tsv", sep="\t")
    characters = {
        " ".join(part.capitalize() for part in slug.split("_")): 0
        for slug in df_chars["slug"]
    }

    # Count lines per character in DB
    with Db().session() as db:
        # Join Line -> Character, filter by characters in your set
        stmt = (
            select(Character.name, func.count(Line.id))
            .join(Line)
            .where(Character.name.in_(characters.keys()))
            .group_by(Character.id)
        )
        for name, count in db.execute(stmt):
            characters[name] = count

    df_in = pd.read_csv(DIR_DATA / "annotations" / "annotations.derived.csv")
    total = len(df_in)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    ) as bar:
        step = bar.add_task("Getting dialogue...", total=total)
        with Db().session() as db:
            for idx, row in df_in.iterrows():
                line = (
                    db.execute(
                        (
                            select(Line)
                            .join(Line.episode)
                            .join(Episode.season)
                            .where(
                                Season.number == row["season_number"],
                                Episode.number == row["episode_number"],
                                Line.number == row["line_number"],
                            )
                        )
                    )
                    .scalars()
                    .first()
                )

                if line:
                    df_in.at[idx, "dialogue"] = line.dialogue
                    df_in.at[idx, "character"] = line.character.name

                bar.update(step, advance=1)

    ratios = compute_topic_ratios(df_in, characters)
    ratios.to_csv(DIR_DATA / "statistics" / "statistics.topics.csv", index=False)


if __name__ == "__main__":
    main()

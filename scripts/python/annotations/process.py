import os
import pandas as pd
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.progress import BarColumn
from rich.progress import TaskProgressColumn
from rich.progress import TimeElapsedColumn
from rich.progress import TimeRemainingColumn

from comp370.constants import DIR_DATA

WEIGHTS = {
    "me@dangre.co": 1.0,
    "kejun.fang@mail.mcgill.ca": 1.0,
    "denis.tsariov@mail.mcgill.ca": 1.0,
    "gpt-oss@dangre.co": 0.75,
    "minimax-m2@dangre.co": 0.5,
}


def consensus(rows) -> str:
    # Keep only the most recent annotation per email
    rows = (
        rows.sort_values("date")  # oldest → newest
        .groupby("email")
        .tail(1)  # most recent per annotator
    )

    emails = rows["email"]

    # 1. Separate human vs all annotators
    human_mask = emails.isin(["me@dangre.co", "kejun.fang@mail.mcgill.ca"])
    human_rows = rows[human_mask]

    # Count human votes
    human_counts = human_rows["category"].value_counts()

    if len(human_counts) == 0:
        return weighted_consensus(rows)

    # 2. If humans produce a clear winner
    if len(human_counts) == 1:
        return human_counts.index[0]

    # 3. Human tie
    top_human = human_counts.max()
    tied = human_counts[human_counts == top_human]

    if len(tied) == 1:
        return tied.index[0]

    return weighted_consensus(rows)


def weighted_consensus(rows) -> str:
    # rows already reduced to the most recent per email
    weighted = rows.groupby("category")["email"].apply(lambda s: s.map(WEIGHTS).sum())

    if len(weighted) == 0:
        return "UNKNOWN"

    max_w = weighted.max()
    winners = weighted[weighted == max_w].index.tolist()

    if len(winners) == 1:
        return winners[0]

    return "UNKNOWN"


def main():
    df_in = pd.read_csv(DIR_DATA / "annotations" / "annotations.all.csv")
    df_out = pd.DataFrame(
        columns=[
            "season_number",
            "episode_number",
            "line_number",
            "category",
        ]
    )

    total = len(df_in)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    ) as bar:
        step = bar.add_task("Processing...", total=total)

        grouped = df_in.groupby(["season_number", "episode_number", "line_number"])
        for (season, episode, line), rows in grouped:  # type: ignore
            df_out.loc[len(df_out)] = [season, episode, line, consensus(rows)]
            bar.update(step, advance=len(rows))

    os.makedirs(DIR_DATA / "annotations", exist_ok=True)
    df_out.to_csv(DIR_DATA / "annotations" / "annotations.derived.csv", index=False)


if __name__ == "__main__":
    main()

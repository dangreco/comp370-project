import os
import sys
import datetime
import pandas as pd
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.progress import BarColumn
from rich.progress import TaskProgressColumn
from rich.progress import TimeElapsedColumn
from rich.progress import TimeRemainingColumn
from dotenv import load_dotenv

from comp370.constants import DIR_DATA
from comp370.client.label_studio import Client


def main():
    if "LABEL_STUDIO_URL" not in os.environ:
        print("LABEL_STUDIO_URL not set")
        sys.exit(1)
    if "LABEL_STUDIO_API_KEY" not in os.environ:
        print("LABEL_STUDIO_API_KEY not set")
        sys.exit(1)

    base_url = os.environ["LABEL_STUDIO_URL"]
    api_key = os.environ["LABEL_STUDIO_API_KEY"]
    client = Client(base_url, api_key)

    df = pd.DataFrame(
        columns=[
            "season_number",
            "episode_number",
            "line_number",
            "date",
            "email",
            "category",
        ]
    )

    total = client.get_num_tasks()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    ) as bar:
        step = bar.add_task("Retrieving...", total=total)

        for task in client.get_tasks():
            season: int = task.data["season"]  # type:ignore
            episode: int = task.data["episode"]  # type:ignore
            line: int = task.data["number"]  # type:ignore

            for annotation in task.annotations:
                if not len(annotation["result"]):
                    print(f"Skipping {task.id}:{annotation['id']}")
                    continue

                date: datetime.datetime = annotation["updated_at"]
                email: str = annotation["created_username"].split(",")[0].strip()
                category: str = annotation["result"][0]["value"]["choices"][0]

                df.loc[len(df)] = [season, episode, line, date, email, category]

            bar.update(step, advance=1)

    os.makedirs(DIR_DATA / "annotations", exist_ok=True)
    df.to_csv(DIR_DATA / "annotations" / "annotations.all.csv", index=False)


if __name__ == "__main__":
    load_dotenv()
    main()

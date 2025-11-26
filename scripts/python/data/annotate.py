import os
import sys
import argparse
import pandas as pd
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.progress import BarColumn
from rich.progress import TaskProgressColumn
from dotenv import load_dotenv
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from typing import Optional
from typing import Callable

from comp370.constants import DIR_DATA
from comp370.annotator.codebooks import CODEBOOKS
from comp370.annotator import Annotator
from comp370.annotator.annotators import HumanAnnotator
from comp370.annotator.annotators import OllamaAnnotator
from comp370.db import Client as Db
from comp370.db.models import Line

load_dotenv()


def annotate(
    annotator: Annotator,
    df: pd.DataFrame,
    tick: Optional[Callable] = None,
) -> pd.DataFrame:
    df = df.copy(deep=True)

    with Db().session() as session:
        for row in df.itertuples():
            line = session.execute(
                select(Line)
                .options(joinedload(Line.character))
                .filter(Line.id == row.id)  # type: ignore
            ).scalar_one()
            category = annotator.annotate(line)
            df.at[row.Index, "category"] = category  # type: ignore

            if tick is not None:
                tick()

    return df


def main():
    parser = argparse.ArgumentParser(description="Annotate lines of dialogue")
    parser.add_argument(
        "-a",
        "--annotator",
        type=str,
        default="human",
        help="Annotator to use",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default=None,
        help="Annotator model to use (LLM only)",
    )
    parser.add_argument(
        "-c",
        "--codebook",
        type=str,
        default=None,
        help="Codebook to use for annotation",
    )
    args = parser.parse_args()

    # Check codebook
    if args.codebook is None:
        print("--codebook must be specified")
        sys.exit(1)

    if args.codebook not in CODEBOOKS:
        print(f"Codebook {args.codebook} not found")
        sys.exit(1)

    # Check annotator
    match args.annotator:
        case "human":
            annotator = HumanAnnotator(codebook=CODEBOOKS[args.codebook])
        case "ollama":
            if "OLLAMA_API_KEY" not in os.environ:
                print("OLLAMA_API_KEY not set")
                sys.exit(1)

            api_key = os.environ["OLLAMA_API_KEY"]

            tmp = OllamaAnnotator(api_key)
            models = tmp.models()

            if args.model is None:
                print("No model specified!")
                print("Available models:")
                for model in models:
                    print(f" - {model}")
                sys.exit(1)

            if args.model not in models:
                print(f"Model {args.model} not found!")
                print("Available models:")
                for model in models:
                    print(f" - {model}")
                sys.exit(1)

            annotator = OllamaAnnotator(
                api_key,
                model=args.model,
                codebook=CODEBOOKS[args.codebook],
            )
        case _:
            raise ValueError(f"Annotator {args.annotator} not implemented")

    print("== ANNOTATING")
    slugs = pd.read_csv(DIR_DATA / "characters.side.tsv", sep="\t")["slug"].tolist()
    for slug in slugs:
        df = pd.read_csv(DIR_DATA / "lines" / "sampled" / f"lines.{slug}.tsv", sep="\t")
        if len(df) <= 0:
            print(f" - {slug}: No lines found, skipping...")
            continue

        # Annotate data
        if args.annotator == "human":
            df_annotated = annotate(annotator, df)
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
            ) as bar:
                task = bar.add_task(
                    f"Annotating lines.{slug}.tsv...",
                    total=len(df),
                )
                df_annotated = annotate(
                    annotator,
                    df,
                    tick=lambda: bar.update(task, advance=1),
                )

        # Save annotated data
        output_file = (
            DIR_DATA / "lines" / "annotated" / args.annotator / f"lines.{slug}.tsv"
        )
        output_file.parent.mkdir(parents=True, exist_ok=True)
        df_annotated.to_csv(output_file, index=False, sep="\t")

    # Touch anchor file
    anchor_file = DIR_DATA / "lines" / "annotated" / args.annotator / "anchor"
    anchor_file.touch()


if __name__ == "__main__":
    main()

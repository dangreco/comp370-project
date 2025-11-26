import argparse
import pandas as pd

from comp370.constants import DIR_DATA


def main():
    parser = argparse.ArgumentParser(description="Sample lines of dialogue")
    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=5,
        help="Number of lines to sample",
    )
    args = parser.parse_args()

    print("== SAMPLING")
    slugs = pd.read_csv(DIR_DATA / "characters.side.tsv", sep="\t")["slug"].tolist()
    for slug in slugs:
        df = pd.read_csv(
            DIR_DATA / "lines" / "extracted" / f"lines.{slug}.tsv", sep="\t"
        )

        if len(df) <= 0:
            print(f" - {slug}: No lines found, skipping...")
            continue
        elif len(df) < args.num:
            print(f" - {slug}: Only {len(df)} lines found, shuffling...")
            sample = df.sample(n=len(df), random_state=42, replace=False)
        else:
            print(f" - {slug}: Sampling {args.num} lines...")
            sample = df.sample(n=args.num, random_state=42, replace=False)

        output_file = DIR_DATA / "lines" / "sampled" / f"lines.{slug}.tsv"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        sample.to_csv(output_file, index=False, sep="\t")


if __name__ == "__main__":
    main()

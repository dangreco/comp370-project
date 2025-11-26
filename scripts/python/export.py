import argparse

from comp370.annotator.codebooks import codebook_dan

CODEBOOKS = {"dan": codebook_dan}


def main():
    parser = argparse.ArgumentParser(description="Export codebook to markdown")
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file name",
    )
    parser.add_argument(
        "codebook",
        type=str,
        help="Codebook to export",
    )

    args = parser.parse_args()

    if args.codebook not in CODEBOOKS:
        raise ValueError(f"Codebook {args.codebook} not found")

    md = CODEBOOKS[args.codebook].to_markdown()
    if args.output:
        with open(args.output, "w") as f:
            f.write(md)
    else:
        print(md)


if __name__ == "__main__":
    main()

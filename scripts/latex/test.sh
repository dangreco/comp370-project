#!/usr/bin/env bash
set -euo pipefail

# Usage: test.sh <source>
function usage() {
    echo "Usage: test.sh <source>"
    exit 1
}

SRC="$1"

if [ ! -f "$SRC" ]; then
    echo "Error: Source file '$SRC' does not exist."
    usage
fi

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT SIGINT SIGTERM

# Copy source files to temporary directory
DIR_SRC=$(dirname "$SRC")
cp -r "$DIR_SRC"/* "$tmp"

# Build LaTeX document
(cd "$tmp" && latexmk -silent -pdf "$(basename "$SRC")" > /dev/null 2>&1)

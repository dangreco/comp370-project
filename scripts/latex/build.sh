#!/usr/bin/env bash
set -euo pipefail

# Usage: build.sh <source> <build_dir>
function usage() {
    echo "Usage: build.sh <source> <build_dir>"
    exit 1
}

SRC="$1"
DIR_BLD="$2"

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
(cd "$tmp" && latexmk -C "$(basename "$SRC")" && latexmk -f -pdf "$(basename "$SRC")")

# Copy to build directory
mkdir -p "$DIR_BLD"
cp "$tmp/$(basename "$SRC" .tex).pdf" "$DIR_BLD"

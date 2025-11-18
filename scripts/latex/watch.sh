#!/usr/bin/env bash
set -euo pipefail

src="$1"
if [ ! -f "$src" ]; then
    echo "Error: Source file '$src' does not exist."
    exit 1
fi

tmp=$(mktemp -d)
viewers=(zathura okular evince xdg-open open)
pid_viewer=""

# Start latexmk in its own process group
(
    cd "$(dirname "$src")"
    exec latexmk -pdf -pvc -synctex=1 -outdir="$tmp" -view=none "$(basename "$src")"
) &
pid_latex=$!
gid_latex=$(ps -o pgid= "$pid_latex" | tr -d ' ')

cleanup() {
    # Kill the whole latexmk process group
    kill -- "-$gid_latex" 2>/dev/null || true

    # Wait until the entire group is gone
    while kill -0 "$pid_latex" 2>/dev/null; do
        sleep 0.05
    done

    # Kill viewer if running
    if [ -n "$pid_viewer" ]; then
        kill "$pid_viewer" 2>/dev/null || true
        while kill -0 "$pid_viewer" 2>/dev/null; do
            sleep 0.05
        done
    fi

    rm -rf "$tmp"
}
trap cleanup EXIT SIGINT SIGTERM

pdf="$tmp/$(basename "$src" .tex).pdf"
while [ ! -f "$pdf" ]; do
    sleep 0.1
done

for viewer in "${viewers[@]}"; do
    if command -v "$viewer" &>/dev/null; then
        "$viewer" "$pdf" &
        pid_viewer=$!
        break
    fi
done

wait "$pid_latex"

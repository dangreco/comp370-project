#!/usr/bin/env bash
root="$(dirname "$(dirname "$(dirname "$(realpath "$0")")")")"

[ -f "$root/.env" ] && source "$root/.env" 2>/dev/null || true

if [[ -z "$GPG_PRIVATE_KEY_BASE64" ]]; then
    echo "GPG_PRIVATE_KEY_BASE64 is not set"
    exit 1
fi

if [[ -z "$GPG_PASSPHRASE" ]]; then
    echo "GPG_PASSPHRASE is not set"
    exit 1
fi

if [[ -z "$GPG_KEY_ID" ]]; then
    echo "GPG_KEY_ID is not set"
    exit 1
fi

gpg=$(which gpg)

if [[ -z "$gpg" ]]; then
    echo "gpg is not installed"
    exit 1
fi

echo "$GPG_PRIVATE_KEY_BASE64" | base64 -d | gpg --batch --import &>/dev/null

(cd "$root/docs/report/_build" && sha256sum report.en.pdf) > "$root/docs/report/_build/checksums.txt"
gpg --batch --yes \
    --passphrase "$GPG_PASSPHRASE" \
    --local-user "$GPG_KEY_ID" \
    --armor \
    --detach-sign \
    --output "$root/docs/report/_build/report.en.pdf.asc" \
    "$root/docs/report/_build/report.en.pdf"

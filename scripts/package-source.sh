#!/usr/bin/env bash
# Create a clean source archive and matching SHA-256 file beside the project.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="$(basename -- "$ROOT")"
PARENT="$(dirname -- "$ROOT")"
OUT="$PARENT/${PROJECT}-source.zip"
SUM="$OUT.sha256"

command -v zip >/dev/null 2>&1 || { echo "zip is required to package source." >&2; exit 1; }
command -v sha256sum >/dev/null 2>&1 || { echo "sha256sum is required to package source." >&2; exit 1; }
command -v unzip >/dev/null 2>&1 || { echo "unzip is required to verify the source archive." >&2; exit 1; }

rm -f "$OUT" "$SUM"
(
  cd "$PARENT"
  zip -qr "$OUT" "$PROJECT" \
    -x "$PROJECT/.git/*" \
       "$PROJECT/**/__pycache__/*" \
       "$PROJECT/**/*.pyc" \
       "$PROJECT/dist/*" \
       "$PROJECT/.build/*" \
       "$PROJECT/build.log"
)
[[ -s "$OUT" ]] || { echo "Source archive was not created." >&2; exit 1; }
unzip -tq "$OUT"
sha256sum "$OUT" > "$SUM"
sha256sum -c "$SUM"
printf 'Source archive: %s\n' "$OUT"
printf 'Checksum file:  %s\n' "$SUM"
cat "$SUM"

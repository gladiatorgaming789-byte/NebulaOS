#!/usr/bin/env bash
# Verify ISO structure and boot-menu wiring without pretending to boot-test it.
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ISO="${1:-$ROOT/dist/NebulaForge-OS-amd64.iso}"
fail() { printf 'ISO verification failed: %s\n' "$*" >&2; exit 1; }

[[ -s "$ISO" ]] || fail "ISO does not exist or is empty: $ISO"
command -v xorriso >/dev/null 2>&1 || fail "xorriso is required to inspect ISO images."
command -v sha256sum >/dev/null 2>&1 || fail "sha256sum is required."

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

printf 'Inspecting ISO: %s\n' "$ISO"
CONTENTS="$(xorriso -indev "$ISO" -ls /live 2>&1)" || fail "could not list /live contents"
printf '%s\n' "$CONTENTS"
for required in vmlinuz initrd.img filesystem.squashfs; do
  grep -Fq "$required" <<<"$CONTENTS" || fail "missing /live/$required"
done

ELTORITO="$TMP/eltorito.txt"
xorriso -indev "$ISO" -report_el_torito plain >"$ELTORITO" 2>&1 || fail "could not read El Torito boot metadata"
cat "$ELTORITO"
# xorriso reports platform IDs (0x00 for BIOS, 0xef for EFI) in its plain
# El Torito report. Accept common textual labels as well as those IDs.
grep -Eiq 'BIOS|platform.*0x00|Platform.*0x00' "$ELTORITO" || fail "no BIOS El Torito boot entry was reported"
grep -Eiq 'UEFI|EFI|platform.*0xef|Platform.*0xef' "$ELTORITO" || fail "no EFI/UEFI El Torito boot entry was reported"

xorriso -osirrox on -indev "$ISO" -extract /boot/grub/grub.cfg "$TMP/grub.cfg" >/dev/null 2>&1 \
  || fail "could not extract /boot/grub/grub.cfg"
CFG="$TMP/grub.cfg"
for required in \
  'NebulaForge OS (Live)' \
  'NebulaForge OS (Live, safe graphics)' \
  'search --no-floppy --set=root --file /live/filesystem.squashfs' \
  'boot=live components' \
  'linux /live/vmlinuz' \
  'initrd /live/initrd.img' \
  'nomodeset'; do
  grep -Fq "$required" "$CFG" || fail "GRUB configuration is missing: $required"
done

printf 'ISO SHA-256: '
sha256sum "$ISO"
printf 'ISO structural verification passed. This does not prove the image boots in a VM.\n'

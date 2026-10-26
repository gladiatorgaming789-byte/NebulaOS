#!/usr/bin/env bash
# Exercise the ISO verifier's success and failure paths with a deterministic
# fake xorriso. This tests the verifier itself, not a real bootable ISO.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/bin"
printf 'synthetic ISO fixture\n' > "$TMP/fake.iso"
cat > "$TMP/bin/xorriso" <<'MOCK'
#!/usr/bin/env bash
set -Eeuo pipefail
args=" $* "
if [[ "$args" == *" -ls /live "* ]]; then
  printf '%s\n' 'vmlinuz' 'initrd.img' 'filesystem.squashfs' 'filesystem.size'
  exit 0
fi
if [[ "$args" == *" -report_el_torito plain "* ]]; then
  if [[ "${MOCK_MISSING_UEFI:-0}" == 1 ]]; then
    printf '%s\n' 'El Torito boot img : 2 BIOS'
  else
    printf '%s\n' 'El Torito boot img : 1 UEFI' 'El Torito boot img : 2 BIOS'
  fi
  exit 0
fi
if [[ "$args" == *" -extract /boot/grub/grub.cfg "* ]]; then
  dest="${!#}"
  cat > "$dest" <<'CFG'
set default=0
menuentry "NebulaForge OS (Live)" {
  search --no-floppy --set=root --file /live/filesystem.squashfs
  linux /live/vmlinuz boot=live components quiet splash
  initrd /live/initrd.img
}
menuentry "NebulaForge OS (Live, safe graphics)" {
  search --no-floppy --set=root --file /live/filesystem.squashfs
  linux /live/vmlinuz boot=live components nomodeset
  initrd /live/initrd.img
}
CFG
  exit 0
fi
printf 'Unexpected xorriso invocation: %s\n' "$*" >&2
exit 2
MOCK
chmod +x "$TMP/bin/xorriso"
if PATH="$TMP/bin:$PATH" bash "$ROOT/scripts/verify-iso.sh" "$TMP/fake.iso" >"$TMP/success.log" 2>&1; then
  echo 'ISO verifier accepts a structurally complete fixture.'
else
  cat "$TMP/success.log" >&2
  echo 'ISO verifier rejected the complete fixture.' >&2
  exit 1
fi
if PATH="$TMP/bin:$PATH" MOCK_MISSING_UEFI=1 bash "$ROOT/scripts/verify-iso.sh" "$TMP/fake.iso" >"$TMP/failure.log" 2>&1; then
  echo 'ISO verifier accepted a fixture missing UEFI metadata.' >&2
  exit 1
fi
grep -q 'no EFI/UEFI El Torito boot entry' "$TMP/failure.log"
echo 'ISO verifier rejects a fixture missing UEFI metadata.'

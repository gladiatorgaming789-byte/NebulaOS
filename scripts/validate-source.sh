#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python3 -m unittest discover -s tests -v
python3 -m py_compile forge/forge.py desktop/nebula-shell.py desktop/nebula-files.py desktop/nebula_fileops.py desktop/nebula-settings.py desktop/nebula_settings_backend.py \
  config/includes.chroot/usr/local/bin/forge \
  config/includes.chroot/usr/local/share/nebula/nebula-shell.py \
  config/includes.chroot/usr/local/share/nebula/nebula-files.py \
  config/includes.chroot/usr/local/share/nebula/nebula_fileops.py \
  config/includes.chroot/usr/local/share/nebula/nebula-settings.py \
  config/includes.chroot/usr/local/share/nebula/nebula_settings_backend.py
bash -n scripts/build-iso.sh scripts/verify-iso.sh scripts/package-source.sh tests/test_verify_iso.sh
bash tests/test_verify_iso.sh
# The ISO builder must use the direct bootstrap path, not depend on live-build.
grep -q 'debootstrap --arch=' scripts/build-iso.sh
grep -q 'mksquashfs ' scripts/build-iso.sh
grep -q 'grub-mkrescue ' scripts/build-iso.sh
grep -q 'validate_live_rootfs' scripts/build-iso.sh
grep -q 'chmod 0755 "$ROOTFS/usr/local/bin/nebula-shell"' scripts/build-iso.sh
grep -q 'PROFILE_LISTS=' scripts/build-iso.sh
grep -q 'nebula-gaming.list.chroot' scripts/build-iso.sh
grep -q 'nebula-developer.list.chroot' scripts/build-iso.sh
grep -q 'NEBULA_PROFILE' .github/workflows/build-iso.yml
grep -q 'verify-iso.sh' scripts/build-iso.sh
grep -q 'El Torito' scripts/verify-iso.sh
grep -q 'safe graphics' scripts/verify-iso.sh
grep -q 'sha256sum -c' scripts/package-source.sh
grep -q '^wine
grep -q 'Live root filesystem acceptance checks passed' scripts/build-iso.sh
if grep -Eq '(^|[[:space:]])lb (config|build)([[:space:]]|$)' scripts/build-iso.sh; then
  echo "ISO builder unexpectedly depends on live-build" >&2
  exit 1
fi
sh -n config/hooks/normal/0100-nebula-user.hook.chroot config/includes.chroot/usr/local/bin/nebula-shell \
  config/includes.chroot/usr/local/bin/nebula-files config/includes.chroot/usr/local/bin/nebula-settings \
  config/includes.chroot/usr/local/sbin/nebula-live-user-setup \
  config/includes.chroot/etc/xdg/labwc/autostart
# Packaged copies must match their canonical source files.
cmp -s forge/forge.py config/includes.chroot/usr/local/bin/forge
cmp -s desktop/nebula-shell.py config/includes.chroot/usr/local/share/nebula/nebula-shell.py
cmp -s desktop/nebula-files.py config/includes.chroot/usr/local/share/nebula/nebula-files.py
cmp -s desktop/nebula_fileops.py config/includes.chroot/usr/local/share/nebula/nebula_fileops.py
cmp -s desktop/nebula-settings.py config/includes.chroot/usr/local/share/nebula/nebula-settings.py
cmp -s desktop/nebula_settings_backend.py config/includes.chroot/usr/local/share/nebula/nebula_settings_backend.py
cmp -s desktop/nebula-wallpaper.svg config/includes.chroot/usr/local/share/nebula/nebula-wallpaper.svg
test -L config/includes.chroot/etc/systemd/system/multi-user.target.wants/nebula-live-user.service
# Fail on an accidental placeholder or malformed package-list line.
if grep -nE '^(TODO|FIXME|vulkan-utils)$' config/package-lists/nebula.list.chroot; then
  echo "Invalid placeholder or unsupported package name in package list" >&2
  exit 1
fi
printf '\nSource validation passed. This does not build or boot an ISO.\n'
 config/package-lists/nebula-gaming.list.chroot
grep -q '^build-essential
grep -q 'Live root filesystem acceptance checks passed' scripts/build-iso.sh
if grep -Eq '(^|[[:space:]])lb (config|build)([[:space:]]|$)' scripts/build-iso.sh; then
  echo "ISO builder unexpectedly depends on live-build" >&2
  exit 1
fi
sh -n config/hooks/normal/0100-nebula-user.hook.chroot config/includes.chroot/usr/local/bin/nebula-shell \
  config/includes.chroot/usr/local/bin/nebula-files config/includes.chroot/usr/local/bin/nebula-settings \
  config/includes.chroot/usr/local/sbin/nebula-live-user-setup \
  config/includes.chroot/etc/xdg/labwc/autostart
# Packaged copies must match their canonical source files.
cmp -s forge/forge.py config/includes.chroot/usr/local/bin/forge
cmp -s desktop/nebula-shell.py config/includes.chroot/usr/local/share/nebula/nebula-shell.py
cmp -s desktop/nebula-files.py config/includes.chroot/usr/local/share/nebula/nebula-files.py
cmp -s desktop/nebula_fileops.py config/includes.chroot/usr/local/share/nebula/nebula_fileops.py
cmp -s desktop/nebula-settings.py config/includes.chroot/usr/local/share/nebula/nebula-settings.py
cmp -s desktop/nebula_settings_backend.py config/includes.chroot/usr/local/share/nebula/nebula_settings_backend.py
cmp -s desktop/nebula-wallpaper.svg config/includes.chroot/usr/local/share/nebula/nebula-wallpaper.svg
test -L config/includes.chroot/etc/systemd/system/multi-user.target.wants/nebula-live-user.service
# Fail on an accidental placeholder or malformed package-list line.
if grep -nE '^(TODO|FIXME|vulkan-utils)$' config/package-lists/nebula.list.chroot; then
  echo "Invalid placeholder or unsupported package name in package list" >&2
  exit 1
fi
printf '\nSource validation passed. This does not build or boot an ISO.\n'
 config/package-lists/nebula-developer.list.chroot
grep -q '^labwc
grep -q 'Live root filesystem acceptance checks passed' scripts/build-iso.sh
if grep -Eq '(^|[[:space:]])lb (config|build)([[:space:]]|$)' scripts/build-iso.sh; then
  echo "ISO builder unexpectedly depends on live-build" >&2
  exit 1
fi
sh -n config/hooks/normal/0100-nebula-user.hook.chroot config/includes.chroot/usr/local/bin/nebula-shell \
  config/includes.chroot/usr/local/bin/nebula-files config/includes.chroot/usr/local/bin/nebula-settings \
  config/includes.chroot/usr/local/sbin/nebula-live-user-setup \
  config/includes.chroot/etc/xdg/labwc/autostart
# Packaged copies must match their canonical source files.
cmp -s forge/forge.py config/includes.chroot/usr/local/bin/forge
cmp -s desktop/nebula-shell.py config/includes.chroot/usr/local/share/nebula/nebula-shell.py
cmp -s desktop/nebula-files.py config/includes.chroot/usr/local/share/nebula/nebula-files.py
cmp -s desktop/nebula_fileops.py config/includes.chroot/usr/local/share/nebula/nebula_fileops.py
cmp -s desktop/nebula-settings.py config/includes.chroot/usr/local/share/nebula/nebula-settings.py
cmp -s desktop/nebula_settings_backend.py config/includes.chroot/usr/local/share/nebula/nebula_settings_backend.py
cmp -s desktop/nebula-wallpaper.svg config/includes.chroot/usr/local/share/nebula/nebula-wallpaper.svg
test -L config/includes.chroot/etc/systemd/system/multi-user.target.wants/nebula-live-user.service
# Fail on an accidental placeholder or malformed package-list line.
if grep -nE '^(TODO|FIXME|vulkan-utils)$' config/package-lists/nebula.list.chroot; then
  echo "Invalid placeholder or unsupported package name in package list" >&2
  exit 1
fi
printf '\nSource validation passed. This does not build or boot an ISO.\n'
 config/package-lists/nebula.list.chroot
grep -q 'Live root filesystem acceptance checks passed' scripts/build-iso.sh
if grep -Eq '(^|[[:space:]])lb (config|build)([[:space:]]|$)' scripts/build-iso.sh; then
  echo "ISO builder unexpectedly depends on live-build" >&2
  exit 1
fi
sh -n config/hooks/normal/0100-nebula-user.hook.chroot config/includes.chroot/usr/local/bin/nebula-shell \
  config/includes.chroot/usr/local/bin/nebula-files config/includes.chroot/usr/local/bin/nebula-settings \
  config/includes.chroot/usr/local/sbin/nebula-live-user-setup \
  config/includes.chroot/etc/xdg/labwc/autostart
# Packaged copies must match their canonical source files.
cmp -s forge/forge.py config/includes.chroot/usr/local/bin/forge
cmp -s desktop/nebula-shell.py config/includes.chroot/usr/local/share/nebula/nebula-shell.py
cmp -s desktop/nebula-files.py config/includes.chroot/usr/local/share/nebula/nebula-files.py
cmp -s desktop/nebula_fileops.py config/includes.chroot/usr/local/share/nebula/nebula_fileops.py
cmp -s desktop/nebula-settings.py config/includes.chroot/usr/local/share/nebula/nebula-settings.py
cmp -s desktop/nebula_settings_backend.py config/includes.chroot/usr/local/share/nebula/nebula_settings_backend.py
cmp -s desktop/nebula-wallpaper.svg config/includes.chroot/usr/local/share/nebula/nebula-wallpaper.svg
test -L config/includes.chroot/etc/systemd/system/multi-user.target.wants/nebula-live-user.service
# Fail on an accidental placeholder or malformed package-list line.
if grep -nE '^(TODO|FIXME|vulkan-utils)$' config/package-lists/nebula.list.chroot; then
  echo "Invalid placeholder or unsupported package name in package list" >&2
  exit 1
fi
printf '\nSource validation passed. This does not build or boot an ISO.\n'

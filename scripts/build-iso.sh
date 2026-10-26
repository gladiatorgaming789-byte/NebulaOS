#!/usr/bin/env bash
# Build NebulaForge directly from Debian packages, without live-build.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"
WORK="$ROOT/.build"
ROOTFS="$WORK/rootfs"
ISO_TREE="$WORK/iso"
LOG="$ROOT/build.log"
ARCH=amd64
SUITE=trixie
MIRROR="${NEBULA_DEBIAN_MIRROR:-http://deb.debian.org/debian}"
SECURITY_MIRROR="${NEBULA_DEBIAN_SECURITY_MIRROR:-http://security.debian.org/debian-security}"

mkdir -p "$DIST"
exec > >(tee -a "$LOG") 2>&1
fail() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

[[ "$(uname -m)" == x86_64 ]] || fail "Build host must be x86_64 (got $(uname -m))."
[[ $EUID -eq 0 ]] || fail "Run with sudo: sudo ./scripts/build-iso.sh"
for tool in debootstrap chroot mount umount mksquashfs grub-mkrescue xorriso mformat; do
  command -v "$tool" >/dev/null 2>&1 || fail "Missing build dependency '$tool'. Install debootstrap, squashfs-tools, grub-common, grub-pc-bin, grub-efi-amd64-bin, xorriso, and mtools. live-build is not required."
done
command -v sha256sum >/dev/null 2>&1 || fail "sha256sum is required."
[[ -f "$ROOT/config/package-lists/nebula.list.chroot" ]] || fail "Missing package list."

MIRROR_HOST="${MIRROR#*://}"
MIRROR_HOST="${MIRROR_HOST%%/*}"
if ! getent hosts "$MIRROR_HOST" >/dev/null 2>&1; then
  fail "Cannot resolve Debian package mirror host '$MIRROR_HOST'. The direct builder needs network access to download Debian packages. No ISO was produced."
fi

BUILD_START="$(date +%s)"
cleanup() {
  set +e
  for target in run /sys /proc /dev; do
    mountpoint -q "$ROOTFS/$target" && umount -R "$ROOTFS/$target"
  done
}
trap cleanup EXIT INT TERM
rm -rf "$WORK"
mkdir -p "$ROOTFS" "$ISO_TREE/live" "$ISO_TREE/boot/grub"

printf '\n==> Stage 1/7: bootstrap Debian %s (%s)\n' "$SUITE" "$ARCH"
debootstrap --arch="$ARCH" --variant=minbase \
  --components=main,contrib,non-free,non-free-firmware \
  "$SUITE" "$ROOTFS" "$MIRROR"

printf '\n==> Stage 2/7: configure package sources and install the OS\n'
mkdir -p "$ROOTFS/etc/apt/sources.list.d"
rm -f "$ROOTFS/etc/apt/sources.list" "$ROOTFS/etc/apt/sources.list.d/debian.sources"
cat > "$ROOTFS/etc/apt/sources.list.d/nebula.sources" <<SOURCES
Types: deb
URIs: $MIRROR
Suites: $SUITE ${SUITE}-updates
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

Types: deb
URIs: $SECURITY_MIRROR
Suites: ${SUITE}-security
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
SOURCES

# Mount only the virtual filesystems required by package configuration.
mount --rbind /dev "$ROOTFS/dev"
mount --make-rslave "$ROOTFS/dev"
mount -t proc proc "$ROOTFS/proc"
mount -t sysfs sysfs "$ROOTFS/sys"
mkdir -p "$ROOTFS/run"
mount -t tmpfs tmpfs "$ROOTFS/run"

chroot "$ROOTFS" /usr/bin/env DEBIAN_FRONTEND=noninteractive sh -eu -c '
  apt-get update
  apt-get install -y --no-install-recommends ca-certificates gnupg locales tzdata systemd-sysv sudo live-boot live-config linux-image-amd64 initramfs-tools
'
mapfile -t PACKAGES < <(sed -e 's/#.*//' -e 's/[[:space:]]//g' "$ROOT/config/package-lists/nebula.list.chroot" | sed '/^$/d' | sort -u)
chroot "$ROOTFS" /usr/bin/env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${PACKAGES[@]}"

printf '\n==> Stage 3/7: install NebulaForge files and configure the live session\n'
cp -a "$ROOT/config/includes.chroot/." "$ROOTFS/"
install -d -m 0755 "$ROOTFS/usr/local/share/nebula"
printf '%s\n' 'NebulaForge OS live image' > "$ROOTFS/usr/local/share/nebula/IMAGE_ID"

# Fail before packaging if the image's own session wiring is incomplete.
validate_live_rootfs() {
  local path package status
  for path in \
    /usr/share/wayland-sessions/nebula.desktop \
    /etc/xdg/labwc/autostart \
    /usr/local/bin/nebula-shell \
    /usr/local/bin/nebula-files \
    /usr/local/bin/nebula-settings \
    /usr/local/bin/forge \
    /usr/local/share/nebula/nebula-shell.py \
    /usr/local/share/nebula/nebula-files.py \
    /usr/local/share/nebula/nebula-settings.py \
    /usr/local/sbin/nebula-live-user-setup \
    /etc/systemd/system/nebula-live-user.service; do
    [[ -s "$ROOTFS$path" ]] || fail "Live root filesystem is missing required file: $path"
  done
  [[ -L "$ROOTFS/etc/systemd/system/multi-user.target.wants/nebula-live-user.service" ]] || fail "Live-user systemd service is not enabled."
  for path in /usr/local/bin/nebula-shell /usr/local/bin/nebula-files /usr/local/bin/nebula-settings /usr/local/bin/forge /usr/local/sbin/nebula-live-user-setup; do
    [[ -x "$ROOTFS$path" ]] || fail "Live-session entry point is not executable: $path"
  done
  for package in live-boot live-config labwc lightdm python3-gi gir1.2-gtk-3.0; do
    status="$(dpkg-query --admindir="$ROOTFS/var/lib/dpkg" -W -f='${db:Status-Status}' "$package" 2>/dev/null || true)"
    [[ "$status" == installed ]] || fail "Required runtime package '$package' is not installed (status: ${status:-missing})."
  done
  grep -Fq 'Exec=labwc' "$ROOTFS/usr/share/wayland-sessions/nebula.desktop" || fail "Nebula Wayland session does not launch labwc."
  grep -Fq '/usr/local/bin/nebula-shell' "$ROOTFS/etc/xdg/labwc/autostart" || fail "labwc autostart does not launch Nebula Desktop."
  printf '%s\n' 'Live root filesystem acceptance checks passed.'
}
validate_live_rootfs

# live-config creates the unprivileged `user` account at boot. Keep it out of
# the image's passwd database and only configure supplementary groups if the
# account already exists (for remastered/installed environments).
# The live account is created at boot; a first-party systemd oneshot applies
# supplementary groups before the display manager starts.

cat > "$ROOTFS/etc/locale.gen" <<'LOCALES'
en_US.UTF-8 UTF-8
LOCALES
chroot "$ROOTFS" locale-gen en_US.UTF-8
printf '%s\n' 'LANG=en_US.UTF-8' > "$ROOTFS/etc/default/locale"
ln -snf /usr/share/zoneinfo/UTC "$ROOTFS/etc/localtime"
printf '%s\n' nebulaforge > "$ROOTFS/etc/hostname"
cat > "$ROOTFS/etc/hosts" <<'HOSTS'
127.0.0.1 localhost
127.0.1.1 nebulaforge
::1 localhost ip6-localhost ip6-loopback
HOSTS

# Ensure live-boot hooks are present in the initramfs after all packages and
# Nebula configuration have been installed.
chroot "$ROOTFS" update-initramfs -u -k all

printf '\n==> Stage 4/7: remove package caches and prepare live filesystem\n'
chroot "$ROOTFS" apt-get clean
rm -rf "$ROOTFS/var/lib/apt/lists/"* "$ROOTFS/tmp/"* "$ROOTFS/var/tmp/"*
find "$ROOTFS" -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete

KERNEL="$(find "$ROOTFS/boot" -maxdepth 1 -type f -name 'vmlinuz-*' -printf '%f\n' | sort -V | tail -n1)"
[[ -n "$KERNEL" ]] || fail "No installed Linux kernel found in the target root filesystem."
KVER="${KERNEL#vmlinuz-}"
INITRD="$ROOTFS/boot/initrd.img-$KVER"
[[ -s "$INITRD" ]] || fail "Missing initramfs for installed kernel $KVER."
install -m 0644 "$ROOTFS/boot/$KERNEL" "$ISO_TREE/live/vmlinuz"
install -m 0644 "$INITRD" "$ISO_TREE/live/initrd.img"

printf '\n==> Stage 5/7: create compressed root filesystem\n'
mksquashfs "$ROOTFS" "$ISO_TREE/live/filesystem.squashfs" -comp xz -b 1M -noappend -processors "$(nproc)"
stat -c '%s' "$ISO_TREE/live/filesystem.squashfs" > "$ISO_TREE/live/filesystem.size"

printf '\n==> Stage 6/7: write BIOS/UEFI GRUB menu and assemble ISO\n'
cat > "$ISO_TREE/boot/grub/grub.cfg" <<'GRUB'
set default=0
set timeout=5
if loadfont unicode; then
  set gfxmode=auto
  insmod all_video
  insmod gfxterm
  terminal_output gfxterm
fi
menuentry "NebulaForge OS (Live)" {
  search --no-floppy --set=root --file /live/filesystem.squashfs
  linux /live/vmlinuz boot=live components quiet splash username=user hostname=nebulaforge locales=en_US.UTF-8 keyboard-layouts=us
  initrd /live/initrd.img
}
menuentry "NebulaForge OS (Live, safe graphics)" {
  search --no-floppy --set=root --file /live/filesystem.squashfs
  linux /live/vmlinuz boot=live components username=user hostname=nebulaforge locales=en_US.UTF-8 keyboard-layouts=us nomodeset
  initrd /live/initrd.img
}
GRUB

ISO_TMP="$DIST/NebulaForge-OS-amd64.iso.tmp"
rm -f "$ISO_TMP"
grub-mkrescue -o "$ISO_TMP" "$ISO_TREE" -- -volid NEBULAFORGE
[[ -s "$ISO_TMP" ]] || fail "GRUB returned without producing a non-empty ISO."
# Inspect the completed image before promoting it to the release path. This
# checks the live payload, BIOS/UEFI El Torito metadata, and embedded GRUB menu.
bash "$ROOT/scripts/verify-iso.sh" "$ISO_TMP"
mv "$ISO_TMP" "$DIST/NebulaForge-OS-amd64.iso"

printf '\n==> Stage 7/7: write checksum and build manifest\n'
sha256sum "$DIST/NebulaForge-OS-amd64.iso" > "$DIST/SHA256SUMS"
cat > "$DIST/build-manifest.txt" <<MANIFEST
Project: NebulaForge OS
Architecture: $ARCH
Base distribution: Debian GNU/Linux 13 (Trixie)
Build method: direct debootstrap + chroot package installation + SquashFS + GRUB (no live-build)
Build time UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Source revision: $(git -C "$ROOT" rev-parse HEAD 2>/dev/null || printf 'not a git checkout')
Builder kernel: $(uname -r)
Target kernel: $KVER
Build duration seconds: $(( $(date +%s) - BUILD_START ))
ISO bytes: $(stat -c %s "$DIST/NebulaForge-OS-amd64.iso")
ISO SHA-256: $(sha256sum "$DIST/NebulaForge-OS-amd64.iso" | awk '{print $1}')
MANIFEST
printf '\nISO produced: %s\n' "$DIST/NebulaForge-OS-amd64.iso"
printf 'Checksum: '; cat "$DIST/SHA256SUMS"

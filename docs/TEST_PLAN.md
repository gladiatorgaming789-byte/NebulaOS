# Acceptance test plan

## Automated checks

- CLI argument parsing and safe error behavior.
- `forge system info` emits valid JSON.
- `forge game list` works when game folders are absent.
- Invalid package query and invalid log line counts are rejected.
- Build script fails clearly when dependencies, privileges, or network access are missing.
- ISO verifier accepts a structurally complete synthetic fixture and rejects a fixture missing UEFI boot metadata.
- Source packaging creates a valid ZIP and matching SHA-256 checksum without caches or build outputs.
- On a real build, the ISO exists, is non-empty, has a SHA-256 checksum, contains the kernel/initramfs/SquashFS, reports BIOS and UEFI El Torito boot entries, and has the expected embedded GRUB menu.

## VirtualBox manual acceptance

Run BIOS and EFI separately. Use 4 vCPUs, 8 GiB RAM, NAT networking, and a disposable 40–64 GiB disk. Verify live boot, graphical login, launcher, file operations, terminal, network, sound fallback, Wine diagnostics, developer tools, restart/shutdown, installer, and installed-system boot. Record the VirtualBox version, VM settings, ISO checksum, and screenshots/logs. Do not mark any test passed until observed.

## Current environment note

This environment currently has no DNS resolution for `deb.debian.org` and does not have `xorriso`, `mksquashfs`, `debootstrap`, or GRUB ISO tools installed. The direct build path no longer requires `live-build`, but ISO generation remains blocked here until a network-enabled build host with the listed build dependencies is available. Unit tests and static validation can run offline.


## Nebula Files manual acceptance checks

- Open Nebula Files from the shell and verify Home and parent navigation.
- Create, rename, copy, cut, and paste a disposable file and directory.
- Confirm hidden-file toggle changes the listing.
- Select multiple items and confirm Delete requires explicit confirmation.
- Verify a symlink is shown as a link and deleting it does not delete its target.
- Verify properties show mode, UID/GID, size, modified time, and symlink target where applicable.
- Attempt a read-only or inaccessible directory and verify a useful error appears without crashing.

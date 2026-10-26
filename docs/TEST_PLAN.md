# Acceptance test plan

## Automated checks

- CLI argument parsing and safe error behavior.
- `forge system info` emits valid JSON.
- `forge game list` works when game folders are absent.
- Invalid package query and invalid log line counts are rejected.
- `forge system health` returns failure for required systemd/root-disk checks, but treats NetworkManager and Vulkan as optional capabilities.
- File operations reject copying or moving a directory into itself or a descendant.
- File operations refuse overwrites, preserve symlinks without following their targets, and publish copied regular files without a destination-exists race.
- Build script fails clearly when dependencies, privileges, or network access are missing.
- ISO verifier accepts a structurally complete synthetic fixture and rejects a fixture missing UEFI boot metadata.
- Source packaging creates a valid ZIP and matching SHA-256 checksum without caches or build outputs.
- On a real build, the ISO exists, is non-empty, has a SHA-256 checksum, contains the kernel/initramfs/SquashFS, reports BIOS and UEFI El Torito boot entries, and has the expected embedded GRUB menu.

## Release boot-validation gate (required before claiming a release boots)

A source-validation run and structural ISO verification do not establish that the image boots. Before marking a release candidate boot-validated, run the same ISO in a disposable VM twice:

1. BIOS/legacy firmware.
2. EFI/UEFI firmware.

Use 4 vCPUs, 8 GiB RAM, NAT networking, and a disposable 40–64 GiB disk. Verify live boot reaches the graphical session, launcher opens, file operations work, terminal opens, network status is available or its failure is explained, sound fallback is sensible, and restart/shutdown works. If installation is part of the release claim, install to the disposable disk and verify the installed system boots. Do not test an untrusted image with host folder sharing or passthrough devices.

For each run, record the release candidate tag/commit, ISO SHA-256, VM software/version, firmware mode, settings, observed result, and relevant logs/screenshots. A failed or unrun firmware mode must remain explicitly marked as not passed. The current CI pipeline does **not** perform these GUI/VM checks automatically; a release is not boot-validated until this gate is completed and its evidence is reviewed.

## VirtualBox manual acceptance

Use the configuration above. Verify the live desktop, graphical login, launcher, file manager, terminal, network, sound fallback, Wine diagnostics, developer tools, restart/shutdown, installer, and installed-system boot. Record the VirtualBox version, VM settings, ISO checksum, and screenshots/logs. Do not mark any test passed until observed.

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

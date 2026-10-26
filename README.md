# NebulaOS / NebulaForge OS

NebulaOS is a Debian-based desktop OS project focused on a lightweight live desktop, a small first-party desktop shell, file manager, settings app, and the `forge` command-line tools.

> **Development status:** this repository is under active development. A successful source check or structurally valid ISO is not proof that the image boots or that the desktop works on physical hardware.

## Project layout

- `desktop/` — desktop shell, file manager, settings UI, and reusable backends.
- `forge/` — source for the `forge` system CLI.
- `config/` — live image configuration and files installed into the image.
- `scripts/build-iso.sh` — direct ISO build pipeline.
- `scripts/verify-iso.sh` — structural ISO and BIOS/UEFI boot-menu checks.
- `scripts/validate-source.sh` — offline unit, syntax, consistency, and packaging checks.
- `tests/` — automated Python and shell regression tests.
- `docs/ARCHITECTURE.md`, `docs/TEST_PLAN.md`, `docs/SECURITY.md` — design, acceptance, and security notes.

## Development prerequisites

For source validation, use Python 3 and Bash. Run from the repository root:

```bash
bash ./scripts/validate-source.sh
```

For an ISO build, use a Debian/Ubuntu Linux host with root/sudo access, network access to Debian package repositories, and the build dependencies installed by the CI workflow (including `debootstrap`, `xorriso`, SquashFS tools, GRUB BIOS/EFI tools, and `mtools`):

```bash
sudo bash ./scripts/build-iso.sh
bash ./scripts/verify-iso.sh dist/NebulaForge-OS-amd64.iso
(cd dist && sha256sum -c SHA256SUMS)
```

The build script may need network access to bootstrap the root filesystem and fetch packages. Keep build outputs in `dist/`; do not commit generated ISOs or local caches.

## Testing and release expectations

1. Run `./scripts/validate-source.sh` and resolve all failures.
2. Build the ISO on a clean, supported Linux runner.
3. Run `scripts/verify-iso.sh` and verify the published SHA-256 manifest.
4. Before calling a release boot-validated, complete the BIOS and UEFI VM acceptance steps in [the test plan](docs/TEST_PLAN.md). Record the ISO checksum, VM settings, and observed results. Structural verification alone is not a boot test.
5. Review [the security baseline](docs/SECURITY.md) before publishing a release.

Version tags matching `v*` trigger the ISO build/release workflow. Do not create a release tag until source validation passes and the release candidate has been reviewed. GitHub release artifacts should include the ISO, `SHA256SUMS`, and build manifest.

## Contributing

Please include regression tests for behavior changes, keep packaged copies synchronized with their canonical source files, and avoid claiming a feature works unless it is implemented and tested. The source-validation script checks several source/package copies for exact consistency.

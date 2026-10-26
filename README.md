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

## Build an ISO with GitHub Actions (recommended)

You do not need to install Linux build tools on your own computer. GitHub Actions can build the ISO on a hosted Ubuntu runner and give you a downloadable artifact.

1. Open the repository's **Actions** tab: [NebulaOS Actions](https://github.com/gladiatorgaming789-byte/NebulaOS/actions).
2. Select **Build NebulaForge ISO** from the workflow list.
3. Click **Run workflow**, choose the branch you want to build, optionally enter a short build note, and click **Run workflow** again.
4. Open the new workflow run and wait for it to finish. A build can take a while because it downloads Debian and installs the desktop packages.
5. Under **Artifacts**, download **NebulaForge-OS-amd64**. Extract the downloaded ZIP; it contains the ISO, `SHA256SUMS`, and `build-manifest.txt`.
6. Verify the ISO checksum from the extracted folder with `sha256sum -c SHA256SUMS` on Linux.

If the build fails, open the failed run's log. The workflow also tries to upload `NebulaForge-build-log` to help diagnose build failures. The ISO artifact is kept for 30 days.

Pushing a version tag such as `v0.1.0` runs the same checks and build, then publishes the ISO and its manifests to a GitHub Release. **A successful build and structural check do not prove that the ISO boots**; complete the BIOS and UEFI VM tests in [the test plan](docs/TEST_PLAN.md) before describing a release as boot-validated.

## Local build (advanced)

If you prefer to build on your own Debian/Ubuntu Linux host, you need root/sudo access, network access to Debian package repositories, and the tools used by the workflow (`debootstrap`, `xorriso`, SquashFS tools, GRUB BIOS/EFI tools, and `mtools`):

```bash
bash ./scripts/validate-source.sh
sudo bash ./scripts/build-iso.sh
bash ./scripts/verify-iso.sh dist/NebulaForge-OS-amd64.iso
(cd dist && sha256sum -c SHA256SUMS)
```

The build script fetches Debian packages from the configured repositories. Keep build outputs in `dist/`; do not commit generated ISOs or local caches.

## Testing and release expectations

1. Run `./scripts/validate-source.sh` and resolve all failures.
2. Build the ISO on a clean, supported Linux runner.
3. Run `scripts/verify-iso.sh` and verify the published SHA-256 manifest.
4. Before calling a release boot-validated, complete the BIOS and UEFI VM acceptance steps in [the test plan](docs/TEST_PLAN.md). Record the ISO checksum, VM settings, and observed results. Structural verification alone is not a boot test.
5. Review [the security baseline](docs/SECURITY.md) before publishing a release.

Version tags matching `v*` trigger the ISO build/release workflow. Do not create a release tag until source validation passes and the release candidate has been reviewed. GitHub release artifacts should include the ISO, `SHA256SUMS`, and build manifest.

## Contributing

Please include regression tests for behavior changes, keep packaged copies synchronized with their canonical source files, and avoid claiming a feature works unless it is implemented and tested. The source-validation script checks several source/package copies for exact consistency.

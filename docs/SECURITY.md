# Security baseline

- Desktop shell and user applications run as an ordinary user.
- The CLI does not evaluate user input as shell syntax.
- File operations reject directory self-nesting, preserve symlinks rather than following them during copy/delete, and avoid overwriting existing destinations. Test filesystem behavior on the target filesystem before adding new operation types.
- Package search is read-only; package install/update/recovery operations are not implemented yet.
- Downloaded Windows installers must be launched only after explicit user action; do not run them with elevated privileges by default.
- No external telemetry is implemented. Diagnostics should remain local unless the user explicitly exports them.
- Do not ship credentials, proprietary Windows files, or game content.
- Release builds must use authenticated Debian repositories and preserve upstream package signatures.
- GitHub Actions in CI/release workflows are pinned to full commit SHAs with the upstream major tag retained as a comment. Review and update pins deliberately; a comment is documentation, not a cryptographic guarantee about the tag.
- Release workflow validates the generated SHA-256 manifest before publishing. Consumers should obtain the checksum file from the same trusted release channel as the ISO and verify it before booting. A checksum proves byte integrity relative to the manifest, not who built the image or whether the image is safe.

## Release verification

1. Review the source diff and CI results for the exact commit being tagged.
2. Build the ISO in the release workflow and require structural verification and `sha256sum -c SHA256SUMS` to pass.
3. Complete the BIOS and UEFI boot-validation gate in [the test plan](TEST_PLAN.md) before describing the release as boot-tested.
4. Publish the ISO with `SHA256SUMS` and `build-manifest.txt`. Preserve the commit/tag and test evidence alongside the release notes.
5. Never interpret a successful source check or ISO structure check as a substitute for VM testing, security review, or signed build provenance.

## Release blockers

Before a public ISO is called secure or production-ready, implement and test the installer, disk-encryption flow, privilege broker, firewall policy, secure update behavior, backup/restore, and privacy controls. These are not claimed complete by this baseline.

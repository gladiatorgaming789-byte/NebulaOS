# Security baseline

- Desktop shell and user applications run as an ordinary user.
- The CLI does not evaluate user input as shell syntax.
- Package search is read-only; package install/update/recovery operations are not implemented yet.
- Downloaded Windows installers must be launched only after explicit user action; do not run them with elevated privileges by default.
- No external telemetry is implemented. Diagnostics should remain local unless the user explicitly exports them.
- Do not ship credentials, proprietary Windows files, or game content.
- Release builds must use authenticated Debian repositories and preserve upstream package signatures.

## Release blockers

Before a public ISO is called secure or production-ready, implement and test the installer, disk-encryption flow, privilege broker, firewall policy, secure update behavior, backup/restore, and privacy controls. These are not claimed complete by this baseline.

# Third-party software inventory (initial plan)

This is an intended package inventory, not a record of a completed ISO. The actual package versions and licenses must be captured from the final root filesystem before release.

| Component | Role | Source / licensing note |
|---|---|---|
| Linux kernel | Kernel | Debian-supplied; GPL-2.0-only and other notices in upstream tree |
| Debian base | Userland, init, package management | Debian packages under their respective licenses |
| debootstrap / live-boot / live-config | Root filesystem creation and live session | Debian packages under their respective licenses |
| GRUB / xorriso / SquashFS tools | Bootable ISO and compressed live filesystem | Debian packages under their respective licenses |
| labwc | Wayland compositor/window manager | Upstream project; retain upstream license and notices |
| GTK 3 / PyGObject | UI toolkit | LGPL and associated upstream notices |
| LightDM | Login manager | Upstream package license and notices |
| Thunar | Initial file manager | XFCE component; not original NebulaForge code |
| Wine / winetricks | Windows API compatibility | Upstream licenses; no Windows binaries bundled |
| Mesa / Vulkan tools | Graphics stack and diagnostics | Upstream licenses and firmware-specific terms |
| MangoHud / GameMode | Gaming telemetry/performance tools | Upstream licenses |

For a distributable image, generate an SPDX or CycloneDX inventory, include applicable license texts, and verify package availability and redistribution terms for the exact build.

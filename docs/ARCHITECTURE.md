# Architecture and boundaries

## Foundation

NebulaForge OS targets Debian 13 (Trixie) on amd64. Debian supplies the kernel, firmware, init system, device management, networking, package verification, and core userspace. These are deliberately reused rather than forked. The direct builder uses `debootstrap` for the base root filesystem, installs a declared package list in a chroot, applies first-party files, creates a SquashFS root, and assembles a BIOS/UEFI GRUB ISO. It does not depend on `live-build`. The build is pinned to the Trixie suite and records a manifest.

## Original components

- `forge`: first-party CLI for read-only system inspection and safe discovery commands. Commands that mutate the system are explicitly marked unimplemented until they have privilege checks, transaction previews, and tests.
- `nebula-shell`: first-party GTK launcher and quick-action surface. It delegates app launch to desktop metadata and launches known system utilities without invoking a shell on user-controlled text.
- Nebula visual tokens and original SVG wallpaper: dark space palette, violet/cyan accents, consistent spacing, readable contrast.

## Reused components

- Linux kernel and Debian userspace: upstream Debian packages.
- labwc: Wayland compositor/window manager.
- GTK 3 and PyGObject: UI toolkit and bindings.
- Thunar: file manager in the initial milestone; it is not an original NebulaForge file manager.
- LightDM: display manager.
- Wine, Mesa, Vulkan tools, MangoHud, GameMode: third-party gaming stack components; availability and licensing must be checked for every release.

## Session startup

LightDM provides a graphical login. The selected Wayland session starts labwc. labwc's session autostart launches `nebula-shell` as the signed-in user. The shell must not run as root. Window placement, snapping, workspaces, and compositor behavior are labwc capabilities, not claimed as original shell code.

## Package and privilege boundary

APT remains the package transaction engine. A future software UI must call a narrow privileged backend with a fixed operation schema and explicit confirmation, never concatenate arbitrary user strings into shell commands. The current `forge package search` is read-only. Mutating package, update, and recovery subcommands return a clear not-implemented result.

## Live ISO limitation

A live ISO is a distinct milestone from an installed OS. Boot success does not prove installation success, secure update behavior, or hardware compatibility. BIOS/UEFI and installed-disk acceptance results must be recorded separately.


## Nebula Files (initial implementation)

`desktop/nebula-files.py` is the first-party GTK file manager. It supports folder navigation, hidden-file visibility, multi-selection, create-folder, rename, copy/cut/paste, delete with explicit confirmation, file opening through the desktop MIME association, and basic metadata/permissions inspection. Copy/move operations preserve symlinks rather than recursively following them. Delete is permanent in this development version; the confirmation dialog states that no trash recovery is available. It does not yet implement drag-and-drop, archive browsing, preview panes, removable-volume management UI, or undo. Filesystem operations are isolated in `desktop/nebula_fileops.py` and covered by offline tests for traversal-name rejection, overwrite refusal, and symlink-safe copy/delete behavior.

## Nebula Settings (first control-center slice)

`desktop/nebula-settings.py` presents an original control-center surface. Network, audio, display, appearance, power, Bluetooth, and default-application actions launch their established configuration utilities only when the corresponding executable exists; missing backends are visibly disabled rather than simulated. The system-information panel reads kernel, architecture, root filesystem, memory, and NetworkManager status using fixed, read-only commands with short timeouts and bounded output. The GTK window is intentionally not run with elevated privileges. `desktop/nebula_settings_backend.py` isolates the read-only diagnostic logic so it can be unit-tested without GTK installed.

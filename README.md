# NebulaOS

NebulaOS is an experimental operating system project aimed at gamers and developers. The long-term goals are a custom kernel, a purpose-built desktop, developer tooling, and a staged Windows PE/API compatibility layer.

## Current milestone: BIOS boot + text console

This branch establishes a small educational x86 boot path:
- A custom 16-bit BIOS boot sector.
- A freestanding 32-bit x86 kernel written in C and assembly.
- A 1.44 MiB El Torito floppy-emulation image embedded in a bootable ISO.
- A GitHub Actions workflow that builds and uploads the ISO artifact.

**Status:** early prototype. It is not a general-purpose OS and does not run Windows `.exe` files yet.

## Build on Windows

1. Install WSL 2 with Ubuntu: `wsl --install -d Ubuntu`.
2. In Ubuntu, install tools:

   ```bash
   sudo apt update
   sudo apt install -y build-essential gcc-multilib binutils nasm xorriso
   ```

3. Clone the repository inside WSL (recommended):

   ```bash
   git clone https://github.com/gladiatorgaming789-byte/NebulaOS.git
   cd NebulaOS
   git checkout feature/custom-bios-boot-console
   ```

4. Build:

   ```bash
   chmod +x build.sh
   ./build.sh
   ```

The ISO is written to `build/NebulaOS.iso`.

## Run in VirtualBox

Create a VM with **Type: Other**, **Version: Other/Unknown (32-bit)**, 128–256 MiB RAM, and EFI disabled. Mount `build/NebulaOS.iso` as the optical disk and boot from it. This prototype uses legacy BIOS and 32-bit protected mode.

## Current constraints

- The bootloader loads a fixed 32 KiB kernel window from the emulated floppy image.
- No disk filesystem, user mode, multitasking, drivers, networking, audio, or graphics acceleration exists yet.
- The first milestone is a VGA text console.
- Windows executable support requires a PE loader plus substantial Win32 API and runtime compatibility; it is a future project, not a current feature.

See [docs/ROADMAP.md](docs/ROADMAP.md) for the development plan.

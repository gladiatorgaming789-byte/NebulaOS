#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$ROOT_DIR/build"
ISO_ROOT="$BUILD_DIR/iso-root"
BOOT_IMAGE="$ISO_ROOT/boot/boot.img"
KERNEL_LIMIT=$((64 * 512))

for tool in nasm gcc ld objcopy xorriso dd truncate wc cp; do
    command -v "$tool" >/dev/null 2>&1 || {
        echo "Missing required tool: $tool" >&2
        exit 1
    }
done

mkdir -p "$BUILD_DIR"
rm -f "$BUILD_DIR"/*.o "$BUILD_DIR"/*.elf "$BUILD_DIR"/*.bin "$BUILD_DIR"/*.iso
rm -rf "$ISO_ROOT"
mkdir -p "$ISO_ROOT/boot"

echo "[1/6] Assembling BIOS boot sector..."
nasm -f bin "$ROOT_DIR/boot/boot.asm" -o "$BUILD_DIR/boot.bin"
BOOT_SIZE="$(wc -c < "$BUILD_DIR/boot.bin")"
if [[ "$BOOT_SIZE" -ne 512 ]]; then
    echo "Boot sector must be exactly 512 bytes (got $BOOT_SIZE)." >&2
    exit 1
fi

echo "[2/6] Assembling kernel entry..."
nasm -f elf32 "$ROOT_DIR/kernel/entry.asm" -o "$BUILD_DIR/entry.o"

echo "[3/6] Compiling freestanding 32-bit kernel..."
gcc -m32 -std=c11 -O2 -Wall -Wextra -Werror \
    -ffreestanding -fno-pie -fno-pic -fno-stack-protector \
    -fno-asynchronous-unwind-tables -fno-unwind-tables \
    -mno-sse -mno-mmx -msoft-float -c \
    "$ROOT_DIR/kernel/kernel.c" -o "$BUILD_DIR/kernel.o"

echo "[4/6] Linking and extracting flat kernel..."
ld -m elf_i386 -T "$ROOT_DIR/linker.ld" -nostdlib \
    -o "$BUILD_DIR/kernel.elf" "$BUILD_DIR/entry.o" "$BUILD_DIR/kernel.o"
objcopy -O binary "$BUILD_DIR/kernel.elf" "$BUILD_DIR/kernel.bin"

KERNEL_SIZE="$(wc -c < "$BUILD_DIR/kernel.bin")"
if [[ "$KERNEL_SIZE" -gt "$KERNEL_LIMIT" ]]; then
    echo "Kernel is $KERNEL_SIZE bytes; bootloader limit is $KERNEL_LIMIT bytes." >&2
    exit 1
fi
echo "Kernel size: $KERNEL_SIZE / $KERNEL_LIMIT bytes"

echo "[5/6] Creating 1.44 MiB floppy-emulation boot image..."
truncate -s 1474560 "$BOOT_IMAGE"
dd if="$BUILD_DIR/boot.bin" of="$BOOT_IMAGE" conv=notrunc status=none
dd if="$BUILD_DIR/kernel.bin" of="$BOOT_IMAGE" bs=512 seek=1 conv=notrunc status=none
cp "$BUILD_DIR/kernel.bin" "$ISO_ROOT/boot/kernel.bin"
cp "$ROOT_DIR/README.md" "$ISO_ROOT/README.txt"

echo "[6/6] Creating bootable ISO..."
xorriso -as mkisofs \
    -o "$BUILD_DIR/NebulaOS.iso" \
    -V NEBULAOS \
    -b boot/boot.img \
    -c boot/boot.cat \
    "$ISO_ROOT"

echo
echo "Build complete: $BUILD_DIR/NebulaOS.iso"

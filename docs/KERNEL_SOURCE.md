# Supplied Linux source archive

The uploaded `linux-7.3.tar.xz` archive passed `xz -t` and its top-level directory contains a Linux kernel source tree whose Makefile identifies version `7.3.0` (codename `Baby Opossum Posse`). Archive SHA-256: `87363c24f10e06321eb362765521094e94471f6bff8bce2d6b3e40f39f004953`. The archive is not copied into this source package to avoid duplicating a large third-party source tree.

The initial live image intentionally uses Debian's maintained `linux-image-amd64` package rather than building the uploaded source directly. This gives the first image a kernel integrated with Debian's package lifecycle and expected firmware/module packaging. The supplied source remains an available candidate for a later controlled kernel-build experiment; before using it in a release, verify upstream provenance/signature and test out-of-tree modules, initramfs generation, VirtualBox boot, and real-hardware driver coverage. The current build does not claim to compile or boot Linux 7.3.0.


## Supplied source archive

The supplied `linux-7.3.tar.xz` archive identifies itself as Linux 7.3.0 (`VERSION = 7`, `PATCHLEVEL = 3`, `SUBLEVEL = 0`). Its observed SHA-256 in the working environment is `87363c24f10e06321eb362765521094e94471f6bff8bce2d6b3e40f39f004953`. This hash identifies the supplied bytes only; it does not establish upstream authenticity. The initial live image uses Debian's maintained signed kernel package to keep the first bootable milestone integrated with Debian's firmware and update process. Before switching to the supplied source, validate its upstream signature/checksum, select and test a kernel configuration, and verify module/firmware compatibility. The archive is not copied into this source ZIP.

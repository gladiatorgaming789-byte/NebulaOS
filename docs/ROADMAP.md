# NebulaOS roadmap

## Phase 0 — Bootable console prototype
- [x] Custom BIOS boot sector source
- [x] Freestanding 32-bit kernel entry
- [x] VGA text output
- [x] ISO build script
- [ ] Verify boot in VirtualBox and QEMU

## Phase 1 — Interactive console
- [ ] Keyboard driver (PS/2 first)
- [ ] Line editor and command parser
- [ ] Commands: help, clear, about, meminfo
- [ ] Basic panic/exception reporting

## Phase 2 — Kernel foundations
- [ ] GDT/IDT and exception handlers
- [ ] Physical memory map and page allocator
- [ ] Paging and virtual memory
- [ ] Timer interrupt and preemptive scheduling
- [ ] Kernel heap

## Phase 3 — Devices and storage
- [ ] PCI enumeration
- [ ] VirtualBox-compatible storage and input drivers
- [ ] Disk block layer
- [ ] Filesystem (start with a simple read-only filesystem)
- [ ] User/kernel privilege separation

## Phase 4 — Native applications
- [ ] System-call ABI
- [ ] Executable format and loader
- [ ] Process isolation
- [ ] Native shell and developer utilities

## Phase 5 — Graphical environment
- [ ] Framebuffer abstraction
- [ ] Window/compositor architecture
- [ ] Input routing and font rendering
- [ ] Nebula launcher, taskbar, settings, and file manager

## Phase 6 — Windows compatibility research
- [ ] PE/COFF parser and loader
- [ ] Define a Windows API compatibility scope
- [ ] Implement memory, process, file, and synchronization APIs
- [ ] Add test programs and compatibility tests
- [ ] Research graphics, audio, networking, and game input APIs

Windows executable compatibility is a long-term effort. Reading a PE file is only one part; applications depend on Win32 APIs, runtimes, graphics, drivers, and sometimes anti-cheat systems. No compatibility promise should be made until individual programs have been tested.

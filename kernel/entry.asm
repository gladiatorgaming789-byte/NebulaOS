BITS 32
section .text
global _start
extern kernel_main

_start:
    cli
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    mov esp, 0x90000
    cld
    call kernel_main
.hang:
    cli
    hlt
    jmp .hang

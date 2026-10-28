; NebulaOS custom BIOS boot sector. Reads 64 sectors from the boot floppy
; image to 0x10000, enters 32-bit protected mode, and jumps to the kernel.

BITS 16
ORG 0x7C00

start:
    cli
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00
    sti
    mov [boot_drive], dl

    mov si, boot_message
    call print_string

    mov ax, 0x1000
    mov es, ax
    xor bx, bx
    mov byte [current_cylinder], 0
    mov byte [current_head], 0
    mov byte [current_sector], 2
    mov word [sectors_left], 64

.load_next:
    mov ah, 0x02
    mov al, 1
    mov ch, [current_cylinder]
    mov dh, [current_head]
    mov cl, [current_sector]
    mov dl, [boot_drive]
    int 0x13
    jc disk_error

    mov ax, es
    add ax, 0x20
    mov es, ax

    inc byte [current_sector]
    cmp byte [current_sector], 19
    jb .chs_ready
    mov byte [current_sector], 1
    inc byte [current_head]
    cmp byte [current_head], 2
    jb .chs_ready
    mov byte [current_head], 0
    inc byte [current_cylinder]
.chs_ready:
    dec word [sectors_left]
    jnz .load_next

    cli
    in al, 0x92
    or al, 00000010b
    out 0x92, al
    lgdt [gdt_descriptor]
    mov eax, cr0
    or eax, 1
    mov cr0, eax
    jmp CODE_SEG:protected_mode

disk_error:
    mov si, error_message
    call print_string
.hang:
    cli
    hlt
    jmp .hang

print_string:
    lodsb
    test al, al
    jz .done
    mov ah, 0x0E
    mov bx, 0x0007
    int 0x10
    jmp print_string
.done:
    ret

BITS 32
protected_mode:
    mov ax, DATA_SEG
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    mov esp, 0x90000
    jmp 0x08:0x00010000

align 8
gdt_start:
    dq 0
    dq 0x00CF9A000000FFFF
    dq 0x00CF92000000FFFF
gdt_end:
gdt_descriptor:
    dw gdt_end - gdt_start - 1
    dd gdt_start
CODE_SEG equ 0x08
DATA_SEG equ 0x10

boot_message db "NebulaOS: loading kernel...", 13, 10, 0
error_message db "Disk read failed. Halting.", 13, 10, 0
boot_drive db 0
current_cylinder db 0
current_head db 0
current_sector db 0
sectors_left dw 0

times 510-($-$$) db 0
dw 0xAA55

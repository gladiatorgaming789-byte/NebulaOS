#include <stddef.h>
#include <stdint.h>

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY ((volatile uint16_t*)0xB8000)
#define VGA_COLOR 0x0B

static size_t row = 0;
static size_t column = 0;

static uint16_t vga_entry(char c) {
    return (uint16_t)(uint8_t)c | ((uint16_t)VGA_COLOR << 8);
}

static void console_clear(void) {
    volatile uint16_t* video = VGA_MEMORY;
    for (size_t i = 0; i < VGA_WIDTH * VGA_HEIGHT; ++i)
        video[i] = vga_entry(' ');
    row = 0;
    column = 0;
}

static void console_putc(char c) {
    volatile uint16_t* video = VGA_MEMORY;
    if (c == '\n') {
        column = 0;
        if (++row >= VGA_HEIGHT) row = 0;
        return;
    }
    video[row * VGA_WIDTH + column] = vga_entry(c);
    if (++column >= VGA_WIDTH) {
        column = 0;
        if (++row >= VGA_HEIGHT) row = 0;
    }
}

static void console_write(const char* text) {
    while (*text) console_putc(*text++);
}

void kernel_main(void) {
    console_clear();
    console_write("========================================\n");
    console_write("             NEBULA OS 0.1              \n");
    console_write("========================================\n\n");
    console_write("Kernel status: booted successfully\n");
    console_write("Architecture: 32-bit x86 protected mode\n");
    console_write("Boot path: custom BIOS bootloader\n\n");
    console_write("Welcome to NebulaOS.\n");
    console_write("Next milestone: keyboard input and shell.\n\n");
    console_write("Early kernel prototype; no app support yet.\n");
    console_write("Windows .exe compatibility is planned, not implemented.\n");
    for (;;) __asm__ volatile ("hlt");
}

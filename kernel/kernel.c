#include <stddef.h>
#include <stdint.h>

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY ((volatile uint16_t*)0xB8000)
#define VGA_COLOR 0x0B
#define INPUT_LIMIT 79

static size_t row = 0;
static size_t column = 0;
static uint8_t shift_down = 0;
static uint8_t caps_lock = 0;

static const char keymap[128] = {
    [0x02]='1',[0x03]='2',[0x04]='3',[0x05]='4',[0x06]='5',
    [0x07]='6',[0x08]='7',[0x09]='8',[0x0A]='9',[0x0B]='0',
    [0x0C]='-',[0x0D]='=',[0x0E]='\b',[0x0F]='\t',
    [0x10]='q',[0x11]='w',[0x12]='e',[0x13]='r',[0x14]='t',
    [0x15]='y',[0x16]='u',[0x17]='i',[0x18]='o',[0x19]='p',
    [0x1A]='[',[0x1B]=']',[0x1C]='\n',
    [0x1E]='a',[0x1F]='s',[0x20]='d',[0x21]='f',[0x22]='g',
    [0x23]='h',[0x24]='j',[0x25]='k',[0x26]='l',
    [0x27]=';',[0x28]='\'',[0x29]='`',[0x2B]='\\',
    [0x2C]='z',[0x2D]='x',[0x2E]='c',[0x2F]='v',[0x30]='b',
    [0x31]='n',[0x32]='m',[0x33]=',',[0x34]='.',
    [0x35]='/',[0x39]=' '
};

static const char shifted_keymap[128] = {
    [0x02]='!',[0x03]='@',[0x04]='#',[0x05]='$',[0x06]='%',
    [0x07]='^',[0x08]='&',[0x09]='*',[0x0A]='(',[0x0B]=')',
    [0x0C]='_',[0x0D]='+',[0x0E]='\b',[0x0F]='\t',
    [0x10]='Q',[0x11]='W',[0x12]='E',[0x13]='R',[0x14]='T',
    [0x15]='Y',[0x16]='U',[0x17]='I',[0x18]='O',[0x19]='P',
    [0x1A]='{',[0x1B]='}',[0x1C]='\n',
    [0x1E]='A',[0x1F]='S',[0x20]='D',[0x21]='F',[0x22]='G',
    [0x23]='H',[0x24]='J',[0x25]='K',[0x26]='L',
    [0x27]=':',[0x28]='"',[0x29]='~',[0x2B]='|',
    [0x2C]='Z',[0x2D]='X',[0x2E]='C',[0x2F]='V',[0x30]='B',
    [0x31]='N',[0x32]='M',[0x33]='<',[0x34]='>',
    [0x35]='?',[0x39]=' '
};

static inline uint8_t inb(uint16_t port) {
    uint8_t value;
    __asm__ volatile ("inb %1, %0" : "=a"(value) : "Nd"(port));
    return value;
}

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

static void console_scroll(void) {
    volatile uint16_t* video = VGA_MEMORY;
    for (size_t y = 1; y < VGA_HEIGHT; ++y)
        for (size_t x = 0; x < VGA_WIDTH; ++x)
            video[(y - 1) * VGA_WIDTH + x] = video[y * VGA_WIDTH + x];
    for (size_t x = 0; x < VGA_WIDTH; ++x)
        video[(VGA_HEIGHT - 1) * VGA_WIDTH + x] = vga_entry(' ');
    row = VGA_HEIGHT - 1;
}

static void console_newline(void) {
    column = 0;
    ++row;
    if (row >= VGA_HEIGHT) console_scroll();
}

static void console_putc(char c) {
    volatile uint16_t* video = VGA_MEMORY;
    if (c == '\n') {
        console_newline();
        return;
    }
    if (c == '\r') {
        column = 0;
        return;
    }
    if (c == '\b') {
        if (column > 0) {
            --column;
        } else if (row > 0) {
            --row;
            column = VGA_WIDTH - 1;
        } else {
            return;
        }
        video[row * VGA_WIDTH + column] = vga_entry(' ');
        return;
    }
    if (c == '\t') {
        do { console_putc(' '); } while (column % 4 != 0);
        return;
    }
    video[row * VGA_WIDTH + column] = vga_entry(c);
    if (++column >= VGA_WIDTH) console_newline();
}

static void console_write(const char* text) {
    while (*text) console_putc(*text++);
}

static int strings_equal(const char* left, const char* right) {
    while (*left && *right && *left == *right) {
        ++left;
        ++right;
    }
    return *left == *right;
}

static void print_prompt(void) {
    console_write("nebula> ");
}

static void execute_command(const char* command) {
    if (strings_equal(command, "help")) {
        console_write("Commands: help, about, clear, meminfo\n");
    } else if (strings_equal(command, "about")) {
        console_write("NebulaOS 0.2 - custom 32-bit x86 kernel\n");
        console_write("A small OS prototype built from the ground up.\n");
    } else if (strings_equal(command, "clear")) {
        console_clear();
    } else if (strings_equal(command, "meminfo")) {
        console_write("Memory manager: not initialized yet.\n");
        console_write("Kernel load window: 32 KiB maximum.\n");
    } else if (command[0] != '\0') {
        console_write("Unknown command. Type 'help' for commands.\n");
    }
}

static void keyboard_shell(void) {
    char input[INPUT_LIMIT + 1];
    size_t length = 0;
    int extended = 0;

    print_prompt();
    for (;;) {
        if ((inb(0x64) & 1u) == 0) {
            __asm__ volatile ("pause");
            continue;
        }

        uint8_t scan = inb(0x60);
        if (scan == 0xE0) {
            extended = 1;
            continue;
        }
        if (extended) {
            extended = 0;
            continue;
        }

        if (scan == 0x2A || scan == 0x36) {
            shift_down = 1;
            continue;
        }
        if (scan == 0xAA || scan == 0xB6) {
            shift_down = 0;
            continue;
        }
        if (scan == 0x3A) {
            caps_lock = (uint8_t)!caps_lock;
            continue;
        }
        if (scan & 0x80) continue;
        if (scan >= 128) continue;

        char ch = shift_down ? shifted_keymap[scan] : keymap[scan];
        if (!ch) continue;
        if (ch >= 'a' && ch <= 'z' && (shift_down != caps_lock))
            ch = (char)(ch - 'a' + 'A');

        if (ch == '\b') {
            if (length > 0) {
                --length;
                console_putc('\b');
            }
        } else if (ch == '\n') {
            console_putc('\n');
            input[length] = '\0';
            execute_command(input);
            length = 0;
            print_prompt();
        } else if (ch >= 32 && ch <= 126 && length < INPUT_LIMIT) {
            input[length++] = ch;
            console_putc(ch);
        }
    }
}

void kernel_main(void) {
    console_clear();
    console_write("========================================\n");
    console_write("             NEBULA OS 0.2              \n");
    console_write("========================================\n\n");
    console_write("Kernel status: booted successfully\n");
    console_write("Architecture: 32-bit x86 protected mode\n");
    console_write("Input: polling PS/2 keyboard (set 1)\n\n");
    console_write("Type 'help' to list available commands.\n\n");
    keyboard_shell();
}

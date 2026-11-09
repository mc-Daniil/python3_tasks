
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <inttypes.h>

#define FLAG "CTF{pwntools_process_pack_unpack}"

static int read_exact(unsigned char *buf, size_t size) {
    size_t received = 0;

    while (received < size) {
        size_t n = fread(buf + received, 1, size - received, stdin);

        if (n == 0) {
            return 0;
        }

        received += n;
    }

    return 1;
}

static uint64_t unpack64(const unsigned char *buf) {
    uint64_t value = 0;

    for (int i = 0; i < 8; i++) {
        value |= (uint64_t)buf[i] << (8 * i);
    }

    return value;
}

static void pack64(unsigned char *buf, uint64_t value) {
    for (int i = 0; i < 8; i++) {
        buf[i] = (unsigned char)(value >> (8 * i));
    }
}

int main(void) {
    char name[64];
    char answer[64];
    unsigned char payload[8];

    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);

    puts("=== Pwntools Challenge ===");

    // Этап 1: текстовый ввод
    printf("Name: ");

    if (!fgets(name, sizeof(name), stdin)) {
        return 1;
    }

    name[strcspn(name, "\r\n")] = '\0';

    if (strcmp(name, "student") != 0) {
        puts("Wrong name!");
        return 1;
    }

    puts("OK!");

    // Этап 2: арифметика
    puts("TASK|SUM|123|456");
    printf("Answer: ");

    if (!fgets(answer, sizeof(answer), stdin)) {
        return 1;
    }

    if (strtol(answer, NULL, 10) != 579) {
        puts("Wrong answer!");
        return 1;
    }

    puts("OK!");

    // Этап 3: бинарные данные
    puts("TASK|PACK64|0x1122334455667788");
    puts("Send exactly 8 raw bytes (little-endian):");

    if (!read_exact(payload, 8)) {
        return 1;
    }

    if (unpack64(payload) != UINT64_C(0x1122334455667788)) {
        puts("Wrong packed value!");
        return 1;
    }

    puts("OK!");

    // Этап 4: утечка условного адреса
    uint64_t leaked = UINT64_C(0x00007f1234567000);

    puts("TASK|LEAK64");

    unsigned char leak_bytes[8];
    pack64(leak_bytes, leaked);

    // Отправляем только 6 младших байт адреса
    fwrite(leak_bytes, 1, 6, stdout);
    putchar('\n');

    puts("Add 0x120 to leaked address.");
    puts("Send exactly 8 raw bytes (little-endian):");

    if (!read_exact(payload, 8)) {
        return 1;
    }

    if (unpack64(payload) != leaked + 0x120) {
        puts("Wrong address!");
        return 1;
    }

    printf("FLAG|%s\n", FLAG);

    return 0;
}

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <string.h>

#define FIFO_NAME "myfifo"
#define NUM_COUNT 7
#define BUFFER_SIZE 256

int main() {
    int fd;
    int numbers[NUM_COUNT];
    char info_string[BUFFER_SIZE];
    int sum = 0;

    // Open the FIFO for reading
    fd = open(FIFO_NAME, O_RDONLY);
    if (fd == -1) {
        perror("open");
        exit(EXIT_FAILURE);
    }

    // Read the numbers from the FIFO
    read(fd, numbers, sizeof(numbers));

    // Read the string from the FIFO
    read(fd, info_string, BUFFER_SIZE);

    // Calculate the sum of the numbers
    for (int i = 0; i < NUM_COUNT; i++) {
        sum += numbers[i];
    }

    // Close the FIFO
    close(fd);

    printf("Receiver: Sum of received numbers is %d\n", sum);
    printf("Receiver: Received string is '%s'\n", info_string);
    return 0;
}

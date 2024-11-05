#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

#define FIFO_NAME "myfifo"
#define NUM_COUNT 7

int main() {
    int fd;
    int numbers[NUM_COUNT];
    int sum = 0;

    // Open the FIFO for reading
    fd = open(FIFO_NAME, O_RDONLY);
    if (fd == -1) {
        perror("open");
        exit(EXIT_FAILURE);
    }

    // Read the numbers from the FIFO
    read(fd, numbers, sizeof(numbers));

    // Calculate the sum of the numbers
    for (int i = 0; i < NUM_COUNT; i++) {
        sum += numbers[i];
    }

    // Close the FIFO
    close(fd);

    printf("Receiver: Sum of received numbers is %d\n", sum);
    return 0;
}

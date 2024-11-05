#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <time.h>
#include <string.h>

#define FIFO_NAME "myfifo"
#define NUM_COUNT 7
#define INFO_STRING "Pham Van Ngoc Vinh 22AD059"

int main() {
    int fd;
    int numbers[NUM_COUNT];
    srand(time(NULL));

    // Generate random numbers
    for (int i = 0; i < NUM_COUNT; i++) {
        numbers[i] = rand() % 100; // Random numbers between 0 and 99
    }

    // Create the FIFO if it does not exist
    mkfifo(FIFO_NAME, 0666);

    // Open the FIFO for writing
    fd = open(FIFO_NAME, O_WRONLY);
    if (fd == -1) {
        perror("open");
        exit(EXIT_FAILURE);
    }

    // Write the numbers to the FIFO
    write(fd, numbers, sizeof(numbers));

    // Write the string to the FIFO
    write(fd, INFO_STRING, strlen(INFO_STRING) + 1);

    // Close the FIFO
    close(fd);

    printf("Sender: Sent numbers and string to FIFO\n");
    return 0;
}

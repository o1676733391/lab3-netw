#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#include <pwd.h>
#include <grp.h>
#include <time.h>
#include "args.h"

void print_file_info(struct stat file_stat, char *filename, int args);
void list_directory(const char *dir, int args);
void print_file(const char *path, const char *name, int args);
int compare_files(const struct dirent **a, const struct dirent **b, int args);
void sort_files(struct dirent **file_list, int count, int args);

int main(int argc, char *argv[]) {
    char directory[256] = {0};
    int args = get_args(argc, argv, directory);

    // If no directory is specified, default to the current directory
    if (directory[0] == '\0') {
        strcpy(directory, ".");
    }

    // If -d flag is present, only list the directory itself
    if (args & ARG_d) {
        print_file(".", directory, args);
    } else {
        // List directory contents
        list_directory(directory, args);
    }

    return 0;
}

void list_directory(const char *dir, int args) {
    struct dirent **file_list;
    int n;

    // Read directory contents
    n = scandir(dir, &file_list, NULL, alphasort);

    if (n < 0) {
        perror("scandir");
        return;
    }

    // Sort the files if needed
    sort_files(file_list, n, args);

    // Print files based on the parsed flags
    for (int i = 0; i < n; i++) {
        // Skip hidden files unless the -a flag is set
        if (!(args & ARG_a) && file_list[i]->d_name[0] == '.') {
            continue;
        }

        print_file(dir, file_list[i]->d_name, args);
        free(file_list[i]);
    }
    free(file_list);
}

void print_file(const char *path, const char *name, int args) {
    char full_path[512];
    snprintf(full_path, sizeof(full_path), "%s/%s", path, name);

    struct stat file_stat;
    if (stat(full_path, &file_stat) == -1) {
        perror("stat");
        return;
    }

    // If the -l flag is present, print detailed information
    if (args & ARG_l) {
        print_file_info(file_stat, (char*)name, args);
    } else {
        printf("%s\n", name);
    }
}

void print_file_info(struct stat file_stat, char *filename, int args) {
    // Print file permissions, number of links, owner, group, size, and name
    printf((S_ISDIR(file_stat.st_mode)) ? "d" : "-");
    printf((file_stat.st_mode & S_IRUSR) ? "r" : "-");
    printf((file_stat.st_mode & S_IWUSR) ? "w" : "-");
    printf((file_stat.st_mode & S_IXUSR) ? "x" : "-");
    printf((file_stat.st_mode & S_IRGRP) ? "r" : "-");
    printf((file_stat.st_mode & S_IWGRP) ? "w" : "-");
    printf((file_stat.st_mode & S_IXGRP) ? "x" : "-");
    printf((file_stat.st_mode & S_IROTH) ? "r" : "-");
    printf((file_stat.st_mode & S_IWOTH) ? "w" : "-");
    printf((file_stat.st_mode & S_IXOTH) ? "x" : "-");
    
    // Print inode if -i flag is present
    if (args & ARG_i) {
        printf(" %ld", file_stat.st_ino);
    }

    // Print number of links
    printf(" %ld", file_stat.st_nlink);

    // Print owner and group if -n flag is not present
    if (!(args & ARG_n)) {
        struct passwd *pwd = getpwuid(file_stat.st_uid);
        struct group *grp = getgrgid(file_stat.st_gid);
        printf(" %s %s", pwd->pw_name, grp->gr_name);
    } else {
        // Numeric IDs
        printf(" %d %d", file_stat.st_uid, file_stat.st_gid);
    }

    // Print file size
    if (args & ARG_h) {
        char size_str[10];
        human_readable_size(file_stat.st_size, size_str);
        printf(" %s", size_str);
    } else {
        printf(" %ld", file_stat.st_size);
    }

    // Print last modification time
    char timebuf[80];
    struct tm *tm_info = localtime(&(file_stat.st_mtime));
    strftime(timebuf, 80, "%b %d %H:%M", tm_info);
    printf(" %s", timebuf);

    // Print file name
    printf(" %s\n", filename);
}

void sort_files(struct dirent **file_list, int count, int args) {
    // Sort by modification time if -t flag is set
    if (args & ARG_t) {
        qsort(file_list, count, sizeof(struct dirent *), (int (*)(const void *, const void *))compare_files);
    }
}

int compare_files(const struct dirent **a, const struct dirent **b, int args) {
    struct stat stat_a, stat_b;
    stat((*a)->d_name, &stat_a);
    stat((*b)->d_name, &stat_b);

    // Compare by modification time or reverse order if -r flag is set
    if (args & ARG_r) {
        return stat_a.st_mtime - stat_b.st_mtime;
    } else {
        return stat_b.st_mtime - stat_a.st_mtime;
    }
}

void human_readable_size(long size, char *output) {
    const char *sizes[] = {"B", "KB", "MB", "GB", "TB"};
    int div = 0;
    long rem = 0;

    while (size >= 1024 && div < (sizeof(sizes) / sizeof(*sizes))) {
        rem = (size % 1024);
        div++;
        size /= 1024;
    }

    sprintf(output, "%ld.%ld %s", size, rem, sizes[div]);
}

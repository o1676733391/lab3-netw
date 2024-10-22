#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <time.h>
#include <pwd.h>
#include <grp.h>
#include "args.h"

void print_file_info(struct stat *file_stat, char *filename, int args);
void list_directory(const char *directory, int args);

// Function to handle listing
int main(int argc, char *argv[]) {
    char directory[256] = {0};  // To store the directory path
    int args = get_args(argc, argv, directory);  // Parse arguments

    // List files in the directory
    list_directory(directory, args);

    return 0;
}

void list_directory(const char *directory, int args) {
    DIR *dir;
    struct dirent *entry;
    struct stat file_stat;
    char filepath[512];

    if ((dir = opendir(directory)) == NULL) {
        perror("opendir() error");
        exit(1);
    }

    while ((entry = readdir(dir)) != NULL) {
        // Skip hidden files unless -a is specified
        if (!(args & ARG_a) && entry->d_name[0] == '.')
            continue;

        snprintf(filepath, sizeof(filepath), "%s/%s", directory, entry->d_name);

        if (stat(filepath, &file_stat) == -1) {
            perror("stat() error");
            continue;
        }

        // Print file information based on arguments
        print_file_info(&file_stat, entry->d_name, args);
    }

    closedir(dir);
}

// Function to print file info based on the flags
void print_file_info(struct stat *file_stat, char *filename, int args) {
    char timebuf[80];
    struct passwd *pw;
    struct group *gr;
    char perms[11] = "----------";

    // -l: Long listing format
    if (args & ARG_l) {
        // File type and permissions
        perms[0] = S_ISDIR(file_stat->st_mode) ? 'd' : '-';
        perms[1] = (file_stat->st_mode & S_IRUSR) ? 'r' : '-';
        perms[2] = (file_stat->st_mode & S_IWUSR) ? 'w' : '-';
        perms[3] = (file_stat->st_mode & S_IXUSR) ? 'x' : '-';
        perms[4] = (file_stat->st_mode & S_IRGRP) ? 'r' : '-';
        perms[5] = (file_stat->st_mode & S_IWGRP) ? 'w' : '-';
        perms[6] = (file_stat->st_mode & S_IXGRP) ? 'x' : '-';
        perms[7] = (file_stat->st_mode & S_IROTH) ? 'r' : '-';
        perms[8] = (file_stat->st_mode & S_IWOTH) ? 'w' : '-';
        perms[9] = (file_stat->st_mode & S_IXOTH) ? 'x' : '-';

        // -n: Numeric user and group IDs instead of names
        if (args & ARG_n) {
            printf("%s %ld %d %d %ld ", perms, file_stat->st_nlink, file_stat->st_uid, file_stat->st_gid, file_stat->st_size);
        } else {
            pw = getpwuid(file_stat->st_uid);
            gr = getgrgid(file_stat->st_gid);
            printf("%s %ld %s %s %ld ", perms, file_stat->st_nlink, pw->pw_name, gr->gr_name, file_stat->st_size);
        }

        // Format time based on -u flag (access time)
        strftime(timebuf, sizeof(timebuf), "%b %d %H:%M", localtime(&(args & ARG_u ? file_stat->st_atime : file_stat->st_mtime)));
        printf("%s ", timebuf);
    }

    // -i: Show inode number
    if (args & ARG_i) {
        printf("%ld ", file_stat->st_ino);
    }

    // -s: Show file sizes
    if (args & ARG_s) {
        // -h: Human-readable sizes
        if (args & ARG_h) {
            double size = (double)file_stat->st_size;
            const char *suffix[] = {"B", "KB", "MB", "GB"};
            int i = 0;
            while (size > 1024 && i < 3) {
                size /= 1024;
                i++;
            }
            printf("%4.1f%s ", size, suffix[i]);
        } else {
            printf("%ld ", file_stat->st_size);
        }
    }

    // Print the filename
    printf("%s\n", filename);
}

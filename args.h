// Define additional argument flags
#define ARG_l 1    // List in long format
#define ARG_a 2    // Include hidden files
#define ARG_i 4    // Show inode numbers
#define ARG_r 8    // Reverse order
#define ARG_t 16   // Sort by modification time
#define ARG_u 32   // Use access time for sorting
#define ARG_s 64   // Print file sizes
#define ARG_d 128  // List directory itself, not its contents
#define ARG_n 256  // Use numeric IDs instead of names
#define ARG_h 512  // Human-readable sizes

// File: args.h
// Purpose: parsing these arguments for the ls program 
// Author: Brett Holman

int get_args(int argc, char *argv[], char *directory);
int iterate_args(int argc, char *argv[], char *directory);
int get_arg(char * arg, int init);

int iterate_args(int argc, char *argv[], char *directory){

    // Base case    
    if(argc == 1) return 0;

    // Don't get args if it's the directory 
    if(argv[argc-1][0] != '-'){
        if(directory[0] != '\0'){
            return -1;
        }
        strcpy(directory, argv[argc-1]); 
        
        // don't get the character for the directory
        return iterate_args(--argc, argv, directory);
    }
    else {
        return iterate_args(--argc, argv, directory) | get_arg(argv[argc], 1);    
    }
}

int get_arg(char * arg, int init){

    // Searching for non-flag arg
    // checking flags
    int args = 0;

    // End of char* (base case)
    if(!arg[init]) return 0;

    // Check for args
    switch(arg[init]){
        case 'l': args |= ARG_l; break;
        case 'a': args |= ARG_a; break;
        case 'i': args |= ARG_i; break;
        case 'r': args |= ARG_r; break;
        case 't': args |= ARG_t; break;
        case 'u': args |= ARG_u; break;
        case 's': args |= ARG_s; break;
        case 'd': args |= ARG_d; break;
        case 'n': args |= ARG_n; break;
        case 'h': args |= ARG_h; break;
        default: return -1;
    }

    // Check the other characters
    return args | get_arg(arg, ++init);
}

// interpret CLI args
int get_args(int argc, char *argv[], char *directory){

    int args = 0;
   
    // if length == 1, no args passed 
    if(argc == 1){
        directory[0] = '.';
        return 0;
    }
    
    // For this program, the only non-flag is the directory for ls
    args = iterate_args(argc, argv, directory);
    
    if(!directory[0])
        directory[0] = '.';

    return args;
}

#ifndef HASHER_H
#define HASHER_H

#define BLOCK_SIZE 16384

typedef struct {
    uint8_t *ptr;
    int size;
    int allocated;
    int logical;
} HASH;

HASH *HASHER(char **filelist, int piece_length);

#endif

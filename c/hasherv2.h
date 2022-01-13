#ifndef HASHERV2_H
#define HASHERV2_H

#include <stdint.h>

typedef uint8_t uint8;

typedef struct { // Hash Result Object
    uint8 *piece_layer;
    uint8 *pieces_root;
} HASHV2;

HASHV2 *HasherV2(char *path, unsigned piece_length);

#endif

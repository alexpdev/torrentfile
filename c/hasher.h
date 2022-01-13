#ifndef HASHER_H
#define HASHER_H

#include <stdint.h>

typedef uint8_t uint8;

typedef struct {
    uint8 *ptr;
    int size;
    int allocated;
    int logical;
} HASH;

typedef struct { // Hash Result Object
    uint8 *piece_layer;
    uint8 *pieces_root;
} HASHV2;

typedef struct { // Hash Result Object
    uint8 *piece_layerV3;
    uint8 *pieces_root;
    uint8 *hashv1;
} HASHHYBRID;

HASH *HASHER(char **filelist, unsigned piece_length);
HASHV2 *HasherV2(char *path, unsigned piece_length);
HASHHYBRID *HasherHybrid(char *path, unsigned piece_length);

#endif

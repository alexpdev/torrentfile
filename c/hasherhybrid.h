#ifndef HASHERHYBRID_H
#define HASHERHYBRID_H

#include <stdint.h>

typedef uint8_t uint8;


typedef struct { // Hash Result Object
    uint8 *piece_layerV3;
    uint8 *pieces_root;
    uint8 *hashv1;
} HASHHYBRID;


HASHHYBRID *HasherHybrid(char *path, unsigned piece_length);

#endif

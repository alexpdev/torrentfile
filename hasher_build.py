#! /usr/bin/python3
# -*- coding: utf-8 -*-

import os
from cffi import FFI

ffibuilder = FFI() # 'hasher_build.py:FFI_BUILDER'

HEADER = '''
typedef struct {
    uint8_t *ptr;
    int size;
    int allocated;
    int logical;
} HASH;

typedef struct {
    uint8_t *piece_layer;
    uint8_t *pieces_root;
} HASHV2;

typedef struct {
    uint8_t *piece_layerV3;
    uint8_t *pieces_root;
    uint8_t *hashv1;
} HASHHYBRID;

HASH *HASHER(char **filelist, int piece_length);
HASHV2 *HasherV2(char *path, unsigned piece_length);
HASHHYBRID *HasherHybrid(char *path, unsigned piece_length);
'''

ffibuilder.cdef(HEADER)

path = "c"
filelist = os.listdir("c")
sources = [
    "hasher.c",
    "hasherv2.c",
    "hasherhybrid.c",
    "sha1.c",
    "sha256.c",
]


ffibuilder.set_source(
    "c_hasher",
    """
    #include "sha256.h"
    #include "sha1.h"
    #include "hasher.h"
    #include "hasherv2.h"
    #include "hasherhybrid.h"
    """,
    sources=sources)

if __name__ == "__main__":
    ffibuilder.compile()

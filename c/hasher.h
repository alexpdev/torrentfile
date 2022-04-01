/*
##############################################################################
#    Copyright (C) 2021-current alexpdev
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
##############################################################################
*/

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

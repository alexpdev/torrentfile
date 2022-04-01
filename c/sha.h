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
#ifndef SHA_H
#define SHA_H

#include "stdint.h"

typedef struct
{
    uint32_t state[5];
    uint32_t count[2];
    uint8_t buffer[64];
} SHA1_CTX;

void SHA1Transform(uint32_t state[5], const uint8_t buffer[64]);
void SHA1Init(SHA1_CTX * context);
void SHA1Update(SHA1_CTX * context, const uint8_t *data, uint32_t len);
void SHA1Final(uint8_t digest[20], SHA1_CTX * context);
void SHA1(uint8_t *hash_out, const uint8_t *str, int len);

typedef struct {
	uint8 *hash;
	uint8 chunk[64];
	uint8 *chunk_pos;
	size_t space_left;
	size_t total_len;
	uint32_t h[8];
} SHA256_CTX;

void SHA256(uint8 *hash, const void *input, size_t len);
void SHA256Init(SHA256_CTX *context, uint8 *hash);
void SHA256Update(SHA256_CTX *context, const void *data, size_t len);
void SHA256Final(SHA256_CTX *context);

#endif

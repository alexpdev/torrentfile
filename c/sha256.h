#ifndef SHA256_H
#define SHA256_H

#include <stdint.h>
#include <string.h>

typedef uint8_t uint8;

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

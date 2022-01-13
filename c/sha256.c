#include <stdlib.h>
#include <stdint.h>
#include "sha256.h"

#define rrot(val, cnt) ((val >> cnt) | (val << (32 - cnt)))

static inline void consume_chunk(uint32_t *h, const uint8_t *p)
{
    unsigned i, j;
    uint32_t ah[8];
    for (i = 0; i < 8; i++)
        ah[i] = h[i];
    uint32_t w[16];
    for (i = 0; i < 4; i++) {
        for (j = 0; j < 16; j++) {
            if (i == 0) {
                w[j] = (uint32_t)p[0] << 24 | (uint32_t)p[1] << 16 | (uint32_t)p[2] << 8 | (uint32_t)p[3];
                p += 4;
            } else {
                const uint32_t s0 = rrot(w[(j + 1) & 0xf], 7) ^ rrot(w[(j + 1) & 0xf], 18) ^ (w[(j + 1) & 0xf] >> 3);
                const uint32_t s1 = rrot(w[(j + 14) & 0xf], 17) ^ rrot(w[(j + 14) & 0xf], 19) ^ (w[(j + 14) & 0xf] >> 10);
                w[j] = w[j] + s0 + w[(j + 9) & 0xf] + s1;
            }
            const uint32_t s1 = rrot(ah[4], 6) ^ rrot(ah[4], 11) ^ rrot(ah[4], 25);
            const uint32_t ch = (ah[4] & ah[5]) ^ (~ah[4] & ah[6]);

            static const uint32_t k[] = {
                0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4,
                0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe,
                0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f,
                0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
                0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc,
                0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
                0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116,
                0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
                0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7,
                0xc67178f2};

            const uint32_t temp1 = ah[7] + s1 + ch + k[i << 4 | j] + w[j];
            const uint32_t s0 = rrot(ah[0], 2) ^ rrot(ah[0], 13) ^ rrot(ah[0], 22);
            const uint32_t maj = (ah[0] & ah[1]) ^ (ah[0] & ah[2]) ^ (ah[1] & ah[2]);
            const uint32_t temp2 = s0 + maj;
            ah[7] = ah[6];
            ah[6] = ah[5];
            ah[5] = ah[4];
            ah[4] = ah[3] + temp1;
            ah[3] = ah[2];
            ah[2] = ah[1];
            ah[1] = ah[0];
            ah[0] = temp1 + temp2;
        }
    }
    for (i = 0; i < 8; i++)
        h[i] += ah[i];
}

void SHA256Init(SHA256_CTX *context, uint8_t *hash)
{
    context->hash = hash;
    context->chunk_pos = context->chunk;
    context->space_left = 64;
    context->total_len = 0;
    context->h[0] = 0x6a09e667;
    context->h[1] = 0xbb67ae85;
    context->h[2] = 0x3c6ef372;
    context->h[3] = 0xa54ff53a;
    context->h[4] = 0x510e527f;
    context->h[5] = 0x9b05688c;
    context->h[6] = 0x1f83d9ab;
    context->h[7] = 0x5be0cd19;
}

void SHA256Update(SHA256_CTX *context, const void *data, size_t len)
{
    context->total_len += len;
    const uint8_t *p = data;
    while (len > 0) {
        if (context->space_left == 64 && len >= 64) {
            consume_chunk(context->h, p);
            len -= 64;
            p += 64;
            continue;
        }
        const size_t consumed_len = len < context->space_left ? len : context->space_left;
        memcpy(context->chunk_pos, p, consumed_len);
        context->space_left -= consumed_len;
        len -= consumed_len;
        p += consumed_len;
        if (context->space_left == 0) {
            consume_chunk(context->h, context->chunk);
            context->chunk_pos = context->chunk;
            context->space_left = 64;
        } else {
            context->chunk_pos += consumed_len;
        }
    }
}

void SHA256Final(SHA256_CTX *context)
{
    uint8_t *pos = context->chunk_pos;
    size_t space_left = context->space_left;
    uint32_t *const h = context->h;
    *pos++ = 0x80;
    --space_left;
    if (space_left < 8) {
        memset(pos, 0x00, space_left);
        consume_chunk(h, context->chunk);
        pos = context->chunk;
        space_left = 64;
    }
    const size_t left = space_left - 8;
    memset(pos, 0x00, left);
    pos += left;
    size_t len = context->total_len;
    pos[7] = (uint8_t)(len << 3);
    len >>= 5;
    int i;
    for (i = 6; i >= 0; --i) {
        pos[i] = (uint8_t)len;
        len >>= 8;
    }
    consume_chunk(h, context->chunk);
    int j;
    uint8_t *const hash = context->hash;
    for (i = 0, j = 0; i < 8; i++) {
        hash[j++] = (uint8_t)(h[i] >> 24);
        hash[j++] = (uint8_t)(h[i] >> 16);
        hash[j++] = (uint8_t)(h[i] >> 8);
        hash[j++] = (uint8_t)h[i];
    }
}

void SHA256(uint8_t *hash, const void *input, size_t len)
{
    SHA256_CTX ctx;
    SHA256Init(&ctx, hash);
    SHA256Update(&ctx, input, len);
    SHA256Final(&ctx);
    hash[32] = '\0';
}

#define SHA1HANDSOFF

#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "sha.h"

typedef uint8_t uint8;

#define rol(value, bits) (((value) << (bits)) | ((value) >> (32 - (bits))))

#if BYTE_ORDER == LITTLE_ENDIAN
#define blk0(i) (block->l[i] = (rol(block->l[i],24)&0xFF00FF00) \
    |(rol(block->l[i],8)&0x00FF00FF))
#elif BYTE_ORDER == BIG_ENDIAN
#define blk0(i) block->l[i]
#else
#error "Endianness not defined!"
#endif
#define blk(i) (block->l[i&15] = rol(block->l[(i+13)&15]^block->l[(i+8)&15] \
    ^block->l[(i+2)&15]^block->l[i&15],1))

#define R0(v,w,x,y,z,i) z+=((w&(x^y))^y)+blk0(i)+0x5A827999+rol(v,5);w=rol(w,30);
#define R1(v,w,x,y,z,i) z+=((w&(x^y))^y)+blk(i)+0x5A827999+rol(v,5);w=rol(w,30);
#define R2(v,w,x,y,z,i) z+=(w^x^y)+blk(i)+0x6ED9EBA1+rol(v,5);w=rol(w,30);
#define R3(v,w,x,y,z,i) z+=(((w|x)&y)|(w&x))+blk(i)+0x8F1BBCDC+rol(v,5);w=rol(w,30);
#define R4(v,w,x,y,z,i) z+=(w^x^y)+blk(i)+0xCA62C1D6+rol(v,5);w=rol(w,30);

void SHA1Transform(uint32_t state[5], const uint8 buffer[64])
{
    uint32_t a, b, c, d, e;

    typedef union
    {
        uint8 c[64];
        uint32_t l[16];
    } CHAR64LONG16;

#ifdef SHA1HANDSOFF
    CHAR64LONG16 block[1];
    memcpy(block, buffer, 64);
#else
    CHAR64LONG16 *block = (const CHAR64LONG16 *) buffer;
#endif
    /* Copy context->state[] to working vars */
    a = state[0]; b = state[1];
    c = state[2]; d = state[3];
    e = state[4];
    R0(a, b, c, d, e, 0); R0(e, a, b, c, d, 1);
    R0(d, e, a, b, c, 2); R0(c, d, e, a, b, 3);
    R0(b, c, d, e, a, 4); R0(a, b, c, d, e, 5);
    R0(e, a, b, c, d, 6); R0(d, e, a, b, c, 7);
    R0(c, d, e, a, b, 8); R0(b, c, d, e, a, 9);
    R0(a, b, c, d, e, 10); R0(e, a, b, c, d, 11);
    R0(d, e, a, b, c, 12); R0(c, d, e, a, b, 13);
    R0(b, c, d, e, a, 14); R0(a, b, c, d, e, 15);
    R1(e, a, b, c, d, 16); R1(d, e, a, b, c, 17);
    R1(c, d, e, a, b, 18); R1(b, c, d, e, a, 19);
    R2(a, b, c, d, e, 20); R2(e, a, b, c, d, 21);
    R2(d, e, a, b, c, 22); R2(c, d, e, a, b, 23);
    R2(b, c, d, e, a, 24); R2(a, b, c, d, e, 25);
    R2(e, a, b, c, d, 26); R2(d, e, a, b, c, 27);
    R2(c, d, e, a, b, 28); R2(b, c, d, e, a, 29);
    R2(a, b, c, d, e, 30); R2(e, a, b, c, d, 31);
    R2(d, e, a, b, c, 32); R2(c, d, e, a, b, 33);
    R2(b, c, d, e, a, 34); R2(a, b, c, d, e, 35);
    R2(e, a, b, c, d, 36); R2(d, e, a, b, c, 37);
    R2(c, d, e, a, b, 38); R2(b, c, d, e, a, 39);
    R3(a, b, c, d, e, 40); R3(e, a, b, c, d, 41);
    R3(d, e, a, b, c, 42); R3(c, d, e, a, b, 43);
    R3(b, c, d, e, a, 44); R3(a, b, c, d, e, 45);
    R3(e, a, b, c, d, 46); R3(d, e, a, b, c, 47);
    R3(c, d, e, a, b, 48); R3(b, c, d, e, a, 49);
    R3(a, b, c, d, e, 50); R3(e, a, b, c, d, 51);
    R3(d, e, a, b, c, 52); R3(c, d, e, a, b, 53);
    R3(b, c, d, e, a, 54); R3(a, b, c, d, e, 55);
    R3(e, a, b, c, d, 56); R3(d, e, a, b, c, 57);
    R3(c, d, e, a, b, 58); R3(b, c, d, e, a, 59);
    R4(a, b, c, d, e, 60); R4(e, a, b, c, d, 61);
    R4(d, e, a, b, c, 62); R4(c, d, e, a, b, 63);
    R4(b, c, d, e, a, 64); R4(a, b, c, d, e, 65);
    R4(e, a, b, c, d, 66); R4(d, e, a, b, c, 67);
    R4(c, d, e, a, b, 68); R4(b, c, d, e, a, 69);
    R4(a, b, c, d, e, 70); R4(e, a, b, c, d, 71);
    R4(d, e, a, b, c, 72); R4(c, d, e, a, b, 73);
    R4(b, c, d, e, a, 74); R4(a, b, c, d, e, 75);
    R4(e, a, b, c, d, 76); R4(d, e, a, b, c, 77);
    R4(c, d, e, a, b, 78); R4(b, c, d, e, a, 79);
    state[0] += a; state[1] += b; state[2] += c;
    state[3] += d; state[4] += e;
    a = b = c = d = e = 0;
    memset(block, '\0', sizeof(block));
}

void SHA1Init(SHA1_CTX * context)
{
    context->state[0] = 0x67452301;
    context->state[1] = 0xEFCDAB89;
    context->state[2] = 0x98BADCFE;
    context->state[3] = 0x10325476;
    context->state[4] = 0xC3D2E1F0;
    context->count[0] = context->count[1] = 0;
}

void SHA1Update(SHA1_CTX * context, const uint8 *data, uint32_t len)
{
    uint32_t i;
    uint32_t j;
    j = context->count[0];

    if ((context->count[0] += len << 3) < j)
        context->count[1]++;

    context->count[1] += (len >> 29);
    j = (j >> 3) & 63;

    if ((j + len) > 63){
        memcpy(&context->buffer[j], data, (i = 64 - j));
        SHA1Transform(context->state, context->buffer);

        for (; i + 63 < len; i += 64){
            SHA1Transform(context->state, &data[i]);
        }
        j = 0;
    }

    else i = 0;
    memcpy(&context->buffer[j], &data[i], len - i);
}

void SHA1Final(uint8 digest[20], SHA1_CTX *context)
{
    unsigned int i;
    uint8 finalcount[8];
    uint8 c;
    for (i = 0; i < 8; i++){
        finalcount[i] = (uint8) ((context->count[(i >= 4 ? 0 : 1)] >> ((3 - (i & 3)) * 8)) & 255);
    }
    c = 0200;
    SHA1Update(context, &c, 1);
    while ((context->count[0] & 504) != 448){
        c = 0000;
        SHA1Update(context, &c, 1);
    }
    SHA1Update(context, finalcount, 8); /* Should cause a SHA1Transform() */
    for (i = 0; i < 20; i++){
        digest[i] = (uint8)
            ((context->state[i >> 2] >> ((3 - (i & 3)) * 8)) & 255);
    }
    memset(context, '\0', sizeof(*context));
    memset(&finalcount, '\0', sizeof(finalcount));
}

void SHA1(uint8 *hash_out, const uint8 *str, int len)
{
    SHA1_CTX ctx;
    unsigned int ii;
    SHA1Init(&ctx);
    for (ii=0; ii<len; ii+=1)
        SHA1Update(&ctx, (const uint8 *)str + ii, 1);
    SHA1Final((uint8 *)hash_out, &ctx);
    hash_out[20] = '\0';
}

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

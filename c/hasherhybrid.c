#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include "sha256.h"
#include "sha1.h"
#include "hasherhybrid.h"

#define BLOCKSIZE 16384
#define HASHSIZE 32
#define V1HASHSIZE 20

typedef uint8_t uint8;

typedef struct Node {     // Linked List Node Item
    uint8 *hash;
    struct Node *next;
} Node;


typedef struct {  // Linked List of layerV3 hashes
    Node *start;
    Node *end;
    int count;
} LayerV3;


// typedef struct { // Hash Result Object
//     uint8 *piece_layerV3;
//     uint8 *pieces_root;
//     uint8 *hashv1;
// } HASHHYBRID;


LayerV3 *newLayerV3()
{
    // Creates a new linked list
    LayerV3 *layerV3 = (LayerV3 *)malloc(sizeof(LayerV3));
    layerV3->start = NULL;
    layerV3->end = NULL;
    layerV3->count = 0;
    return layerV3;
}


void hex_digest(uint8 *hash)
{
    for (int i = 0; i < HASHSIZE; i++)
    {
        printf("%02x", hash[i]);
    }
}


void showLayer(LayerV3 *layerV3)
{
    printf("\n\n");
    Node *current = layerV3->start;
    while (current != NULL)
    {
        printf("----  ");
        hex_digest(current->hash);
        printf("  ----\n");
        current = current->next;
    }
    printf("\n\n");
}


uint8 *join_hash(uint8 *hash1, uint8 *hash2)
{
    uint8 *joined = (uint8 *)malloc(HASHSIZE * 2);
    for (int i = 0; i < HASHSIZE; i++){
        joined[i] = hash1[i];
    }

    for (int j = 0; j < HASHSIZE; j++){
        joined[HASHSIZE+j] = hash2[j];
    }
    uint8 *hash3 = (uint8 *)malloc(HASHSIZE);
    SHA256(hash3, joined, HASHSIZE*2);
    return hash3;
}


void deleteLayerV3(LayerV3 *layerV3)
{
    Node *start = layerV3->start;
    while (start)
    {
        Node *next = start->next;
        free(start->hash);
        free(start);
        start = next;
    }
    free(layerV3);
}


void add_node(LayerV3 *layerV3, uint8 *hash)
{
    Node *newnode = (Node *)malloc(sizeof(Node));
    newnode->hash = hash;
    newnode->next = NULL;
    if (layerV3->start)
    {
        Node *end = layerV3->end;
        end->next = newnode;
        layerV3->end = newnode;
    }
    else
    {
        layerV3->start = newnode;
        layerV3->end = newnode;
    }
    layerV3->count = layerV3->count + 1;
}


uint8 *getPadding()
{
    uint8 *padding = (uint8 *)malloc(HASHSIZE);
    for (int i = 0; i < HASHSIZE; i++)
    {
        padding[i] = 0;
    }
    return padding;
}


uint8 *MerkleRoot(LayerV3 *layerV3)
{
    int count = layerV3->count;
    while (count > 1)
    {
        printf("\nCount = %d\n", count);
        Node *current = layerV3->start;
        Node *next = current->next;
        Node *last = current;
        int index = 0;
        while (true)
        {
            uint8 *partial = join_hash(current->hash, next->hash);
            last->hash = partial;
            index++;
            current = next->next;
            if (!current) break;
            next = current->next;
            last = last->next;
        }
        count = index;
        layerV3->end = last;
        last->next = NULL;
    }
    printf("MerkleRoot");
    showLayer(layerV3);
    return layerV3->start->hash;
}


uint8 *getPadPiece(unsigned n)
{
    uint8 *padding;
    LayerV3 *layerV3 = newLayerV3();
    for (int i = 0; i < n; i++)
    {
        padding = getPadding();
        add_node(layerV3, padding);
    }
    return MerkleRoot(layerV3);
}


unsigned extend_v1hash(uint8 *hash, uint8 *v1pieces, unsigned v1length)
{
    unsigned size = v1length + V1HASHSIZE;
    uint8 v1piece[size];
    for (int i = 0; i < v1length; i++){
        v1piece[i] = v1pieces[i];
    }
    for (int j=0; j < V1HASHSIZE; j++){
        v1piece[v1length + j] = hash[j];
    }
    v1pieces = v1piece;
    return size;
}


HASHHYBRID *HasherHybrid(char *path, unsigned piece_length)
{
    unsigned amount, next_pow2, total, remaining, blocks_per_piece;
    LayerV3 *layerV3;
    LayerV3 *layerV3_hashes = newLayerV3();
    FILE *fptr = fopen(path, "rb");
    uint8 *buffer = (uint8 *)malloc(BLOCKSIZE);
    uint8 v1pieces[] = {};
    unsigned v1length = 0;
    total = 0;
    blocks_per_piece = (unsigned) floor(piece_length / BLOCKSIZE);
    while (true)
    {
        uint8 *v1buffer = (uint8 *)malloc(piece_length);
        unsigned bufsize = 0;
        layerV3 = newLayerV3();
        uint8 *piece;
        for (int i = 0; i < blocks_per_piece; i++)
        {
            amount = fread(buffer, 1, BLOCKSIZE, fptr);
            total += amount;
            if (!amount) break;
            uint8 *hash = (uint8 *)malloc(amount);
            SHA256(hash, buffer, amount);
            add_node(layerV3, hash);
            for (int bufi = 0; bufi < BLOCKSIZE; bufi++)
            {
                v1buffer[bufsize] = buffer[bufi];
                bufsize += 1;
            }
        }
        if (!layerV3->count) break;
        if (layerV3->count < blocks_per_piece)
        {
            if (!layerV3_hashes->count)
            {
                next_pow2 = 1 << (unsigned) floor((log(total)/log(2)) + 1);
                remaining = (unsigned) ((next_pow2 - total) / BLOCKSIZE) + 1;
            }
            else
            {
                remaining = blocks_per_piece - layerV3->count;
            }
            printf("Remaining = %d; count = %d.", remaining, layerV3->count);
            uint8 *padding;
            for (int i = 0; i < remaining; i++)
            {
                padding = getPadding();
                add_node(layerV3, padding);
            }
        }
        uint8 *v1hash = (uint8 *)malloc(V1HASHSIZE);
        SHA1(v1hash, v1buffer, bufsize);
        piece = MerkleRoot(layerV3);
        add_node(layerV3_hashes, piece);
        v1length = extend_v1hash(v1hash, v1pieces, v1length);
    }
    uint8 *piece_layerV3 = (uint8 *)malloc(HASHSIZE * layerV3_hashes->count);
    Node *current = layerV3_hashes->start;
    long index = 0;
    while (current != NULL)
    {
        for (int j=0; j<HASHSIZE;j++)
        {
            piece_layerV3[index] = current->hash[j];
            index += 1;
        }
        current = current->next;
    }
    int x = layerV3_hashes->count;
    if (!(x && (!(x&(x-1)))))
    {
        next_pow2 = 1 << (unsigned) floor((log(x)/log(2)) + 1);
        remaining = next_pow2 - x;
        uint8 *piece;
        for (int i = 0; i < remaining; i++){
            piece = getPadPiece(blocks_per_piece);
            add_node(layerV3_hashes, piece);
        }
    }
    uint8 *roothash;
    roothash = MerkleRoot(layerV3_hashes);
    HASHHYBRID *result = (HASHHYBRID *)malloc(sizeof(HASHHYBRID));
    result->piece_layerV3 = piece_layerV3;
    result->pieces_root = roothash;
    result->hashv1 = v1pieces;
    return result;
}

// int main(int argc, char **argv)
// {
//     printf("%s\n", argv[1]);
//     unsigned piece_length = (unsigned)pow(2.0, 16.0);
//     HASHHYBRID* result;
//     result = HasherHybrid(argv[1], piece_length);
//     hex_digest(result->piece_layerV3);
//     hex_digest(result->pieces_root);
//     hex_digest(result->hashv1);
//     return 0;
// }

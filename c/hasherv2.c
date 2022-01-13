#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include "sha256.h"
#include "hasherv2.h"

#define BLOCKSIZE 16384
#define HASHSIZE 32


typedef uint8_t uint8;


typedef struct Node {     // Linked List Node Item
    uint8 *hash;
    struct Node *next;
} Node;


typedef struct {  // Linked List of layer hashes
    Node *start;
    Node *end;
    int count;
} Layer;


// typedef struct { // Hash Result Object
//     uint8 *piece_layer;
//     uint8 *pieces_root;
// } HASHV2;


Layer *newLayer()
{
    // Creates a new linked list
    Layer *layer = (Layer *)malloc(sizeof(Layer));
    layer->start = NULL;
    layer->end = NULL;
    layer->count = 0;
    return layer;
}

void hexdigest(uint8 *hash)
{
    for (int i = 0; i < HASHSIZE; i++)
    {
        printf("%02x", hash[i]);
    }
}

void showTree(Layer *layer)
{
    printf("\n\n");
    Node *current = layer->start;
    while (current != NULL)
    {
        printf("----  ");
        hexdigest(current->hash);
        printf("  ----\n");
        current = current->next;
    }
    printf("\n\n");
}

uint8 *hashJoin(uint8 *hash1, uint8 *hash2)
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

void deleteLayer(Layer *layer)
{
    Node *start = layer->start;
    while (start)
    {
        Node *next = start->next;
        free(start->hash);
        free(start);
        start = next;
    }
    free(layer);
}

void addNode(Layer *layer, uint8 *hash)
{
    Node *newnode = (Node *)malloc(sizeof(Node));
    newnode->hash = hash;
    newnode->next = NULL;
    if (layer->start)
    {
        Node *end = layer->end;
        end->next = newnode;
        layer->end = newnode;
    }
    else
    {
        layer->start = newnode;
        layer->end = newnode;
    }
    layer->count = layer->count + 1;
}

uint8 *get_padding()
{
    uint8 *padding = (uint8 *)malloc(HASHSIZE);
    for (int i = 0; i < HASHSIZE; i++)
    {
        padding[i] = 0;
    }
    return padding;
}

uint8 *merkle_root(Layer *layer)
{
    int count = layer->count;
    while (count > 1)
    {
        printf("\nCount = %d\n", count);
        Node *current = layer->start;
        Node *next = current->next;
        Node *last = current;
        int index = 0;
        while (true)
        {
            uint8 *partial = hashJoin(current->hash, next->hash);
            last->hash = partial;
            index++;
            current = next->next;
            if (!current) break;
            next = current->next;
            last = last->next;
        }
        count = index;
        layer->end = last;
        last->next = NULL;
    }
    printf("MerkleRoot");
    showTree(layer);
    return layer->start->hash;
}


uint8 *get_pad_piece(unsigned n)
{
    uint8 *padding;
    Layer *layer = newLayer();
    for (int i = 0; i < n; i++)
    {
        padding = get_padding();
        addNode(layer, padding);
    }
    return merkle_root(layer);
}


HASHV2 *HasherV2(char *path, unsigned piece_length)
{
    unsigned amount, next_pow2, total, remaining, blocks_per_piece;
    Layer *layer;
    Layer *layer_hashes = newLayer();
    FILE *fptr = fopen(path, "rb");
    uint8 *buffer = (uint8 *)malloc(BLOCKSIZE);
    total = 0;
    blocks_per_piece = (unsigned) floor(piece_length / BLOCKSIZE);
    while (true)
    {
        layer = newLayer();
        uint8 *piece;
        for (int i = 0; i < blocks_per_piece; i++)
        {
            amount = fread(buffer, 1, BLOCKSIZE, fptr);
            total += amount;
            if (!amount) break;
            uint8 *hash = (uint8 *)malloc(amount);
            SHA256(hash, buffer, amount);
            addNode(layer, hash);
        }
        if (!layer->count) break;
        if (layer->count < blocks_per_piece)
        {
            if (!layer_hashes->count)
            {
                next_pow2 = 1 << (unsigned) floor((log(total)/log(2)) + 1);
                remaining = (unsigned) ((next_pow2 - total) / BLOCKSIZE) + 1;
            }
            else
            {
                remaining = blocks_per_piece - layer->count;
            }
            printf("Remaining = %d; count = %d.", remaining, layer->count);
            uint8 *padding;
            for (int i = 0; i < remaining; i++)
            {
                padding = get_padding();
                addNode(layer, padding);
            }
        }
        piece = merkle_root(layer);
        addNode(layer_hashes, piece);
    }
    uint8 *piece_layer = (uint8 *)malloc(HASHSIZE * layer_hashes->count);
    Node *current = layer_hashes->start;
    long index = 0;
    while (current != NULL)
    {
        for (int j=0; j<HASHSIZE;j++)
        {
            piece_layer[index] = current->hash[j];
            index += 1;
        }
        current = current->next;
    }
    int x = layer_hashes->count;
    if (!(x && (!(x&(x-1)))))
    {
        next_pow2 = 1 << (unsigned) floor((log(x)/log(2)) + 1);
        remaining = next_pow2 - x;
        uint8 *piece;
        for (int i = 0; i < remaining; i++){
            piece = get_pad_piece(blocks_per_piece);
            addNode(layer_hashes, piece);
        }
    }
    uint8 *roothash;
    roothash = merkle_root(layer_hashes);
    // hexdigest(roothash);
    HASHV2 *result = (HASHV2 *)malloc(sizeof(HASHV2));
    result->piece_layer = piece_layer;
    result->pieces_root = roothash;
    return result;
}


// int main(int argc, char **argv)
// {
//     printf("%s\n", argv[1]);
//     unsigned piece_length = (unsigned)pow(2.0, 16.0);
//     printf("\npiece length = %d\n", piece_length);
//     HASHV2* result;
//     result = HasherV2(argv[1], piece_length);
//     return 0;
// }

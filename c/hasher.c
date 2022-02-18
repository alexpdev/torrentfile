#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <sys/stat.h>
#include <math.h>
#include <stdbool.h>
#include "sha.h"
#include "hasher.h"

#define BLOCKSIZE 16384
#define HASHSIZE 32
#define V1HASHSIZE 20

typedef struct Node {     // Linked List Node Item
    uint8 *hash;
    struct Node *next;
} Node;

typedef struct {  // Linked List of layer hashes
    Node *start;
    Node *end;
    int count;
} Layer;


// typedef struct {
//     uint8_t *ptr;
//     int size;
//     int allocated;
//     int logical;
// } Hash;

// int main(int argc, char **argv)
// {
//     int piece_length = BLOCK_SIZE;
//     printf("%d\n", BLOCK_SIZE);
//     Hash *hash = malloc(sizeof(Hash));
//     HashInit(hash);
//     Hasher(argv, piece_length, hash);
//     show_Hash(hash);
//     return 0;
// }

void HASHInit(HASH *hash)
{
    hash->size = 20;
    hash->allocated = 2;
    hash->logical = 0;
    hash->ptr = (uint8_t *)malloc(40);
}


void extend_Hash(HASH *hash, uint8_t *output)
{
    int index, i, j;
    if (hash->logical == hash->allocated){
        int current = hash->allocated * hash->size;
        uint8_t *seq = (uint8_t *)malloc(current*2);
        for (i=0; i<current; i++){
            seq[i] = hash->ptr[i];
            printf("%02X ", (unsigned char)seq[i]);
        }
        hash->allocated *= 2;
        hash->ptr = seq;
    }
    for (j=0; j<20; j++){
        index = (hash->logical * hash->size) + j;
        hash->ptr[index] = output[j];
    }
    hash->logical += 1;
    return;
}

int addpartial(uint8_t *buffer, FILE *fptr, int remains, int piece_length)
{
    int subsize = piece_length - remains;
    uint8_t *subbuff = (uint8_t *)malloc(subsize);
    int amount = fread(subbuff, 1, subsize, fptr);
    for (int i=0; i<amount; i++)
        buffer[remains + i] = subbuff[i];
    return amount + remains;
}


HASH *HASHER(char **filelist, int piece_length){
    HASH *hash = (HASH *)malloc(sizeof(HASH));
    HASHInit(hash);
    int i, amount;
    FILE *fptr;
    bool partial = false;
    uint8_t *buffer;
    buffer = (uint8_t *)malloc(piece_length);
    uint8_t *output;
    size_t remains;
    // printf("partial: %d\n", partial);
    for (i=1;filelist[i] != NULL; i++)
    {
        fptr = fopen(filelist[i], "rb");
        printf("filename: %s\n", filelist[i]);
        while (true)
        {
            if (!partial){
                amount = fread(buffer, 1, piece_length, fptr);
                printf("amount read: %d", amount);
            }
            else{
                buffer = (uint8_t *)malloc(piece_length);
                amount = addpartial(buffer, fptr, remains, piece_length);
                printf("amount read: %d", amount);
            }
            if (amount < piece_length)
            {
                fclose(fptr);
                if (!amount) break;
                partial = true;
                remains = amount;
                break;
            }
            output = (uint8_t *)malloc(20);
            SHA1(output, buffer, piece_length);
            extend_Hash(hash, output);
            partial = false;
        }
    }
    if (partial){
        output = (uint8_t *)malloc(21);
        SHA1(output, buffer, amount);
        extend_Hash(hash, output);
    }
    return hash;
}


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
    Layer *layerv2;
    Layer *layer_hashes = newLayer();
    FILE *fptr = fopen(path, "rb");
    uint8 *buffer = (uint8 *)malloc(BLOCKSIZE);
    total = 0;
    blocks_per_piece = (unsigned) floor(piece_length / BLOCKSIZE);
    while (true)
    {
        layerv2 = newLayer();
        uint8 *piece;
        for (int i = 0; i < blocks_per_piece; i++)
        {
            amount = fread(buffer, 1, BLOCKSIZE, fptr);
            total += amount;
            if (!amount) break;
            uint8 *hash = (uint8 *)malloc(amount);
            SHA256(hash, buffer, amount);
            addNode(layerv2, hash);
        }
        if (!layerv2->count) break;
        if (layerv2->count < blocks_per_piece)
        {
            if (!layer_hashes->count)
            {
                next_pow2 = 1 << (unsigned) floor((log(total)/log(2)) + 1);
                remaining = (unsigned) ((next_pow2 - total) / BLOCKSIZE) + 1;
            }
            else
            {
                remaining = blocks_per_piece - layerv2->count;
            }
            uint8 *padding;
            for (int i = 0; i < remaining; i++)
            {
                padding = get_padding();
                addNode(layerv2, padding);
            }
        }
        piece = merkle_root(layerv2);
        addNode(layer_hashes, piece);
    }
    uint8 *piece_layerv2 = (uint8 *)malloc(HASHSIZE * layer_hashes->count);
    Node *current = layer_hashes->start;
    long index = 0;
    while (current != NULL)
    {
        for (int j = 0;j < HASHSIZE; j++)
        {
            piece_layerv2[index] = current->hash[j];
            index += 1;
        }
        current = current->next;
    }
    int x = layer_hashes->count;
    if (x && (x & (x - 1) == 0))
    {
        next_pow2 = 1 << (unsigned) floor((log(x)/log(2)) + 1);
        remaining = next_pow2 - x;
        uint8 *piece;
        for (int i = 0; i < remaining; i++){
            piece = get_pad_piece(blocks_per_piece);
            addNode(layer_hashes, piece);
        }
    }
    uint8 *roothashv2;
    roothashv2 = merkle_root(layer_hashes);
    // hexdigest(roothash);
    HASHV2 *result = (HASHV2 *)malloc(sizeof(HASHV2));
    result->piece_layer = piece_layerv2;
    result->pieces_root = roothashv2;
    return result;
}


HASHHYBRID *HasherHybrid(char *path, int piece_length)
{
    Layer *layer;
    Layer *layer_hashes = newLayer();
    Layer *v1pieces = newLayer();
    FILE *fptr = fopen(path, "rb");
    uint8 *buffer = (uint8 *)malloc(BLOCKSIZE);
    uint8 *v1buffer = (uint8 *)malloc(piece_length);
    int total, blocks_per_piece, amount, next_pow2, remaining;
    total = 0;
    blocks_per_piece = (int) floor(piece_length / BLOCKSIZE);
    while (true)
    {
        int bufsize = 0;
        layer = newLayer();
        uint8 *piece;
        for (int i = 0; i < blocks_per_piece; i++)
        {
            amount = fread(buffer, 1, BLOCKSIZE, fptr);
            total += amount;
            if (!amount) break;
            uint8 *hash = (uint8 *)malloc(amount);
            SHA256(hash, buffer, amount);
            add_node(layer, hash);
            for (int j = 0; j < amount; j++)
            {
                v1buffer[bufsize] = buffer[j];
                bufsize += 1;
            }
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
            uint8 *padding;
            for (int i = 0; i < remaining; i++)
            {
                padding = get_padding();
                addNode(layer, padding);
            }
        }
        uint8 *v1hash = (uint8 *)malloc(V1HASHSIZE);
        SHA1(v1hash, v1buffer, bufsize);
        piece = merkle_root(layer);
        addNode(layer_hashes, piece);
        addNode(v1pieces, v1hash);
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
    if (x && (x & (x-1) == 0))
    {
        next_pow2 = 1 << (unsigned) floor((log(x)/log(2)) + 1);
        remaining = next_pow2 - x;
        uint8 *piece;
        for (int i = 0; i < remaining; i++){
            piece = get_pad_piece(blocks_per_piece);
            addNode(layer_hashes, piece);
        }
    }
    uint8 *v1p = (uint8 *)malloc(V1HASHSIZE * v1pieces->count);
    Node *first = v1pieces->start;
    int counter = 0;
    while (first != NULL){
        for (int i=0; i<V1HASHSIZE; i++){
            v1p[counter] = first->hash[i];
            counter += 1;
        }
        first = first->next;
    }
    uint8 *roothash;
    roothash = merkle_root(layer_hashes);
    HASHHYBRID *result = (HASHHYBRID *)malloc(sizeof(HASHHYBRID));
    result->piece_layer = piece_layerV3;
    result->pieces_root = roothash;
    result->hashv1 = v1p;
    return result;
}

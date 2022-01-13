#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <sys/stat.h>
#include <math.h>
#include <stdbool.h>
#include "sha1.h"
#include "hasher.h"

#define BLOCK_SIZE 16384

// typedef struct {
//     uint8_t *ptr;
//     int size;
//     int allocated;
//     int logical;
// } Hash;


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


void show_Hash(HASH *hash)
{
    int i;
    printf("%d, %d, %d", hash->logical, hash->allocated, hash->size);
    int size = hash->logical*hash->size;
    printf("\n");
    for (i=0;i<size;i++)
    {
        printf("%02X", (unsigned char)hash->ptr[i]);
    }
    printf("\n");
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

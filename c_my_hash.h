/**
 * @file c_my_hash.h
 * @author Zuoru YANG (zryang@cse.cuhk.edu.hk)
 * @brief my hash table
 * @version 0.1
 * @date 2023-06-13
 *
 * @copyright Copyright (c) 2023
 *
 */

#ifndef MY_HASH_TYPE_H
#define MY_HASH_TYPE_H

#include "define_const.h"
#include "c_include.h"
#include "third_party/uthash.h"

typedef int ZUORU_HashData;

typedef struct {
    int hashKey;
    ZUORU_HashData hashVal;
    UT_hash_handle hh;
} ZUORU_HashTblIntItem;

/**
 *********************************************
 ***               for int key hash table
 *********************************************
 */

ZUORU_HashTblIntItem** ZUORU_InitIntHashTbl()
{
    ZUORU_HashTblIntItem **hashTblPtr = (ZUORU_HashTblIntItem**)calloc(1,
        sizeof(ZUORU_HashTblIntItem*));
    *hashTblPtr = NULL;
    return hashTblPtr;
}

ZUORU_HashTblIntItem* ZUORU_InsertIntHashTbl(ZUORU_HashTblIntItem **hashTblPtr,
    int key, ZUORU_HashData *inVal)
{
    ZUORU_HashTblIntItem *tmpHashItem;

    HASH_FIND_INT(*hashTblPtr, &key, tmpHashItem);
    if (tmpHashItem == NULL) {
        tmpHashItem = (ZUORU_HashTblIntItem*)calloc(1, sizeof(ZUORU_HashTblIntItem));
        tmpHashItem->hashKey = key;
        HASH_ADD_INT(*hashTblPtr, hashKey, tmpHashItem);
    }
    memcpy(&tmpHashItem->hashVal, inVal, sizeof(ZUORU_HashData));
    return tmpHashItem;
}

bool ZUORU_FindIntHashTbl(ZUORU_HashTblIntItem **hashTblPtr, int key,
    ZUORU_HashTblIntItem **ret)
{
    ZUORU_HashTblIntItem *tmpHashItem = NULL;
    HASH_FIND_INT(*hashTblPtr, &key, tmpHashItem);
    if (tmpHashItem == NULL) {
        *ret = NULL;
        return false;
    }

    *ret = tmpHashItem;
    return true;
}

void ZUORU_DelIntHashTbl(ZUORU_HashTblIntItem **hashTblPtr,
    ZUORU_HashTblIntItem *hashItem)
{
    HASH_DEL(*hashTblPtr, hashItem);
    free(hashItem);
    return;
}

void ZUORU_FreeIntHashTbl(ZUORU_HashTblIntItem **hashTblPtr)
{
    ZUORU_HashTblIntItem *curItem;
    ZUORU_HashTblIntItem *tmpItem;

    HASH_ITER(hh, *hashTblPtr, curItem, tmpItem) {
        HASH_DEL(*hashTblPtr, curItem);
        free(curItem);
    }
    free(hashTblPtr);
    return;
}

/**
 *********************************************
 ***               for ptr key hash table
 *********************************************
 */

typedef struct {
    void *hashKey;
    ZUORU_HashData hashVal;
    UT_hash_handle hh;
} ZUORU_HashTblPtrItem;

ZUORU_HashTblPtrItem** ZUORU_InitPtrHashTbl()
{
    ZUORU_HashTblPtrItem **hashTblPtr = (ZUORU_HashTblPtrItem**)calloc(1,
        sizeof(ZUORU_HashTblPtrItem*));
    *hashTblPtr = NULL;
    return hashTblPtr;
}

void ZUORU_InsertPtrHashTbl(ZUORU_HashTblPtrItem **hashTblPtr, void *key,
    ZUORU_HashData *inVal)
{
    ZUORU_HashTblPtrItem *tmpHashItem = NULL;
    HASH_FIND_PTR(*hashTblPtr, &key, tmpHashItem);
    if (tmpHashItem == NULL) {
        tmpHashItem = (ZUORU_HashTblPtrItem*)calloc(1, sizeof(ZUORU_HashTblPtrItem));
        tmpHashItem->hashKey = key;
        HASH_ADD_PTR(*hashTblPtr, hashKey, tmpHashItem);
    }
    memcpy(&tmpHashItem->hashVal, inVal, sizeof(ZUORU_HashData));
    return;
}

bool ZUORU_FindPtrHashTbl(ZUORU_HashTblPtrItem **hashTblPtr, void *key,
    ZUORU_HashTblPtrItem **ret)
{
    ZUORU_HashTblPtrItem *tmpHashItem = NULL;
    HASH_FIND_PTR(*hashTblPtr, &key, tmpHashItem);
    if (tmpHashItem == NULL) {
        *ret = NULL;
        return false;
    }

    *ret = tmpHashItem;
    return true;
}

void ZUORU_DelPtrHashTbl(ZUORU_HashTblPtrItem **hashTblPtr,
    ZUORU_HashTblPtrItem *hashItem)
{
    HASH_DEL(*hashTblPtr, hashItem);
    free(hashItem);
    return;
}

void ZUORU_FreePtrHashTbl(ZUORU_HashTblPtrItem **hashTblPtr)
{
    ZUORU_HashTblPtrItem *curItem;
    ZUORU_HashTblPtrItem *tmpItem;

    HASH_ITER(hh, *hashTblPtr, curItem, tmpItem) {
        HASH_DEL(*hashTblPtr, curItem);
        free(curItem);
    }
    free(hashTblPtr);
    return;
}

/**
 *********************************************
 ***               for str key hash table
 *********************************************
 */

#define MAX_HASH_KEY_SIZE 32

typedef struct {
    char hashKey[MAX_HASH_KEY_SIZE];
    ZUORU_HashData hashVal;
    UT_hash_handle hh;
} ZUORU_HashTblStrItem;

ZUORU_HashTblStrItem** ZUORU_InitStrHashTbl()
{
    ZUORU_HashTblStrItem **hashTblPtr = (ZUORU_HashTblStrItem**)calloc(1,
        sizeof(ZUORU_HashTblStrItem*));
    *hashTblPtr = NULL;
    return hashTblPtr;
}

void ZUORU_InsertStrHashTbl(ZUORU_HashTblStrItem **hashTblPtr, const char *key,
    ZUORU_HashData *inVal)
{
    ZUORU_HashTblStrItem *tmpHashItem = NULL;
    HASH_FIND_STR(*hashTblPtr, key, tmpHashItem);
    if (tmpHashItem == NULL) {
        tmpHashItem = (ZUORU_HashTblStrItem*)calloc(1, sizeof(ZUORU_HashTblStrItem));
        strcpy(tmpHashItem->hashKey, key);
        HASH_ADD_STR(*hashTblPtr, hashKey, tmpHashItem);
    }
    memcpy(&tmpHashItem->hashVal, inVal, sizeof(ZUORU_HashData));
    return;
}

bool ZUORU_FindStrHashTbl(ZUORU_HashTblStrItem **hashTblPtr, const char *key,
    ZUORU_HashTblStrItem **ret)
{
    ZUORU_HashTblStrItem *tmpHashItem = NULL;
    HASH_FIND_STR(*hashTblPtr, key, tmpHashItem);
    if (tmpHashItem == NULL) {
        *ret = NULL;
        return false;
    }

    *ret = tmpHashItem;
    return true;
}

void ZUORU_DelStrHashTbl(ZUORU_HashTblStrItem **hashTblPtr,
    ZUORU_HashTblStrItem *hashItem)
{
    HASH_DEL(*hashTblPtr, hashItem);
    free(hashItem);
    return;
}

void ZUORU_FreeStrHashTbl(ZUORU_HashTblStrItem **hashTblPtr)
{
    ZUORU_HashTblStrItem *curItem;
    ZUORU_HashTblStrItem *tmpItem;

    HASH_ITER(hh, *hashTblPtr, curItem, tmpItem) {
        HASH_DEL(*hashTblPtr, curItem);
        free(curItem);
    }
    free(hashTblPtr);
    return;
}

#endif

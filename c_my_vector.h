/**
 * @file c_my_vector.h
 * @author Zuoru YANG (zryang@cse.cuhk.edu.hk)
 * @brief implement my vector in C
 * @version 0.1
 * @date 2023-11-17
 *
 * @copyright Copyright (c) 2023
 *
 */

#ifndef C_MY_VECTOR_H
#define C_MY_VECTOR_H

#include "c_include.h"

typedef struct {
    int key;
    int value;
} VectorDataItem;

typedef struct {
    VectorDataItem *data;
    int size;
    int capacity;
} Vector;

static Vector *VectorInit(int initCapacity)
{
    Vector *vector = (Vector*)calloc(1, sizeof(Vector));
    vector->size = 0;
    vector->capacity = initCapacity;
    vector->data = (VectorDataItem*)calloc(initCapacity, sizeof(VectorDataItem));
    return vector;
}

static void VectorPushBack(Vector *vector, VectorDataItem *item)
{
    if (vector->size == vector->capacity) {
        vector->capacity *= 2;
        vector->data = (VectorDataItem*)realloc(vector->data,
            vector->capacity * sizeof(VectorDataItem));
    }
    memcpy(&vector->data[vector->size], item, sizeof(VectorDataItem));
    vector->size++;
    return;
}

static bool VectorPopBack(Vector *vector, VectorDataItem *outItem)
{
    if (vector->size == 0) {
        return false;
    }
    memcpy(outItem, &vector->data[vector->size - 1], sizeof(VectorDataItem));
    vector->size--;
    return true;
}

static void VectorFree(Vector *vector)
{
    free(vector->data);
    free(vector);
}

static bool VectorFind(Vector *vector, int key, int *outIdx)
{
    for (int idx = 0; idx < vector->size; idx++) {
        if (vector->data[idx].key == key) {
            *outIdx = idx;
            return true;
        }
    }
    return false;
}

static bool VectorDel(Vector *vector, int key)
{
    int findIdx = 0;
    int copyLen = 0;
    if (VectorFind(vector, key, &findIdx)) {
        copyLen = (vector->size - 1) - (findIdx + 1) + 1;
        memmove(vector->data + findIdx, vector->data + findIdx + 1,
            copyLen * sizeof(VectorDataItem));
        vector->size--;
        return true;
    }
    return false;
}

static int VectorCmpFuncKeyValue(const void *rawItem1, const void *rawItem2)
{
    VectorDataItem *item1 = (VectorDataItem*)rawItem1;
    VectorDataItem *item2 = (VectorDataItem*)rawItem2;
    if (item1->key != item2->key) {
        return item1->key - item2->key; // ascend
    } else {
        if (item1->value != item2->value) {
            return item1->value - item2->value; // ascend
        }
    }
    return 0;
}

static void VectorSortByKeyValue(Vector *vector)
{
    qsort(vector->data, vector->size, sizeof(VectorDataItem), VectorCmpFuncKeyValue);
    return;
}

#endif

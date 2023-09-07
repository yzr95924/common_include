/**
 * @file my_data_struct.h
 * @author Zuoru YANG (zryang@cse.cuhk.edu.hk)
 * @brief my data struct
 * @version 0.1
 * @date 2023-06-08
 *
 * @copyright Copyright (c) 2023
 *
 */

#ifndef MY_DATA_STRUCT_H
#define MY_DATA_STRUCT_H

#include "define_const.h"
#include "c_include.h"

#define MY_DATA_STRUCT_EMPTY_POS (-1)
typedef int ZUORU_DataItem;

int ZUORU_CompFunc(const void *rawInput1, const void *rawInput2)
{
    ZUORU_DataItem *input1 = (ZUORU_DataItem*)rawInput1;
    ZUORU_DataItem *input2 = (ZUORU_DataItem*)rawInput2;
    int ret = *input1 - *input2; // ascend

    return ret;
}

/**
 *********************************************
 ***               for queue
 *********************************************
 */

typedef struct {
    ZUORU_DataItem *data;
    int head;
    int rear;
    int capacity;
    int curSize;
} ZUORU_Queue;

ZUORU_Queue* ZUORU_InitQueue(int capacity)
{
    ZUORU_Queue *queuePtr = (ZUORU_Queue*)calloc(1, sizeof(ZUORU_Queue));
    queuePtr->data = (ZUORU_DataItem*)calloc(capacity, sizeof(ZUORU_DataItem));
    queuePtr->head = MY_DATA_STRUCT_EMPTY_POS;
    queuePtr->rear = MY_DATA_STRUCT_EMPTY_POS;
    queuePtr->capacity = capacity;
    queuePtr->curSize = 0;

    return queuePtr;
}

bool ZUORU_EnQueue(ZUORU_Queue *queuePtr, ZUORU_DataItem *inVal)
{
    if (queuePtr->curSize + 1 > queuePtr->capacity) {
        fprintf(stderr, "queue is full\n");
        return false;
    }

    if (queuePtr->head == MY_DATA_STRUCT_EMPTY_POS) {
        queuePtr->head = 0;
    }
    queuePtr->rear = (queuePtr->rear + 1) % queuePtr->capacity;
    memcpy(&queuePtr->data[queuePtr->rear], inVal, sizeof(ZUORU_DataItem));

    queuePtr->curSize++;
    return true;
}

bool ZUORU_DeQueue(ZUORU_Queue *queuePtr, ZUORU_DataItem *outVal)
{
    if (queuePtr->curSize == 0) {
        fprintf(stderr, "queue is empty\n");
        return false;
    }

    memcpy(outVal, &queuePtr->data[queuePtr->head], sizeof(ZUORU_DataItem));
    if (queuePtr->head == queuePtr->rear) {
        queuePtr->rear = MY_DATA_STRUCT_EMPTY_POS;
        queuePtr->head = MY_DATA_STRUCT_EMPTY_POS;
    }
    queuePtr->head = (queuePtr->head + 1) % queuePtr->capacity;

    queuePtr->curSize--;
    return true;
}

bool ZUORU_IsFullQueue(ZUORU_Queue *queuePtr)
{
    if (queuePtr->curSize == queuePtr->capacity) {
        return true;
    }
    return false;
}

bool ZUORU_IsEmptyQueue(ZUORU_Queue *queuePtr)
{
    if (queuePtr->curSize == 0) {
        return true;
    }
    return false;
}

void ZUORU_FreeQueue(ZUORU_Queue *queuePtr)
{
    free(queuePtr->data);
    free(queuePtr);
    return;
}

/**
 *********************************************
 ***               for list
 *********************************************
 */

typedef struct {
    ZUORU_DataItem *data;
    int capacity;
    int curSize;
} ZUORU_ArrList;

ZUORU_ArrList* ZUORU_InitArrList(int capacity)
{
    ZUORU_ArrList *arrListPtr = (ZUORU_ArrList*)calloc(1, sizeof(ZUORU_ArrList));
    arrListPtr->data = (ZUORU_DataItem*)calloc(capacity, sizeof(ZUORU_DataItem));
    arrListPtr->capacity = capacity;
    arrListPtr->curSize = 0;

    return arrListPtr;
}

bool ZUORU_IsFullArrList(ZUORU_ArrList *arrListPtr)
{
    if (arrListPtr->curSize == arrListPtr->capacity) {
        return true;
    }
    return false;
}

bool ZUORU_IsEmptyArrList(ZUORU_ArrList *arrListPtr)
{
    if (arrListPtr->curSize == 0) {
        return true;
    }
    return false;
}

void ZUORU_FreeArrList(ZUORU_ArrList *arrListPtr)
{
    free(arrListPtr->data);
    free(arrListPtr);
}

bool ZUORU_AppendArrList(ZUORU_ArrList *arrListPtr, ZUORU_DataItem *inVal)
{
    if (ZUORU_IsFullArrList(arrListPtr)) {
        fprintf(stderr, "list is full\n");
        return false;
    }

    memcpy(&arrListPtr->data[arrListPtr->curSize], inVal, sizeof(ZUORU_DataItem));
    arrListPtr->curSize++;

    return true;
}

bool ZUORU_InsertArrList(ZUORU_ArrList *arrListPtr, int posIdx, ZUORU_DataItem *inVal)
{
    if (ZUORU_IsFullArrList(arrListPtr)) {
        fprintf(stderr, "list is full\n");
        return false;
    }

    if (posIdx > arrListPtr->curSize) {
        fprintf(stderr, "list insert pos is invalid, posIdx: %d, curSize%d\n",
            posIdx, arrListPtr->curSize);
        return false;
    }

    for (int idx = arrListPtr->curSize - 1; idx >= posIdx; idx--) {
        memcpy(&arrListPtr->data[idx + 1], &arrListPtr->data[idx], sizeof(ZUORU_DataItem));
    }

    memcpy(&arrListPtr->data[posIdx], inVal, sizeof(ZUORU_DataItem));
    arrListPtr->curSize++;

    return true;
}

bool ZUORU_FindArrList(ZUORU_ArrList *arrListPtr, ZUORU_DataItem* inVal, int *posIdx)
{
    for (int idx = 0; idx < arrListPtr->curSize; idx++) {
        if (memcmp(&arrListPtr->data[idx], inVal, sizeof(ZUORU_DataItem)) == 0) {
            *posIdx = idx;
            return true;
        }
    }

    return false;
}

bool ZUORU_DeleteArrList(ZUORU_ArrList *arrListPtr, int posIdx, ZUORU_DataItem *delVal)
{
    if (ZUORU_IsEmptyArrList(arrListPtr)) {
        fprintf(stderr, "list is empty\n");
        return false;
    }

    if (posIdx >= arrListPtr->curSize) {
        fprintf(stderr, "list del pos is invalid, posIdx: %d, curSize%d\n",
            posIdx, arrListPtr->curSize);
        return false;
    }

    memcpy(delVal, &arrListPtr->data[posIdx], sizeof(ZUORU_DataItem));

    for (int idx = 0; idx < arrListPtr->curSize - 1; idx++) {
        memcpy(&arrListPtr->data[idx], &arrListPtr->data[idx + 1],
            sizeof(ZUORU_DataItem));
    }

    arrListPtr->curSize--;
    return true;
}

void ZUORU_SortArrList(ZUORU_ArrList *arrListPtr)
{
    qsort(arrListPtr->data, arrListPtr->curSize, sizeof(ZUORU_DataItem), ZUORU_CompFunc);
    return;
}

/**
 *********************************************
 ***               for stack
 *********************************************
 */

typedef struct {
    ZUORU_DataItem *data;
    int stackTopIdx;
    int curSize;
    int capacity;
} ZUORU_Stack;

ZUORU_Stack* ZUORU_InitStack(int capacity)
{
    ZUORU_Stack *stackPtr = (ZUORU_Stack*)calloc(1, sizeof(ZUORU_Stack));
    stackPtr->data = (ZUORU_DataItem*)calloc(capacity, sizeof(ZUORU_DataItem));
    stackPtr->stackTopIdx = MY_DATA_STRUCT_EMPTY_POS;
    stackPtr->capacity = capacity;
    stackPtr->curSize = 0;

    return stackPtr;
}

void ZUORU_FreeStack(ZUORU_Stack *stackPtr)
{
    free(stackPtr->data);
    free(stackPtr);
    return;
}

bool ZUORU_IsFullStack(ZUORU_Stack *stackPtr)
{
    if (stackPtr->stackTopIdx == (stackPtr->capacity - 1)) {
        return true;
    }
    return false;
}

bool ZUORU_IsEmptyStack(ZUORU_Stack *stackPtr)
{
    if (stackPtr->stackTopIdx == MY_DATA_STRUCT_EMPTY_POS) {
        return true;
    }
    return false;
}

bool ZUORU_PushStack(ZUORU_Stack *stackPtr, ZUORU_DataItem *inVal)
{
    if (ZUORU_IsFullStack(stackPtr)) {
        fprintf(stderr, "stack is full\n");
        return false;
    }
    stackPtr->stackTopIdx++;
    memcpy(&stackPtr->data[stackPtr->stackTopIdx], inVal,
        sizeof(ZUORU_DataItem));
    stackPtr->curSize++;
    return true;
}

bool ZUORU_PopStack(ZUORU_Stack *stackPtr, ZUORU_DataItem *outVal)
{
    if (ZUORU_IsEmptyStack(stackPtr)) {
        fprintf(stderr, "stack is empty\n");
        return false;
    }

    memcpy(outVal, &stackPtr->data[stackPtr->stackTopIdx],
        sizeof(ZUORU_DataItem));
    stackPtr->stackTopIdx--;
    stackPtr->curSize--;
    return true;
}

bool ZUORU_TopStack(ZUORU_Stack *stackPtr, ZUORU_DataItem *outVal)
{
    if (ZUORU_IsEmptyStack(stackPtr)) {
        fprintf(stderr, "stack is empty");
        return false;
    }
    memcpy(outVal, &stackPtr->data[stackPtr->stackTopIdx],
        sizeof(ZUORU_DataItem));

    return true;
}

/**
 *********************************************
 ***               for double-linked list
 *********************************************
 */

struct ZUORU_DLListNode {
    ZUORU_DataItem data;
    struct ZUORU_DLListNode *next;
    struct ZUORU_DLListNode *prev;
};

typedef struct ZUORU_DLListNode ZUORU_DLListNode;

typedef struct {
    ZUORU_DLListNode *head;
    ZUORU_DLListNode *tail;
    int curSize;
} ZUORU_DLList;

ZUORU_DLList* ZUORU_InitDLList()
{
    ZUORU_DLList *dlListPtr = (ZUORU_DLList*)calloc(1, sizeof(ZUORU_DLList));
    dlListPtr->head = NULL;
    dlListPtr->tail = NULL;
    dlListPtr->curSize = 0;
    return dlListPtr;
}

void ZUORU_FreeDLList(ZUORU_DLList *dlListPtr)
{
    ZUORU_DLListNode *curNode = dlListPtr->head;
    ZUORU_DLListNode *delNode = NULL;

    while (curNode != NULL) {
        delNode = curNode;
        curNode = curNode->next;
        free(delNode);
    }

    free(dlListPtr);
    return;
}

ZUORU_DLListNode* ZUORU_InsertHeadDLList(ZUORU_DLList *dlListPtr, ZUORU_DataItem *inVal)
{
    ZUORU_DLListNode *newNode = (ZUORU_DLListNode*)calloc(1, sizeof(ZUORU_DLListNode));
    memcpy(&newNode->data, inVal, sizeof(ZUORU_DataItem));
    newNode->next = NULL;
    newNode->prev = NULL;

    if (dlListPtr->curSize == 0) {
        dlListPtr->tail = newNode;
    } else {
        dlListPtr->head->prev = newNode;
        newNode->next = dlListPtr->head;
    }

    dlListPtr->head = newNode;
    dlListPtr->curSize++;

    return newNode;
}

ZUORU_DLListNode* ZUORU_InsertTailDLList(ZUORU_DLList *dlListPtr, ZUORU_DataItem *inVal)
{
    ZUORU_DLListNode *newNode = (ZUORU_DLListNode*)calloc(1, sizeof(ZUORU_DLListNode));
    memcpy(&newNode->data, inVal, sizeof(ZUORU_DataItem));
    newNode->next = NULL;
    newNode->prev = NULL;

    if (dlListPtr->curSize == 0) {
        dlListPtr->head = newNode;
    } else {
        dlListPtr->tail->next = newNode;
        newNode->prev = dlListPtr->tail;
    }

    dlListPtr->tail = newNode;
    dlListPtr->curSize++;

    return newNode;
}

ZUORU_DLListNode* ZUORU_InsertAfterNodeDLList(ZUORU_DLList *dlListPtr, ZUORU_DLListNode *targetNode,
    ZUORU_DLListNode *inVal)
{
    ZUORU_DLListNode *newNode = (ZUORU_DLListNode*)calloc(1, sizeof(ZUORU_DLListNode));
    memcpy(newNode, inVal, sizeof(ZUORU_DLListNode));
    newNode->next = NULL;
    newNode->prev = NULL;

    if (targetNode == dlListPtr->tail) {
        newNode->next = NULL;
        dlListPtr->tail = newNode;
    } else {
        newNode->next = targetNode->next;
        targetNode->next->prev = newNode;
    }

    newNode->prev = targetNode;
    targetNode->next = newNode;
    dlListPtr->curSize++;
    return newNode;
}

bool ZUORU_FindDLList(ZUORU_DLList *dlListPtr, ZUORU_DataItem *inVal, ZUORU_DLListNode *findNode)
{
    ZUORU_DLListNode *curNode = dlListPtr->head;

    if (dlListPtr->curSize == 0) {
        return false;
    }

    while (memcmp(&curNode->data, inVal, sizeof(ZUORU_DataItem)) != 0) {
        if (curNode->next == NULL) {
            return false;
        } else {
            curNode = curNode->next;
        }
    }

    memcpy(findNode, curNode, sizeof(ZUORU_DataItem));
    return true;
}

bool ZUORU_DelDLListWithPtr(ZUORU_DLList *dlListPtr, ZUORU_DLListNode *targetNode)
{
    if (dlListPtr->curSize == 0) {
        return false;
    }

    if (targetNode == dlListPtr->head) {
        dlListPtr->head = targetNode->next;
    } else {
        targetNode->prev->next = targetNode->next;
    }

    if (targetNode == dlListPtr->tail) {
        dlListPtr->tail = targetNode->prev;
    } else {
        targetNode->next->prev = targetNode->prev;
    }

    dlListPtr->curSize--;
    free(targetNode);
    return true;
}

#endif

#include <stdlib.h>
#include <stdio.h>

#define MAX_LEN 28
#define MAX_QUEUE 1024



typedef struct DUO{int x,y;}duo;

duo intarray[MAX_QUEUE];

int map[MAX_LEN][MAX_LEN];

void map_print2(){
   int mp2i, mp2j;
   for(mp2i = 0; mp2i < 10; mp2i++){
       for(mp2j = 0; mp2j < 10; mp2j++){
           printf("%d",now.map[mp2i].a[mp2j]);
       }
       printf("\n");
   }
 
}

void put_map(){
    system("rm level4pml.txt");
    FILE* fp = fopen("level4pml.txt","a");
    int i,j;
    for(i = 0; i < MAX_LEN; i++){
        for(j = 0; j < MAX_LEN; j++){
            if(now.map[i].a[j] == 2)
                fprintf(fp, "A");
            else if(now.map[i].a[j] == 3)
                fprintf(fp, "G");
            else if(now.map[i].a[j] == 4)
                fprintf(fp, "E");
            else if(now.map[i].a[j] == 1)
                fprintf(fp, "1");
            else if(now.map[i].a[j] == 0)
                fprintf(fp, "0");
        }
        fprintf(fp, "\n");
    }
    fclose(fp);
}

void put_map_2_memory(){
    int i, j;
    for(i = 0; i < MAX_LEN; i++){
        for(j = 0; j < MAX_LEN; j++){
            map[i][j] = now.map[i].a[j];
        }
    }
}

int search(int x, int y){
    if ((x >= MAX_LEN) || (y >= MAX_LEN) || x < 0 || y < 0) return 10000;
    if (map[x][y] == 1) return 10000;

}

void calculate_next_move(int x, int y, int* next_x, int* next_y){
    int min = 9999;
    char cmd[50];
    FILE* fs;
    int i = -1;
    char* ret = "Skip";

    sprintf(cmd, "python3.6 ../spin/miracle2.py %d %d > bfs.txt", x, y);
    system(cmd);
    fs = fopen("bfs.txt","r");
    fscanf(fs, "%d", &i);
    fclose(fs);

    switch(i){
        case 0:
            printf("Opponent - A\n");
            *next_x = x-1;
            *next_y = y;
            break;
        case 1:
            printf("Opponent - W\n");
            *next_x = x;
            *next_y = y-1;
            break;
        case 2:
            printf("Opponent - D\n");
            *next_x = x+1;
            *next_y = y;
            break;
        case 3:
            printf("Opponent - S\n");
            *next_x = x;
            *next_y = y+1;
            break;
        default:
            printf("Opponent - Skip\n");
            *next_x = x;
            *next_y = y;
    }

    /*
        sprintf(cmd, "python3.6 ../spin/miracle.py %d %d > bfs.txt", x-1, y);
        system(cmd);
        fs = fopen("bfs.txt", "r");
        fscanf(fs,"%d",&i);
        fclose(fs);

        if(i < min){
            min = i;
            *next_x = x-1;
            *next_y = y;
            ret = "A";
        }
        
    

    sprintf(cmd, "python3.6 ../spin/miracle.py %d %d > bfs.txt", x, y-1);
    system(cmd);
    fs = fopen("bfs.txt", "r");
    fscanf(fs,"%d",&i);
    fclose(fs);

    if(i < min){
        min = i;
        *next_x = x;
        *next_y = y-1;
        ret = "W";
    }

    
        sprintf(cmd, "python3.6 ../spin/miracle.py %d %d > bfs.txt", x+1, y);
        system(cmd);
        fs = fopen("bfs.txt", "r");
        fscanf(fs,"%d",&i);
        fclose(fs);

        if(i < min){
            min = i;
            *next_x = x+1;
            *next_y = y;
            ret = "D";
        }
    
    
        
    sprintf(cmd, "python3.6 ../spin/miracle.py %d %d > bfs.txt", x, y+1);
    system(cmd);
    fs = fopen("bfs.txt", "r");
    fscanf(fs,"%d",&i);
    fclose(fs);

    if(i < min){
        min = i;
        *next_x = x;
        *next_y = y+1;
        ret = "S";
    }*/
    return;
}
/*
#define ROW_COUNT 9
#define COL_COUNT 10

#define WALL 1
#define GOAL 3

#define TRUE 1
#define FALSE 0

#define MAX_STACK 1000

typedef struct{
    int first;
    int second;
}Pair;

typedef struct{
    double first;
    Pair second;
}pPair;

typedef struct{
    int parent_i, parent_j;
    double f, g, h;
}cell;

struct stack{
    int maxsize;
    int top;
    Pair *items;
};

struct stack* newStack(int capacity){
    struct stack *pt = (struct stack*)malloc(sizeof(struct stack));
    pt->maxsize = capacity;
    pt->top = -1;
    pt->items = (Pair*)malloc(sizeof(Pair)*capacity);
    return pt;
}

int size(struct stack *pt){
    return pt->top + 1;
}

int isEmpty(struct stack *pt){
    if (pt-> top == -1) return TRUE;
    return FALSE;
}

int isFull(struct stack *pt){
    if(pt->top == pt->maxsize -1) return TRUE;
    return FALSE;
}

unsigned char push(struct stack *pt, Pair x){
    if (isFull(pt) == TRUE) return FALSE;
    pt->items[++(pt->top)] = x;
    return TRUE;
}

Pair peek(struct stack *pt){
    if(isEmpty(pt) == FALSE) return pt->items[pt->top];
    Pair a;
    a.first = -1;
    a.second = -1;
    return a;
}

Pair pop(struct stack *pt){
    if(isEmpty(pt) == FALSE) return pt->items[pt->top--];
    Pair a;
    a.first = -1;
    a.second = -1;
    return a;
}

unsigned char isValid(int row, int col){
    if ((row >= 0) && (row < ROW_COUNT) && (col >= 0) && (col < COL_COUNT))
        return TRUE;
    return FALSE;
}

unsigned char isUnBlocked(int grid[][COL_COUNT], int row, int col){
    if (grid[row][col] == WALL) return FALSE;
    return TRUE;
}

unsigned char isDestination(int row, int col, Pair destination){
    if (row == destination.first && col == destination.second) return TRUE;
    return FALSE;
}

double calculateHValue(int row, int col, Pair dest){
    return ((double)sqrt((row-dest.first)*(row-dest.first) + (col-dest.second)*(col-dest.second)));
}

void tracePath(cell cellDetails[][COL_COUNT], Pair dest){
    int row = dest.first;
    int col = dest.second;

    struct stack *Path = newStack(MAX_STACK);

    while(!(cellDetails[row][col].parent_i == row &&  cellDetails[row][col].parent_j == col)){
        Pair temp;
        temp.first = row;
        temp.second = col;
        unsigned char ret = push(Path, temp);

        int temp_row = cellDetails[row][col].parent_i;
        int temp_col = cellDetails[row][col].parent_j;

        row = temp_row;
        col = temp_col;
    }
    Pair q;
    q.first = row;
    q.second = col;
    push(Path, q);

    while(isEmpty(Path) == FALSE){
        Pair p = pop(Path);
    }
    return;
}

void aStarSearch(int grid[][COL_COUNT], Pair src, Pair dest){
    if(isValid(src.first, src.second) == FALSE) return;
    if(isValid(dest.first, dest.second) == FALSE) return;
    if(isUnBlocked(grid,src.first, src.second) == FALSE || isUnblocked(grid, dest.first, dest.second) == FALSE) return;

    unsigned char closedList[ROW_COUNT][COL_COUNT];
    memset(closedList, FALSE, sizeof(closedList));

    cell cellDetails[ROW_COUNT][COL_COUNT];
    int i, j;
    for(i = 0; i < ROW_COUNT; i++)
        for(j = 0; j < COL_COUNT; j++){
            cellDetails[i][j].f = __FLT_MAX__;
            cellDetails[i][j].g = __FLT_MAX__;
            cellDetails[i][j].h = __FLT_MAX__;
            cellDetails[i][j].parent_i = -1;
            cellDetails[i][j].parent_j = -1;
        }

    i = src.first;
    j = src.second;

    cellDetails[i][j].f = 0.0;
    cellDetails[i][j].g = 0.0;
    cellDetails[i][j].h = 0.0;
    cellDetails[i][j].parent_i = i;
    cellDetails[i][j].parent_j = j;

    
}*/
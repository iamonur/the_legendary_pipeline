#include <stdlib.h>
#include <stdio.h>

void calculate_next_move(int x, int y, int* next_x, int* next_y){
    int min = 9999;
    char cmd[50];
    FILE* fs;
    int i = -1;
    if(x > 0){
        sprintf(cmd, "python3.6 ../spin/miracle.py %d %d > bfs.txt", x-1, y);
        system(cmd);
        fs = fopen("bfs.txt", "r");
        fscanf(fs,"%d",&i);
        fclose(fs);

        if(i < min){
            *next_x = x-1;
            *next_y = y;
        }
    }
    if(y > 0){
        sprintf(cmd, "python3.6 ../spin/miracle.py %d %d > bfs.txt", x, y-1);
        system(cmd);
        fs = fopen("bfs.txt", "r");
        fscanf(fs,"%d",&i);
        fclose(fs);

        if(i < min){
            *next_x = x;
            *next_y = y-1;
        }
    }
        
    sprintf(cmd, "python3.6 ../spin/miracle.py %d %d > bfs.txt", x, y+1);
    system(cmd);
    fs = fopen("bfs.txt", "r");
    fscanf(fs,"%d",&i);
    fclose(fs);

    if(i < min){
        *next_x = x;
        *next_y = y+1;
    }

    sprintf(cmd, "python3.6 ../spin/miracle.py %d %d > bfs.txt", x+1, y);
    system(cmd);
    fs = fopen("bfs.txt", "r");
    fscanf(fs,"%d",&i);
    fclose(fs);

    if(i < min){
        *next_x = x+1;
        *next_y = y;
    }


    return;
}

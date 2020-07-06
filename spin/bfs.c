#include <stdlib.h>
#include <stdio.h>

#define MAX_LEN 10
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

void calculate_next_move(int x, int y, int* next_x, int* next_y){
    int min = 9999;
    char cmd[50];
    FILE* fs;
    int i = -1;
    char* ret = "Skip";

    
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
    }

    

    printf("Opponent - %s\n", ret);
    return;
}

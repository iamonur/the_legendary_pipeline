#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#define MAX_LEN 26
#define MAX_QUEUE 1024
//#define __DEBUG_PRINT

typedef struct
{
  int X;
  int Y;
  int Value;
  void *NextInSolvedPath;   //AStar_Node*
  void *Neighbors[4];  //AStar_Node*
} AStar_Node;

typedef struct
{
  AStar_Node *node;
  void *next; //AStarNode_List*
} AStarNode_List;

typedef struct
{
  AStar_Node   *CameFrom;
  float        GScore;
  float        FScore;
} NodeDataMap;

AStarNode_List *AllNodesGSet;

int map_[MAX_LEN][MAX_LEN];
int map[MAX_LEN*MAX_LEN];
int goalx, goaly;

float DistanceBetween(int X1,int Y1, int X2, int Y2)
{
  return sqrt((float)((X2-X1)*(X2-X1))+((Y2-Y1)*(Y2-Y1)));
}
float CostOfGoal(int X1,int Y1, int X2, int Y2,int (*GetMap)(int,int))
{
  return DistanceBetween(X1,Y1,X2,Y2);
}
void AddToNodeList(AStarNode_List **List,AStar_Node *NodeToAdd,int *LengthPtr)
{
  AStarNode_List *newNode = malloc(sizeof(*newNode));
  newNode->node = NodeToAdd;
  newNode->next = *List;
  
  *List = newNode;
  
  if (LengthPtr)
  {
    (*LengthPtr)++;
  }
  
  return;
}

AStar_Node *CreateNode(int X,int Y,int Value,AStarNode_List **AllNodesSet)
{
  AStar_Node *ThisNode = malloc(sizeof(*ThisNode));
  ThisNode->X          = X;
  ThisNode->Y          = Y;
  ThisNode->Value      = Value;
  ThisNode->Neighbors[0]  = NULL;
  ThisNode->Neighbors[1]  = NULL;
  ThisNode->Neighbors[2]  = NULL;
  ThisNode->Neighbors[3]  = NULL;
  
  AddToNodeList(AllNodesSet,ThisNode,NULL);
  
  return ThisNode;
}

AStarNode_List *FindInNodeList(AStarNode_List *List,AStar_Node *NodeToFind)
{
  AStarNode_List *FoundNode = NULL;
  AStarNode_List *CurrentNode   = List;
  while (CurrentNode)
  {
    if ((CurrentNode->node->X == NodeToFind->X) && (CurrentNode->node->Y == NodeToFind->Y))
    {
      // Found it.
      FoundNode = CurrentNode;
      break;
    }
    
    CurrentNode = CurrentNode->next;
  }
  
  return FoundNode;
}

void RemoveFromNodeList(AStarNode_List **List,AStar_Node *NodeToRemove,int *LengthPtr)
{
  AStarNode_List *CurrentNode   = *List;
  AStarNode_List *PreviousNode  = NULL;
  while (CurrentNode)
  {
    if ((CurrentNode->node->X == NodeToRemove->X) && (CurrentNode->node->Y == NodeToRemove->Y))
    {
      // Found it.
      if (PreviousNode)
      {
        PreviousNode->next = CurrentNode->next;
      }
      else
      {
        *List = CurrentNode->next;
      }
      
      if (LengthPtr)
      {
        (*LengthPtr)--;
      }
      break;
    }
    else
    {
      PreviousNode = CurrentNode;
      CurrentNode  = CurrentNode->next;
    }
  }
  
  return;
}

void RemoveAllFromNodeList(AStarNode_List **List,int FreeNodes)
{
  if (!List)
  {
    return;
  }
  
  AStarNode_List *CurrentNode   = *List;
  AStarNode_List *NextNode;
  
  while (CurrentNode)
  {
    if (FreeNodes && CurrentNode->node)
    {
      free(CurrentNode->node);
    }
    NextNode = CurrentNode->next;
    free(CurrentNode);
    CurrentNode = NextNode;
  }
  *List = NULL;
  return;
}


AStar_Node *AStar_Find(int mapWidth,int mapHeight,int StartX,int StartY,int EndX,int EndY,int (*GetMap)(int,int),NodeDataMap *dataMap)
{
  AStar_Node     *Neighbor       = NULL;
  AStarNode_List *OpenSet        = NULL;
  AStarNode_List *ClosedSet      = NULL;
  AStarNode_List *NextInOpenSet  = NULL;
  AStar_Node   *AStar_SolvedPath = NULL;
  int           OpenSetLength    = 0;
  float         TentativeGScore  = 0;
  float         TentativeFScore  = 0;
  AStar_Node   *Current;
  float        LowestFScore;
  float        NextFScore;
  int neighbor_pos;
  AStar_Node     TempNodeToFind;
  AStarNode_List *TempNeighborNode;
  int neighborPosInLists;
  
  AllNodesGSet = NULL;
  
  
  if ((GetMap(StartX,StartY) >= 9) || (GetMap(EndX,EndY) >= 9))
  {
    return NULL;
  }
  
  Current = CreateNode(StartX,StartY,GetMap(StartX,StartY),&AllNodesGSet);
  
  dataMap[Current->X + (Current->Y*mapWidth)].GScore   = 0.0;
  dataMap[Current->X + (Current->Y*mapWidth)].FScore   = dataMap[Current->X + (Current->Y*mapWidth)].GScore + CostOfGoal(Current->X,Current->Y,EndX,EndY,GetMap);
  dataMap[Current->X + (Current->Y*mapWidth)].CameFrom = NULL;
  
  AddToNodeList(&OpenSet,Current,&OpenSetLength);
  
  while (OpenSetLength)
  {
    Current = NULL;
    NextInOpenSet = OpenSet;
    LowestFScore = dataMap[NextInOpenSet->node->X + (NextInOpenSet->node->Y*mapWidth)].FScore;
    while (NextInOpenSet)
    {
      NextFScore = dataMap[NextInOpenSet->node->X + (NextInOpenSet->node->Y*mapWidth)].FScore;
      if (!Current || (LowestFScore > NextFScore))
      {
        Current = NextInOpenSet->node;
        LowestFScore = NextFScore;
      }
      NextInOpenSet = NextInOpenSet->next;
    }
    
    
    if ((Current->X == EndX) && (Current->Y == EndY))
    {
      AStar_SolvedPath = Current;
      break;
    }
    
    RemoveFromNodeList(&OpenSet,Current,&OpenSetLength);
    if (!FindInNodeList(ClosedSet,Current))
    {
      AddToNodeList(&ClosedSet,Current,NULL);
    }
    for (neighbor_pos = 0;neighbor_pos < 4;neighbor_pos++)
    {
      Neighbor = Current->Neighbors[neighbor_pos];
      if (!Neighbor)
      {
        TempNodeToFind.X = Current->X;
        TempNodeToFind.Y = Current->Y;
        switch(neighbor_pos)
        {
          case 0:
            TempNodeToFind.Y--;
            break;
          case 1:
            TempNodeToFind.X++;
            break;
          case 2:
            TempNodeToFind.Y++;
            break;
          default:
            // Assumed 3
            TempNodeToFind.X--;
        }
        
        if ((TempNodeToFind.X >= 0) && (TempNodeToFind.X < mapWidth)
            &&
            (TempNodeToFind.Y >= 0) && (TempNodeToFind.Y < mapHeight)
            && (GetMap(TempNodeToFind.X,TempNodeToFind.Y) == 1))
        {
          TempNeighborNode = FindInNodeList(AllNodesGSet,&TempNodeToFind);
          if (TempNeighborNode)
          {
            Neighbor = TempNeighborNode->node;
          }
          else
          {
#ifdef __DEBUG_PRINT
            printf("Creating new neighbor\n");
#endif
            Neighbor = CreateNode(TempNodeToFind.X,TempNodeToFind.Y,GetMap(TempNodeToFind.X,TempNodeToFind.Y),&AllNodesGSet);
          }
          
#ifdef __DEBUG_PRINT
          printf("Linking current node and neighbor as, well, neighbors\n");
#endif
          Current->Neighbors[neighbor_pos] = Neighbor;
          switch(neighbor_pos)
          {
            case 0:
              Neighbor->Neighbors[2] = Current;
              break;
              
            case 1:
              Neighbor->Neighbors[3] = Current;
              break;
              
            case 2:
              Neighbor->Neighbors[0] = Current;
              break;
              
            default:
              // Assumed 3
              Neighbor->Neighbors[1] = Current;
          }
        }
        else
        {
        }
      }
      
      if (Neighbor)
      {
        TentativeGScore = dataMap[Current->X + (Current->Y * mapWidth)].GScore + DistanceBetween(Current->X,Current->Y,Neighbor->X,Neighbor->Y);

        TentativeFScore = TentativeGScore + CostOfGoal(Neighbor->X,Neighbor->Y,EndX,EndY,GetMap);

        
        neighborPosInLists = Neighbor->X + (Neighbor->Y * mapWidth);
        if (!FindInNodeList(ClosedSet,Neighbor) || (TentativeFScore < dataMap[neighborPosInLists].FScore))
        {
          if (!FindInNodeList(OpenSet,Neighbor) || (TentativeFScore < dataMap[neighborPosInLists].FScore))
          {
            if (!dataMap[neighborPosInLists].CameFrom)
            {
              dataMap[neighborPosInLists].CameFrom = Current;
            }
            dataMap[neighborPosInLists].GScore   = TentativeGScore;
            dataMap[neighborPosInLists].FScore   = TentativeFScore;
          
            if (!FindInNodeList(OpenSet,Neighbor))
            {

              AddToNodeList(&OpenSet,Neighbor,&OpenSetLength);
            }
          }
        }
      }
    }
  }
  
  RemoveAllFromNodeList(&OpenSet,0);
  RemoveAllFromNodeList(&ClosedSet,0);
  return AStar_SolvedPath;
}


void map_print2(){
   int mp2i, mp2j;
   for(mp2i = 0; mp2i < MAX_LEN; mp2i++){
       for(mp2j = 0; mp2j < MAX_LEN; mp2j++){
           printf("%d",now.map[mp2i].a[mp2j]);
       }
       printf("\n");
   }
 
}

void map_print(){
    for(int i = 0; i < MAX_LEN; i++)
    {
        for(int j = 0; j < MAX_LEN; j++){
            printf("%d",map[i*MAX_LEN + j]);
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

int CustomGetMap( int x, int y )
{
	if( x < 0 || x >= MAX_LEN || y < 0 || y >= MAX_LEN )
	{
		return 9;	 
	}

	return map[y*MAX_LEN+x];
}

void put_map_2_memory_portal_goal(){
    int i, j;
    for(i = 0; i < MAX_LEN; i++){
        for(j = 0; j < MAX_LEN; j++){
            switch (now.map[i].a[j])
            {
            case 1:
                map[MAX_LEN*i+j] = 9;
                break;
            case 3:
                goalx = i;
                goaly = j;            
            default:
                map[MAX_LEN*i+j] = 1;
            }
        }
    }
}

void put_map_2_memory_portal_goal_avatar_wall(){
    int i, j;
    for(i = 0; i < MAX_LEN; i++){
        for(j = 0; j < MAX_LEN; j++){
            switch (now.map[i].a[j])
            {
            case 1:
            case 2:
                map[MAX_LEN*i+j] = 9;
                break;
            case 3:
                goalx = i;
                goaly = j;            
            default:
                map[MAX_LEN*i+j] = 1;
            }
        }
    }
}

void put_map_2_memory_avatar_goal(){
    int i, j;
    for(i = 0; i < MAX_LEN; i++){
        for(j = 0; j < MAX_LEN; j++){
            switch (now.map[i].a[j])
            {
            case 1:
                map[MAX_LEN*i+j] = 9;
                break;
            case 2:
                goalx = i;
                goaly = j;            
            default:
                map[MAX_LEN*i+j] = 1;
            }
        }
    }
}

void calculate_next_move_to_avatar(int xx, int yy, int xxx, int yyy, int* next_x, int* next_y){
    put_map_2_memory_portal_goal();
    int x,y,i;
      
  AStar_Node *Solution;
  AStar_Node *NextInSolution;
  AStar_Node *SolutionNavigator;
  int NextInSolutionPos;
  NodeDataMap *dataMap = (NodeDataMap*)malloc(sizeof(*dataMap) * MAX_LEN * MAX_LEN);
  
  for (i=0;i<MAX_LEN * MAX_LEN;i++)
  {
    dataMap[i].GScore   = 0.0;
    dataMap[i].FScore   = 0.0;
    dataMap[i].CameFrom = NULL;
  }
  int StartX = yy, StartY = xx, EndX = yyy, EndY = xxx;
   
  Solution = AStar_Find(MAX_LEN,MAX_LEN,StartX,StartY,EndX,EndY,CustomGetMap,dataMap);
    
 

  SolutionNavigator = NULL;
  NextInSolution = Solution;
  
  // NextInSolution will actually refer to the next node from end to start (that is, we're going reverse from the target).
  if (NextInSolution)
  {
    do
    {
      NextInSolutionPos = NextInSolution->X + (NextInSolution->Y * MAX_LEN);
      NextInSolution->NextInSolvedPath = SolutionNavigator;
      SolutionNavigator = NextInSolution;
      NextInSolution = dataMap[NextInSolutionPos].CameFrom;
    }
    while ((SolutionNavigator->X != StartX) || (SolutionNavigator->Y != StartY));
  }
  *next_y = ((AStar_Node*)SolutionNavigator->NextInSolvedPath)->X;
  *next_x = ((AStar_Node*)SolutionNavigator->NextInSolvedPath)->Y;
  
  printf("Opponent - [%d,%d]\n", (*next_y-yy), (*next_x-xx));
  RemoveAllFromNodeList(&AllNodesGSet,1);
  
  free(dataMap);
}

void calculate_next_move_to_portal_avatar_blocks(int xx, int yy, int* next_x, int* next_y){
    put_map_2_memory_portal_goal();
    int x,y,i;
      
  AStar_Node *Solution;
  AStar_Node *NextInSolution;
  AStar_Node *SolutionNavigator;
  int NextInSolutionPos;
  NodeDataMap *dataMap = (NodeDataMap*)malloc(sizeof(*dataMap) * MAX_LEN * MAX_LEN);
  
  for (i=0;i<MAX_LEN * MAX_LEN;i++)
  {
    dataMap[i].GScore   = 0.0;
    dataMap[i].FScore   = 0.0;
    dataMap[i].CameFrom = NULL;
  }
  int StartX = yy, StartY = xx, EndX = goaly, EndY = goalx;
   
  Solution = AStar_Find(MAX_LEN,MAX_LEN,StartX,StartY,EndX,EndY,CustomGetMap,dataMap);
    
 
  SolutionNavigator = NULL;
  NextInSolution = Solution;
  //printf("a\n");
  // NextInSolution will actually refer to the next node from end to start (that is, we're going reverse from the target).
  if (NextInSolution)
  {
    do
    {
      NextInSolutionPos = NextInSolution->X + (NextInSolution->Y * MAX_LEN);
      NextInSolution->NextInSolvedPath = SolutionNavigator;
      SolutionNavigator = NextInSolution;
      NextInSolution = dataMap[NextInSolutionPos].CameFrom;
    }
    while ((SolutionNavigator->X != StartX) || (SolutionNavigator->Y != StartY));
  }
  //printf("b\n");
  *next_y = ((AStar_Node*)SolutionNavigator->NextInSolvedPath)->X;
  *next_x = ((AStar_Node*)SolutionNavigator->NextInSolvedPath)->Y;
  printf("Opponent - [%d,%d]\n", (*next_y-yy), (*next_x-xx));
  RemoveAllFromNodeList(&AllNodesGSet,1);
  free(dataMap);
}



int _calculate_next_move_to_portal(int xx, int yy){
    put_map_2_memory_portal_goal();
    //if(map[MAX_LEN*xx+yy]==1) return 10000;
    int x,y,i;
      
  AStar_Node *Solution;
  AStar_Node *NextInSolution;
  AStar_Node *SolutionNavigator;
  int NextInSolutionPos;
  NodeDataMap *dataMap = (NodeDataMap*)malloc(sizeof(*dataMap) * MAX_LEN * MAX_LEN);
  
  for (i=0;i<MAX_LEN * MAX_LEN;i++)
  {
    dataMap[i].GScore   = 0.0;
    dataMap[i].FScore   = 0.0;
    dataMap[i].CameFrom = NULL;
  }
  int StartX = yy, StartY = xx, EndX = goaly, EndY = goalx;
   
  Solution = AStar_Find(MAX_LEN,MAX_LEN,StartX,StartY,EndX,EndY,CustomGetMap,dataMap);
    
 

  SolutionNavigator = NULL;
  NextInSolution = Solution;
  int asd = 0;
  // NextInSolution will actually refer to the next node from end to start (that is, we're going reverse from the target).
  if (NextInSolution)
  {
    
    do
    {
      asd++;
      NextInSolutionPos = NextInSolution->X + (NextInSolution->Y * MAX_LEN);
      NextInSolution->NextInSolvedPath = SolutionNavigator;
      SolutionNavigator = NextInSolution;
      NextInSolution = dataMap[NextInSolutionPos].CameFrom;
    }
    while ((SolutionNavigator->X != StartX) || (SolutionNavigator->Y != StartY));
  }
  /*printf("%d\n",asd);
  *next_y = ((AStar_Node*)SolutionNavigator->NextInSolvedPath)->X;
  *next_x = ((AStar_Node*)SolutionNavigator->NextInSolvedPath)->Y;*/

  //printf("Opponent - [%d,%d]\n", (*next_y-yy), (*next_x-xx));
  
  RemoveAllFromNodeList(&AllNodesGSet,1);
  
  free(dataMap);
  //printf("%d\n",asd);
  if(asd == 0) return 10000;
  return asd;
}

void calculate_next_move_to_portal(int xx, int yy, int* next_x, int* next_y){
  int base = _calculate_next_move_to_portal(xx, yy);
  //fprintf(stderr,"%d\n",base);
  if(_calculate_next_move_to_portal(xx, yy + 1) < base){
    *next_y = yy+1;
    *next_x = xx;
    base = _calculate_next_move_to_portal(xx, yy + 1);
        printf("Opponent - [1,0]\n");
  }
  if(_calculate_next_move_to_portal(xx + 1, yy) < base){
    *next_x = xx+1;
    *next_y = yy;
    base = _calculate_next_move_to_portal(xx + 1, yy);
        printf("Opponent - [0,1]\n");

  }
  
  
  
  if(_calculate_next_move_to_portal(xx, yy - 1) < base){
    *next_y = yy -1;
    *next_x = xx;
    base = _calculate_next_move_to_portal(xx, yy - 1);
        printf("Opponent - [-1,0]\n");
  }
  if(_calculate_next_move_to_portal(xx - 1, yy) < base){
    base = _calculate_next_move_to_portal(xx, yy - 1);
    *next_x = xx-1;
    *next_y=yy;
    printf("Opponent - [0,-1]\n");
  }
  //fprintf(stderr,"%d\n",base);
  //fprintf(stderr,"-------------------\n");
  //printf("%d %d\n", *next_x, *next_y);
}
void calculate_next_move2(int x, int y, int* next_x, int* next_y){
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

    return;
}

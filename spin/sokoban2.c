#ifndef NUM_OF_BOXES 
#define NUM_OF_BOXES 1
#endif

#ifndef MAX_LEN
#define MAX_LEN 26
#endif

#define NUM_OF_CHOICES NUM_OF_BOXES*4

char sokoban_map[MAX_LEN][MAX_LEN];
char sokoban_map2[MAX_LEN][MAX_LEN];

unsigned int sokoban_avatar_1, sokoban_avatar_2;
void soko_map_print(){
    for(int i = 0; i < MAX_LEN; i++)
    {
        for(int j = 0; j < MAX_LEN; j++){
            fprintf(stderr, "%c",sokoban_map[i][j]);
        }
        fprintf(stderr, "\n");
    }
}
void sokoban_putMapToMem() {
  unsigned int i, j;

  for(i = 0; i < MAX_LEN; i++) {
    for(j = 0; j < MAX_LEN; j++) {
      switch(now.map[i].a[j]){
        case 0:
          sokoban_map[i][j] = ' ';
        break;
        case 1:
          sokoban_map[i][j] = 'w';
        break;
        case 2:
          sokoban_map[i][j] = 'a';
          sokoban_avatar_1 = i;
          sokoban_avatar_2 = j;
        break;
        case 3:
          sokoban_map[i][j] = 'b';
        break;
        case 4:
          sokoban_map[i][j] = 'h';
        break;
        default:
          exit(0);
      }
    }
  }

}

void sokoban_recurseAvatarizedMap(int avatar_f, int avatar_s) {
  sokoban_map2[avatar_f][avatar_s] = 'a';
  if( sokoban_map2[avatar_f - 1][avatar_s] == ' ')
    sokoban_recurseAvatarizedMap(avatar_f - 1, avatar_s);
  if( sokoban_map2[avatar_f + 1][avatar_s] == ' ')
    sokoban_recurseAvatarizedMap(avatar_f + 1, avatar_s);
  if( sokoban_map2[avatar_f][avatar_s - 1] == ' ')
    sokoban_recurseAvatarizedMap(avatar_f, avatar_s - 1);
  if( sokoban_map2[avatar_f][avatar_s + 1] == ' ')
    sokoban_recurseAvatarizedMap(avatar_f, avatar_s + 1);
  return;
}

void sokoban_getAvatarizedMap() {
  memcpy(sokoban_map2, sokoban_map, MAX_LEN * MAX_LEN);
  sokoban_recurseAvatarizedMap(sokoban_avatar_1, sokoban_avatar_2);
}

void sokoban_updateTarget(int coor_1, int coor_2, int box_num) {
  if(sokoban_map2[coor_1 - 1][coor_2] == 'a')
    switch(sokoban_map2[coor_1 + 1][coor_2]){
      case 'a':
      case ' ':
      case 'h':
        now.choices[box_num*4 + 0] = 1;
      break;
      default:
        now.choices[box_num*4 + 0] = 0;
    }
  else now.choices[box_num*4 + 0] = 0;

  if(sokoban_map2[coor_1][coor_2 - 1] == 'a')
    switch(sokoban_map2[coor_1][coor_2 + 1]){
      case 'a':
      case ' ':
      case 'h':
        now.choices[box_num*4 + 1] = 1;
      break;
      default:
        now.choices[box_num*4 + 1] = 0;
    }
  else now.choices[box_num*4 + 1] = 0;

  if(sokoban_map2[coor_1 + 1][coor_2] == 'a')
    switch(sokoban_map2[coor_1 - 1][coor_2]){
      case 'a':
      case ' ':
      case 'h':
        now.choices[box_num*4 + 2] = 1;
      break;
      default:
        now.choices[box_num*4 + 2] = 0;
    }
  else now.choices[box_num*4 + 2] = 0;

  if(sokoban_map2[coor_1][coor_2 + 1] == 'a')
    switch(sokoban_map2[coor_1][coor_2 - 1]){
      case 'a':
      case ' ':
      case 'h':
        now.choices[box_num*4 + 3] = 1;
      break;
      default:
        now.choices[box_num*4 + 3] = 0;
    }
  else now.choices[box_num*4 + 3] = 0;
  return;
}

void sokoban_updateAllTargets(){

  for(unsigned int a = 0; a < NUM_OF_BOXES*4; a++) {
    now.choices[a] = 0;
  }

  sokoban_getAvatarizedMap();

  unsigned char box_number = 0;
  for(unsigned int i = 0; i < MAX_LEN; i++) {
    for(unsigned int j = 0; j < MAX_LEN; j++) {
      if(sokoban_map2[i][j] == 'b') {
        sokoban_updateTarget(i,j,box_number);
        box_number++;
      }
    }
  }

  now.remaining_goals = box_number;
}

void push_a_box(unsigned int ind1, unsigned int ind2, unsigned int pos) {
  now.map[ind1].a[ind2] = 2;
  now.map[sokoban_avatar_1].a[sokoban_avatar_2] = 0;
  printf("Push@ %d %d ; Side: %d\n", ind1-1, ind2-1, pos);
  switch(pos) {
    case 0:
      switch(sokoban_map[ind1 + 1][ind2]) {
        
        case 'a':
        case ' ':
          now.map[ind1 + 1].a[ind2] = 3;
        break;
        case 'h':
          now.map[ind1 + 1].a[ind2] = 0;
          now.remaining_goals--;
        break;
        default:
          exit(0);
      }
    break;
    case 1:
      switch(sokoban_map[ind1][ind2 + 1]){
        case 'a':
        case ' ':
          now.map[ind1].a[ind2 + 1] = 3;
        break;
        case 'h':
          now.map[ind1].a[ind2 + 1] = 0;
          now.remaining_goals--;
        break;
        default:
          exit(0);
      }
    break;
    case 2:
      switch(sokoban_map[ind1 - 1][ind2]){
        case 'a':
        case ' ':
          now.map[ind1 - 1].a[ind2] = 3;
        break;
        case 'h':
          now.map[ind1 - 1].a[ind2] = 0;
          now.remaining_goals--;
        break;
        default:
          exit(0);
      }
    break;
    case 3:
      switch(sokoban_map[ind1][ind2 - 1]) {
        case 'a':
        case ' ':
          now.map[ind1].a[ind2 - 1] = 3;
        break;
        case 'h':
          now.map[ind1].a[ind2 - 1] = 0;
          now.remaining_goals--;
        break;
        default:
          exit(0);
      }
    break;
    default:
      exit(0);
  }

}

void push(int choice){
  unsigned int box = choice/4;
  unsigned int side = choice%4;
  //soko_map_print();
  for(unsigned int i = 0; i < MAX_LEN; i++){
    for(unsigned int j = 0; j < MAX_LEN; j++){
      if(sokoban_map[i][j] == 'b') {
        if(box == 0){
          push_a_box(i, j, side);
          sokoban_putMapToMem();
          return;
        }
        else box--;
      }
    }
  }
}

void sokoban_init(){
  sokoban_putMapToMem();

  sokoban_updateAllTargets();
}

void sokoban_push(unsigned int choice){
  sokoban_putMapToMem();
  push(choice);
  //soko_map_print();
  sokoban_updateAllTargets();
}
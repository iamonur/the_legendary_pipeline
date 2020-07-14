import collections
import sys

def bfs_python(level, wall='1', floor='0', frm=(0,0), goal='G'):

    frm = (frm[1], frm[0])

    width = len(level[0])
    height = len(level)


    if frm[0] >= height or frm[1] >= width or frm[0] < 0 or frm[1] < 0:
        return 10000

    if level[frm[1]][frm[0]] == wall:
        return 10000
        
    queue = collections.deque([[frm]])
    seen = set([frm])
    

    while queue:
        path = queue.popleft()
        x, y = path[-1]
        if level[y][x] == goal:
            if path is None:
                return 10000
            
            return len(path)
        for x2, y2 in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
            if 0 <= x2 < width and 0 <= y2 < height and level[y2][x2] != wall and (x2, y2) not in seen:
                queue.append(path + [(x2, y2)])
                seen.add((x2, y2))

    return 10000

if __name__ == "__main__":

    f = open("../src/level4pml.txt", "r")
    file_all = f.read()
    lines = file_all.split("\n")

    top = str(sys.argv[1])
    left = str(sys.argv[2])
    
    for line in lines:
        line = line.replace("E","0")
        line = line.replace("A","0")
        
    print(bfs_python(lines[:-1], frm=(int(top),int(left))))
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def get_file_list():
    files_here = os.listdir()
    for file in files_here:
        if ".py" not in file:
            directory = file
            break
    os.chdir(directory)
    files_here = os.listdir()
    csv_files = []
    for file in files_here:
        if ".csv" in file:
            temp = file.split('w')[1]
            wall = temp.split('f')[0]
            temp = temp.split('f')[1]
            floor = temp.split('p')[0]
            temp = temp.split('p')[1]
            portal = temp.split('.')[0]
            csv_files.append([directory + "/" + file, int(wall), int(floor), int(portal)])
    return csv_files

def parse_csv_file(file_structure):
    file = open(file_structure[0].split("/")[1], "r")
    lines = file.readlines()
    file.close()
    results = []
    for line in lines:
        list_line = line.split(',')
        moves = list_line[0].split("*")
        score = int(list_line[1])
        if list_line[2] == "True":
            terminal = True
        else:
            terminal = False
        timing = float(list_line[3])
        results.append([moves, score, terminal, timing])
    return results

def compute_on_results(results):
    avg_cost = 0.0
    avg_reward = 0.0
    win_rating = 0.0
    best_game = results[0]
    worst_game = results[0]
    count = 0 #I could use a .len for this, but this will save few clocks.
    
    for result in results:
        count += 1
        avg_cost += result[3]
        avg_reward += result[1]
        win_rating += int(result[2])

        if result[1] < worst_game[1]: #New worst
            worst_game = result
        if result[1] > best_game[1]: #New best
            best_game = result

    avg_cost = avg_cost/count
    avg_reward = avg_reward/count
    win_rating = win_rating/count

    return [avg_cost, avg_reward, win_rating], best_game, worst_game


def fitness(win_rate, reward, max_reward):
    if reward == max_reward:
        return float(99999999)
    return win_rate*abs(max_reward/(max_reward-reward))

def compute_on_all():
    file_list = get_file_list()
    all_results = []
    for item in file_list:
        result,best,worst = compute_on_results(parse_csv_file(item));
        temp_dict = {
            "wall":item[1],
            "floor":item[2],
            "portal":item[3],
            "time":result[0],
            "reward":result[1],
            "win_rating":result[2],
            "fitness":fitness(result[2], result[1], ( 9 * item[2] + item[3] ) )
        }
        all_results.append(temp_dict)
    return all_results

def group_on_portal_reward(all_results):
    ret_dict = {1:[],5:[],25:[],125:[],625:[],3125:[],15625:[],78125:[],390625:[],1953125:[]}
    for result in all_results:
        ret_dict[result["portal"]].append(result)
    return ret_dict

def get_numpy_array_from_list(li, to_be_plotted="time"):
    #Group them around wall first

    dictionary = {-1:[],-4:[],-16:[],-64:[],-256:[],-1024:[],-4096:[]}
    for item in li:
        dictionary[item["wall"]].append([item["floor"],item[to_be_plotted]])


    dict_list = [ [-4096,dictionary[-4096]], [-1024,dictionary[-1024]], [-256,dictionary[-256]], [-64,dictionary[-64]], [-16,dictionary[-16]], [-4,dictionary[-4]], [-1,dictionary[-1]]]


    for elnum,elem in enumerate(dict_list):
        dict_list[elnum][1] = sorted(elem[1], key=lambda lili: lili[0])

    #Now both are sorted.

    ret = np.empty((7,7),dtype=np.float64)
    
    for n1,item1 in enumerate(dict_list):
        for n2,item2 in enumerate(item1[1]):
            ret[n1][n2] = item2[1]
            
    return ret

def save_np_array_heatmap(arr, name):
    ax = sns.heatmap(arr, linewidth=0, xticklabels=[-4096,-1024,-256,-64,-16,-4,-1], yticklabels=[-4096,-1024,-256,-64,-16,-4,-1], cmap="YlOrRd", annot=True)
    plt.title(name)
    plt.ylabel("Wall Hit Reward")
    plt.xlabel("Floor Hit Reward")
    ax.figure.savefig(name+".png")

    

if __name__ == "__main__":
    to_be_plotted_portal_reward = 5
    portal_dict = group_on_portal_reward(compute_on_all())
    portal_rewards = [1,25,625,15625,390625]
    for rew in portal_rewards:
        save_np_array_heatmap(get_numpy_array_from_list(portal_dict[rew]),"Portal_reward:"+str(rew))
        plt.clf()

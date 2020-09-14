import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

def get_file_list():
    files_here = os.listdir()
    for file in files_here:
        if ".py" not in file:
            directory = file
            break
    directory="dataset_best"
    
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

def get_file_list_2():
    files_here = os.listdir()
    for file in files_here:
        if ".py" not in file:
            directory = file
            break
    directory="zzz"
    
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

def compute_on_all_2():
    file_list = get_file_list_2()
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
    ret_dict = {1:[],5:[],25:[],125:[],625:[],3125:[],15625:[],78125:[],390625:[]}
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

def save_alternate_graph(whole_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    """portal_rewards=[625,15625,390625]
    wall_rewards=[-2048,-128,-32,-8,-2,0]
    floor_rewards=[-2048,-128,-32,-8,-2,0]"""
    portal_rewards=[2,3,4]
    wall_rewards=[11,7,5,3,1,-1]
    floor_rewards=[11,7,5,3,1,-1]
    dp_count = len(whole_data)*len(whole_data[0])*len(whole_data[0][0])
    
    portal_reward = np.random.standard_normal(dp_count)
    wall_reward = np.random.standard_normal(dp_count)
    floor_reward = np.random.standard_normal(dp_count)
    data_points = np.random.standard_normal(dp_count)
    index = 0
    for pn,portal in enumerate(whole_data):
        for wn,wall in enumerate(portal):
           for fn, value in enumerate(wall):
               portal_reward[index] = portal_rewards[pn]
               wall_reward[index] = wall_rewards[wn]
               floor_reward[index] = floor_rewards[fn]
               data_points[index] = value
               index += 1
    

    img = ax.scatter(portal_reward, wall_reward, floor_reward, c=data_points, cmap=plt.hot(), s=200)
    ax.set_xlabel("Portal Reward")
    ax.set_ylabel("Wall Reward")
    ax.set_zlabel("Floor Reward")
    plt.title("Graph #2")
    fig.colorbar(img)
    plt.show()

def save_another_type_graph(whole_data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
#    portal_rewards=[1,25,625,15625,390625]
    portal_rewards=[0,1,2,3,4]#log25(x)
#    wall_rewards=[4096,1024,256,64,16,4,1]
    wall_rewards=[12,10,8,6,4,2,0]#log2(-x)
#    floor_rewards=[4096,1024,256,64,16,4,1]
    floor_rewards=[12,10,8,6,4,2,0]#log2(-x)
    dp_count = len(whole_data)*len(whole_data[0])*len(whole_data[0][0])
    
    portal_reward = np.random.standard_normal(dp_count)
    wall_reward = np.random.standard_normal(dp_count)
    floor_reward = np.random.standard_normal(dp_count)
    data_points = np.random.standard_normal(dp_count)
    index = 0
    for pn,portal in enumerate(whole_data):
        for wn,wall in enumerate(portal):
           for fn, value in enumerate(wall):
               portal_reward[index] = portal_rewards[pn]
               wall_reward[index] = wall_rewards[wn]
               floor_reward[index] = floor_rewards[fn]
               data_points[index] = value
               index += 1
    

    img = ax.scatter(portal_reward, wall_reward, floor_reward, c=data_points, cmap=plt.hot(), s=200)
    ax.set_xlabel("Portal Reward")
    ax.set_ylabel("Wall Reward")
    ax.set_zlabel("Floor Reward")
    #ax.set_xscale('log')
    #ax.set_yscale('log')
    #ax.set_zscale('log')
    plt.title("Graph #1")
    fig.colorbar(img)
    plt.show()



#if __name__ == "__main__":
def main_1():
    portal_dict = group_on_portal_reward(compute_on_all())
    portal_rewards = [1,25,625,15625,390625]
    for rew in portal_rewards:
        save_np_array_heatmap(get_numpy_array_from_list(portal_dict[rew]),"Portal_reward:"+str(rew))
        plt.clf()

def get_listoflist_2(lili, to_be_plotted="win_rating"):
        #Group them around wall first

    dictionary = {0:[],-2:[],-8:[],-32:[],-128:[],-2048:[]}
    for item in lili:
        dictionary[item["wall"]].append([item["floor"],item[to_be_plotted]])


    dict_list = [ [-2048,dictionary[-2048]], [-128,dictionary[-128]], [-32,dictionary[-32]], [-8,dictionary[-8]], [-2,dictionary[-2]], [0,dictionary[0]]]

    for elnum,elem in enumerate(dict_list):
        dict_list[elnum][1] = sorted(elem[1], key=lambda lili: lili[0])

    #Now both are sorted.

    #ret = np.empty((7,7),dtype=np.float64)
    ret = []
    for n1, item1 in enumerate(dict_list):
        ret2 = []
        for n2, item2 in enumerate(item1[1]):
            ret2.append(item2[1])
        ret.append(ret2)
    return ret

def get_listoflist(lili, to_be_plotted="win_rating"):
        #Group them around wall first

    dictionary = {-1:[],-4:[],-16:[],-64:[],-256:[],-1024:[],-4096:[]}
    for item in lili:
        dictionary[item["wall"]].append([item["floor"],item[to_be_plotted]])


    dict_list = [ [-4096,dictionary[-4096]], [-1024,dictionary[-1024]], [-256,dictionary[-256]], [-64,dictionary[-64]], [-16,dictionary[-16]], [-4,dictionary[-4]], [-1,dictionary[-1]]]


    for elnum,elem in enumerate(dict_list):
        dict_list[elnum][1] = sorted(elem[1], key=lambda lili: lili[0])

    #Now both are sorted.

    #ret = np.empty((7,7),dtype=np.float64)
    ret = []
    for n1, item1 in enumerate(dict_list):
        ret2 = []
        for n2, item2 in enumerate(item1[1]):
            ret2.append(item2[1])
        ret.append(ret2)
    return ret


def main_4D():
    #save_another_type_graph(None)
    portal_dict = group_on_portal_reward(compute_on_all())
    portal_rewards = [1,25,625,15625,390625]
    lilili = []
    for a in portal_rewards:
        lilili.append(get_listoflist(portal_dict[a]))

    save_another_type_graph(lilili)

def main_4D_2():
    portal_dict = group_on_portal_reward(compute_on_all_2())
    portal_rewards = [625,15625,390625]
    lilili = []
    for a in portal_rewards:
        lilili.append(get_listoflist_2(portal_dict[a]))

    save_alternate_graph(lilili)

if __name__ == "__main__":
    main_4D_2()

import time

import graph
from city_graphs import graph_from_file
import hyper_graph as hg
from random import choice
import cluster_graph as cg

def simulate_traffic(city_graph,num_of_simulated_paths = 10,*,printall=True):

    nodes_used = dict()
    print("Number of nodes: ",len(city_graph.nodes))

    print("Number of simulations: ",num_of_simulated_paths)


    if printall:
        print("#: (start,end) - [path]")

    start_time = time.time()
    for i in range(num_of_simulated_paths):
        try:
            start_node, end_node, path = simulate_traffic_path(city_graph, nodes_used)
        except:
            start_node = end_node = path = "ERROR"
        if printall:
            print(str(i + 1) + ": (" + str(start_node) + ", " + str(end_node) + ")" + " - " + str(path))

    end_time = time.time()
    print("Simulation time: ",end_time-start_time)
    print("Average time per simulation: ",(end_time-start_time)/num_of_simulated_paths)


    print("Most used nodes: ")
    for _ in range(min(10,len(nodes_used)//10)):
        key,value = max(list(nodes_used.items()),key=lambda x:x[1])
        print(""+str(key)+": "+str(value),end="; ")
        nodes_used.pop(key)
    print()


    return nodes_used


def simulate_traffic_path(city_graph,nodes_used):
    start_node = choice(list(city_graph.nodes))
    end_node = choice(list(city_graph.nodes))

    path = city_graph.shortest_path(start_node, end_node)

    for node in path:
        if node not in nodes_used:
            nodes_used[node] = 1
        else:
            nodes_used[node] += 1

    return start_node,end_node,path

if __name__ == "__main__":

    main_graph = graph_from_file("RepublicofSrpska")

    print("Regular graph: ")
    start_time = time.time()
    #banja_luka_graph = graph.Graph(main_graph)
    end_time = time.time()
    print("Creation time: ", end_time - start_time)
    #simulate_traffic(banja_luka_graph,num_of_simulated_paths=500,printall=False)
    print()

    print("HyperGraph: ")
    start_time = time.time()
    #banja_luka_graph = hg.HyperGraph(main_graph)
    end_time = time.time()
    print("Creation time: ", end_time - start_time)
    #simulate_traffic(banja_luka_graph,num_of_simulated_paths=500,printall=False)
    print()

    print("ClusterGraph: ")
    start_time = time.time()
    banja_luka_graph = cg.ClusterGraph(main_graph,max_cluster_size = 50)
    end_time = time.time()
    print("Creation time: ",end_time-start_time)
    simulate_traffic(banja_luka_graph,num_of_simulated_paths=10,printall=True)
    print()









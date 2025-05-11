import time
from random import choice

import cluster_graph as cg
from utils import *


def simulate_traffic(city_graph: nx.Graph ,num_of_simulated_paths = 10,*,log=False,total_nodes=None,console=""):

    nodes_used = dict()

    if log:
        print("Number of nodes: ",len(city_graph.nodes))
        print("Number of simulations: ",num_of_simulated_paths)

    start_time = time.time()
    for i in range(num_of_simulated_paths):
        print(f"\r{console}Path simulations: {i}/{num_of_simulated_paths}", end=" ")
        try:
            path = simulate_traffic_path(city_graph, nodes_used)
            if total_nodes is not None:
                for node in path:
                    if node in total_nodes:
                        total_nodes[node] +=  1
                    else:
                        total_nodes[node] = 1
        except:
            pass


    end_time = time.time()
    if log:
        print("Simulation time: ",end_time-start_time)
        print("Average time per simulation: ",(end_time-start_time)/num_of_simulated_paths)

        print("Most used nodes: ")
        copy = nodes_used.copy()
        for _ in range(min(10,len(copy)//10)):
            key,value = max(list(copy.items()),key=lambda x:x[1])
            print(""+str(key)+": "+str(value),end="; ")
            copy.pop(key)
        print()


    return nodes_used


def simulate_traffic_path(city_graph: nx.Graph,nodes_used):
    start_node = choice(list(city_graph.nodes))
    end_node = choice(list(city_graph.nodes))

    path = nx.dijkstra_path(city_graph,start_node,end_node)

    for node in path:
        nodes_used[node]=nodes_used.get(node,0) + 1

    return path

def interpret_graph_data(data,total_nodes,nodes_used_per_iteration,cluster_graph,cg_nodes,cg_per_iteration,c_total_nodes):
    print("Matching and interpreting data...")
    total_match = match_data(cluster_graph,cg_nodes,total_nodes)
    iteration_match = [(match_data(cluster_graph,cg_per_iteration[i],nodes_used_per_iteration[i]),nodes_used_per_iteration[i]) for i in range(len(cg_per_iteration))]

    graph_list = sorted([(node, uses) for node, uses in total_nodes.items()], key=lambda x: x[1], reverse=True)[:20]
    cluster_list = sorted([(node, uses) for node, uses in cg_nodes.items()], key=lambda x: x[1], reverse=True)[:20]

    output = str(data)+"\nTop 20 clusters[lat,long]: \nname,lat,long\n"
    counter = 1
    for cluster,_ in cluster_list:
        x,y = cluster_graph.get_cluster_coordinate(cluster)
        output += f"{cluster}(#{counter}),{y},{x}\n"
        counter += 1
    output+=str(cluster_list)+"\n"

    output+="\nTop 20 nodes in regular graph: \nname,lat,long\n"
    counter = 1
    for node,_ in graph_list:
        x,y = cluster_graph.get_node_coordinates(node)
        output += f"{node}(#{counter}),{y},{x}\n"
        counter += 1
    output+=str(graph_list)+"\n"
    output += "\nTop 20 nodes in cluster graph: \nname,lat,long\n"
    counter = 1
    c_total_nodes = sorted([(node, uses) for node, uses in c_total_nodes.items()], key=lambda x: x[1], reverse=True)[:20]
    for node, _ in c_total_nodes:
        x, y = cluster_graph.get_node_coordinates(node)
        output += f"{node}(#{counter}),{y},{x}\n"
        counter += 1
    output += str(c_total_nodes) + "\n"

    output += str({node[0]: clustergraph.node_to_cluster[node[0]] for node in graph_list})
    output += "\nTotal matches(#cl,#reg): \n"+ str(total_match)+"\nMatches per iteration\n"
    for i in range(len(iteration_match)):
        output += str(iteration_match[i]) + "\n"
    output+="-"*50+"\n"
    file = open("results.txt","a")
    file.write(output)
    file.close()
    print("Data saved in results.txt")

def match_data(cluster_graph,clusters,regular):
    graph_list = sorted([(node, uses) for node, uses in regular.items()], key=lambda x: x[1], reverse=True)[:20]
    cluster_list = sorted([(node, uses) for node, uses in clusters.items()], key=lambda x: x[1], reverse=True)
    cluster_list = {node[0]: i + 1 for i, node in enumerate(cluster_list)}

    match = dict()
    # positions of regular graph and cluster graph (r,c)
    for i, node in enumerate(graph_list):
        if cluster_graph.node_to_cluster[node[0]] in cluster_list:
            match[node[0]] = (cluster_list[cluster_graph.node_to_cluster[node[0]]], i+1)
        else:
            match[node[0]] = (-1, i+1)
    return match

def simulate_cluster_path(cluster_graph: cg.ClusterGraph, nodes_used, clusters_used):
    orig = cluster_graph.G_orig
    graph = cluster_graph.get_cluster_graph()

    start_node = choice(list(orig.nodes))
    end_node = choice(list(orig.nodes))

    start_node_cluster = cluster_graph.node_to_cluster[start_node]
    end_node_cluster = cluster_graph.node_to_cluster[end_node]

    cpath = nx.dijkstra_path(graph,start_node_cluster,end_node_cluster)

    members = [member for x in cpath for member in cluster_graph.clusters[x]]

    sub = generate_graph_from_members(orig,members)

    full_path = nx.dijkstra_path(sub,start_node,end_node)

    return full_path, cpath

def generate_graph_from_members(graph,members):
    subgraph = nx.Graph()
    for member in members:
        subgraph.add_node(member)
        neighbors = graph.neighbors(member)
        for neighbor in neighbors:
            if neighbor in members:
                subgraph.add_node(neighbor)
                subgraph.add_edge(member,neighbor,weight=1)
    return subgraph

def simulate_cluster_traffic(clustergraph: cg.ClusterGraph,
                             num_of_simulated_paths=10,
                             *, log=False, total_nodes=None, console=""):
    nodes_used = {}
    clusters_used = {}

    if log:
        print("Clusters:", clustergraph.get_cluster_graph().number_of_nodes())
        print("Simulations:", num_of_simulated_paths)

    start_time = time.time()
    for i in range(num_of_simulated_paths):
        print(f"\r{console}Path simulations: {i}/{num_of_simulated_paths}", end=" ")
        path, cpath = simulate_cluster_path(clustergraph, nodes_used, clusters_used)
        for c in cpath:
            if c in clusters_used:
                clusters_used[c] += 1
            else:
                clusters_used[c] = 1
        if total_nodes is not None:
            for node in path:
                total_nodes[node] = total_nodes.get(node, 0) + 1
    end_time = time.time()

    if log:
        print("\nTime:", end_time - start_time,
              "| Avg:", (end_time-start_time)/num_of_simulated_paths)

    return nodes_used, clusters_used

if __name__ == "__main__":

    ########################
    ## Simulation configs

    city_name = "Prijedor"
    number_of_simulations = 1
    num_of_iterations = 1
    plot = True


    #####################
    ## Obtaining graph

    print(f"Obtaining graph of '{city_name}' from file...")
    main_graph = graph_from_file(city_name)
    print("Graph obtained.\n")


    ####################
    ## Running simulations

    print("Graph: ")
    start_time = time.time()
    regular_graph = main_graph.copy()
    end_time = time.time()
    print("Creation time: ", end_time - start_time)

    rg_total_data = dict()
    rg_iteration_data = list()

    start_time = time.time()
    for i in range(number_of_simulations):
        console = f"\rRunning simulations: {i}/{number_of_simulations} | "
        print(console, end="")
        n = simulate_traffic(regular_graph, num_of_iterations, total_nodes=rg_total_data, console=console)
        rg_iteration_data.append(n)
    end_time = time.time()
    print(f"\rSimulation completed (time: {end_time - start_time}) ")
    print(f"Graph nodes: {regular_graph.number_of_nodes()} , Simulated paths: {num_of_iterations}, Number of simulations: {number_of_simulations}")
    print()

    cluster_size = 100
    print("ClusterGraph: ")
    start_time = time.time()
    clustergraph = cg.ClusterGraph(main_graph, cluster_size)
    subs = {cid: clustergraph.get_cluster_graph().subgraph(members).copy() for cid, members in
            clustergraph.clusters.items()}

    end_time = time.time()
    #members = cluster_graph.clusters[cid]
    #sub = orig.subgraph(members).copy()
    print("Creation time: ", end_time - start_time)
    cg_total_data = dict()
    cg_iteration_data = list()
    cl=dict()

    start_time = time.time()
    for i in range(number_of_simulations):
        console = f"\rRunning simulations: {i}/{number_of_simulations} | "
        print(console, end="")
        n, c = simulate_cluster_traffic(clustergraph, num_of_iterations, total_nodes=cg_total_data, console=console)
        for cluster in c:
            cl[cluster] = cl.get(cluster, 0) + 1
        cg_iteration_data.append(c)
    end_time = time.time()
    print(f"\rSimulation completed (time: {end_time - start_time}) ")
    print(f"Graph nodes: {clustergraph.get_cluster_graph().number_of_nodes()} , Simulated paths: {num_of_iterations}, Number of simulations: {number_of_simulations}")
    print()



    #####################
    ## Interpreting data

    data = {"city:":city_name,"simulations":number_of_simulations,"iterations":num_of_iterations,"cluster size":cluster_size}
    interpret_graph_data(data,rg_total_data,rg_iteration_data,clustergraph,cl,cg_iteration_data,cg_total_data)

    ###################
    ## Plotting graphs

    if plot:
        ox.plot_graph(main_graph,bgcolor="white",node_color="skyblue",node_size=100)
        plot_graph(clustergraph.get_cluster_graph(), showLabels=False, font_size=8)

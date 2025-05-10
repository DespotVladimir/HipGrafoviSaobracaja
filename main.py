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
        print(f"\r{console}Path simulations: {i + 1}/{num_of_simulated_paths}", end=" ")
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
    iteration_match = [match_data(cluster_graph,cg_per_iteration[i],nodes_used_per_iteration[i]) for i in range(len(cg_per_iteration))]

    graph_list = sorted([(node, uses) for node, uses in total_nodes.items()], key=lambda x: x[1], reverse=True)[:20]
    cluster_list = sorted([(node, uses) for node, uses in cg_nodes.items()], key=lambda x: x[1], reverse=True)[:20]

    output = str(data)+"\nTop 20 clusters[lat,long]: \nname,lat,long\n"
    counter = 1
    for cluster,_ in cluster_list:
        x,y = cluster_graph.get_cluster_coordinate(cluster)
        output += f"{cluster}(#{counter}),{y},{x}\n"
        counter += 1

    output+="\nTop 20 nodes in regular graph: \nname,lat,long\n"
    counter = 1
    for node,_ in graph_list:
        x,y = cluster_graph.get_node_coordinates(node)
        output += f"{node}(#{counter}),{y},{x}\n"
        counter += 1

    output += "\nTop 20 nodes in cluster graph: \nname,lat,long\n"
    counter = 1
    c_total_nodes = sorted([(node, uses) for node, uses in c_total_nodes.items()], key=lambda x: x[1], reverse=True)[:20]
    for node, _ in c_total_nodes:
        x, y = cluster_graph.get_node_coordinates(node)
        output += f"{node}(#{counter}),{y},{x}\n"
        counter += 1


    output += str({node[0]: clustergraph.node_to_cluster[node[0]] for node in graph_list})
    output += "\nTotal matches: \n"+ str(total_match)+"\nMatches per iteration\n"
    for i in iteration_match:
        output += str(i) + "\n"
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

def simulate_cluster_path(cluster_graph:cg.ClusterGraph,nodes_used,clusters_used):
    """
    Simulate a single path through the cluster graph, fully unpacked within connected clusters.
    Returns start_node, end_node, and the full node-level path.
    """
    # work on undirected original graph
    orig = cluster_graph.G_orig.to_undirected()

    # 1) choose random start and end
    start = choice(list(orig.nodes()))
    end   = choice(list(orig.nodes()))

    # 2) compute shortest path on cluster-level graph
    cpath = nx.dijkstra_path(
        cluster_graph.get_cluster_graph(),
        cluster_graph.node_to_cluster[start],
        cluster_graph.node_to_cluster[end],
        weight='weight'
    )
    for node in cpath:
        if node in clusters_used:
            clusters_used[node]+=1
        else:
            clusters_used[node]=1

    full_path = [start]
    # 3) unpack each cluster hop
    for i, cid in enumerate(cpath):
        members = cluster_graph.clusters[cid]
        sub = orig.subgraph(members).copy()
        prev_c = cpath[i-1] if i > 0 else None
        next_c = cpath[i+1] if i < len(cpath)-1 else None
        # add boundary edges
        if prev_c is not None:
            for u, v in cluster_graph.hyperedges[frozenset((prev_c, cid))]:
                if not sub.has_edge(u, v):
                    # extract a single edge attr dict from a MultiGraph if needed
                    data = cluster_graph.G_orig.get_edge_data(u, v)
                    if isinstance(data, dict) and any(isinstance(k, (int, str)) for k in data):
                        # Multi-edge: pick the first edge's attributes
                        attrs = next(iter(data.values()))
                    else:
                        attrs = data or {}
                    sub.add_edge(u, v, **attrs)
        if next_c is not None:
            for u, v in cluster_graph.hyperedges[frozenset((cid, next_c))]:
                if not sub.has_edge(u, v):
                    data = cluster_graph.G_orig.get_edge_data(u, v)
                    if isinstance(data, dict) and any(isinstance(k, (int, str)) for k in data):
                        attrs = next(iter(data.values()))
                    else:
                        attrs = data or {}
                    sub.add_edge(u, v, **attrs)
        # determine entry and exit
        if prev_c is None:
            entry = start
        else:
            entry = v if cluster_graph.node_to_cluster[v] == cid else u
        if next_c is None:
            exit = end
        else:
            exit = u if cluster_graph.node_to_cluster[u] == cid else v
        # 4) shortest path within cluster subgraph
        subpath = nx.dijkstra_path(sub, entry, exit, weight="weight")
        # merge without duplicating
        if full_path[-1] == subpath[0]:
            full_path.extend(subpath[1:])
        else:
            full_path.extend(subpath)
    # 5) update visit counts
    for node in full_path:
        nodes_used[node] = nodes_used.get(node, 0) + 1


    return full_path,cpath

def simulate_cluster_traffic(clustergraph: cg.ClusterGraph ,num_of_simulated_paths = 10,*,log=False,total_nodes=None,console=""):
    nodes_used = dict()
    cpatha = dict()
    if log:
        print("Number of nodes: ", len(clustergraph.nodes))
        print("Number of simulations: ", num_of_simulated_paths)

    start_time = time.time()

    for i in range(num_of_simulated_paths):
        print(f"\r{console}Path simulations: {i + 1}/{num_of_simulated_paths}", end=" ")
        try:
            path,cpath = simulate_cluster_path(clustergraph, nodes_used, cpatha)
            if total_nodes is not None:
                for node in path:
                    if node in total_nodes:
                        total_nodes[node] += 1
                    else:
                        total_nodes[node] = 1
        except:
            pass

    end_time = time.time()
    if log:
        print("Simulation time: ", end_time - start_time)
        print("Average time per simulation: ", (end_time - start_time) / num_of_simulated_paths)

        print("Most used nodes: ")
        copy = nodes_used.copy()
        for _ in range(min(10, len(copy) // 10)):
            key, value = max(list(copy.items()), key=lambda x: x[1])
            print("" + str(key) + ": " + str(value), end="; ")
            copy.pop(key)
        print()

    return nodes_used,cpatha

if __name__ == "__main__":

    ########################
    ## Simulation configs

    city_name = "Belgrade"
    number_of_simulations = 1
    num_of_iterations = 100
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
        console = f"\rRunning simulations: {i + 1}/{number_of_simulations} | "
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
    end_time = time.time()
    print("Creation time: ", end_time - start_time)
    cg_total_data = dict()
    cg_iteration_data = list()
    cl=dict()

    start_time = time.time()
    for i in range(number_of_simulations):
        console = f"\rRunning simulations: {i + 1}/{number_of_simulations} | "
        print(console, end="")
        n, c = simulate_cluster_traffic(clustergraph, num_of_iterations, total_nodes=cg_total_data)
        for cluster in c:
            cl[cluster] = cl.get(cluster, 0) + 1
        cg_iteration_data.append(n)
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







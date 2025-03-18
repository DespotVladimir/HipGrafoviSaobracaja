import osmnx as ox

def get_city_graph(city_name: str):

    graph = ox.graph_from_place(city_name, network_type="all")
    print(city_name + " Graph obtained ("+str(len(graph))+" nodes)")
    edges = dict()
    for node1,node2,_ in graph.edges:
        node1 = int(node1)
        node2 = int(node2)
        if node1 not in edges:
            edges[node1] = list()
        edges[node1].append(node2)


    files = open("Cities/"+city_name.split(",")[0].replace(" ","") + ".txt", "w")
    files.write(edges.__str__())

def graph_from_file(city_name: str):
    try:
        files = open("Cities/"+city_name.replace(" ","")+".txt", "r")
        lines = files.readlines()
        return eval(lines[0])
    except FileNotFoundError:
        raise FileNotFoundError(city_name+" not found")
    except:
        raise RuntimeError("Error getting "+city_name)

if __name__ == "__main__":
    city = input("Enter city name, country (ex. Sarajevo, Bosnia): ")
    get_city_graph(city)
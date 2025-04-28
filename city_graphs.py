import osmnx as ox

def get_city_graph(city_name: str, network_type: str = "all"):
    ox.io.settings.log_console = True

    graph = ox.graph_from_place(city_name, network_type=network_type)
    print(city_name + " Graph obtained ("+str(len(graph))+" nodes)")
    ox.io.save_graphml(graph, "Cities/" + city_name.split(",")[0].replace(" ","").capitalize() + ".graphml")

    return graph

def graph_from_file(city_name: str):
    try:
        graph = ox.load_graphml("Cities/" + city_name.replace(" ","").capitalize() + ".graphml")
        return graph
    except FileNotFoundError:
        raise FileNotFoundError("Error getting file: "+city_name)
    except:
        raise RuntimeError("Error getting "+city_name)

if __name__ == "__main__":
    city = input("Enter city name, country (ex. Sarajevo, Bosnia): ")
    get_city_graph(city,"all")
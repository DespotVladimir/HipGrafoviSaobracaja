import osmnx as ox

def get_city_graph(city_name: str, network_type: str = "all", console_reading = False):
    """
        Download and save a street network graph for a given city from OpenStreetMap.

        Parameters
        ----------
        city_name : str
            The name of the city, optionally with country (e.g., "Sarajevo, Bosnia").
        network_type : str, optional
            Type of street network to retrieve ("all", "drive", "walk", etc.), by default "all".
        console_reading : bool, optional
            Whether to read the log to the console, by default False.

        Returns
        -------
        networkx.MultiDiGraph
            The street network graph as a NetworkX graph object.

        Side Effects
        ------------
        - Saves the graph to a GraphML file in the "Cities" directory.
          File name is derived from city_name (spaces removed and first part capitalized).

        Raises
        ------
        OSMnxError
            If the city data cannot be retrieved from OpenStreetMap.

    """

    ox.io.settings.log_console = console_reading
    graph = ox.graph_from_place(city_name, network_type=network_type)
    ox.io.save_graphml(graph, "Cities/" + city_name.split(",")[0].replace(" ","").capitalize() + ".graphml")

    return graph

def graph_from_file(city_name: str):
    """
        Load a previously saved GraphML file for the given city.

        Parameters
        ----------
        city_name : str
            The base name of the city file (matching the saved GraphML file).

        Returns
        -------
        networkx.MultiDiGraph
            The loaded street network graph.

        Raises
        ------
        FileNotFoundError
            If the GraphML file does not exist for the specified city.
        RuntimeError
            For any other error encountered while loading the file.
    """

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
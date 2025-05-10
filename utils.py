import osmnx as ox
import networkx as nx
from matplotlib import pyplot as plt


def plot_graph(G_original,*, node_color='skyblue', bgcolor='white', node_size=110,showLabels=True,font_size=10, **plot_kwargs):
    """
    Convert a NetworkX Graph into a MultiDiGraph with x, y attributes and CRS,
    then plot using OSMnx.

    Automatically extracts coordinates from node attributes: supports direct 'x','y', nested 'attr', or 'centroid'.

    Parameters
    ----------
    G_original : networkx.Graph or networkx.DiGraph or networkx.MultiGraph
        The input graph whose nodes must have 'x' and 'y' attributes, or 'centroid', or nested in 'attr'.
    node_color : str or list
        Node color passed to ox.plot_graph.
    bgcolor : str
        Background color for the plot.
    node_size : int or list
        Node size passed to ox.plot_graph.
    show : bool
        Whether to show the plot or not.
    **plot_kwargs
        Additional keyword arguments forwarded to ox.plot_graph.

    """
    # Create a MultiDiGraph to support keys and directed edges
    C = nx.MultiDiGraph()

    # Copy nodes with attributes, extracting x/y
    for node, data in G_original.nodes(data=True):
        # Attempt to find coordinates
        x = data.get('x')
        y = data.get('y')
        if x is None or y is None:
            # check for centroid
            centroid = data.get('centroid') or data.get('attr', {}).get('centroid')
            if centroid and len(centroid) >= 2:
                x, y = centroid[0], centroid[1]
            else:
                # check nested attr x/y
                nested = data.get('attr', {})
                x = nested.get('x')
                y = nested.get('y')
        if x is None or y is None:
            raise KeyError(f"Node {node} missing 'x' or 'y' attribute needed for plotting.")
        # Prepare attributes copy, inject correct x,y
        attrs = data.copy()
        attrs['x'] = x
        attrs['y'] = y
        C.add_node(node, **attrs)

    # Copy edges with all attributes
    if not getattr(G_original, 'is_multigraph', lambda: False)():
        for u, v, data in G_original.edges(data=True):
            C.add_edge(u, v, **data)
    else:
        for u, v, key, data in G_original.edges(keys=True, data=True):
            C.add_edge(u, v, key, **data)

    # Set CRS for geographic plotting
    C.graph['crs'] = 'EPSG:4326'

    if showLabels:
        _,ax = ox.plot_graph(
        C,
        node_color=node_color,
        bgcolor=bgcolor,
        node_size=node_size,
        show=False,
        **plot_kwargs
        )
        print_labels_on_graph(C,ax,font_size=font_size)
    else:
        ox.plot_graph(
            C,
            node_color=node_color,
            bgcolor=bgcolor,
            node_size=node_size,
            show=True,
            **plot_kwargs
        )



def print_labels_on_graph(G,ax,*,font_size=10):
    pos=dict()
    for node, data in G.nodes(data=True):
        pos[node] = (G.nodes[node]["attr"]['x'], G.nodes[node]["attr"]['y'])

    nx.draw_networkx_labels(G, pos,
                            labels={n: n for n in G.nodes()},
                            font_size=font_size,
                            ax=ax)
    plt.show()


def get_city_graph(city_name: str,*, network_type: str = "all", console_reading = False):
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
    graph = ox.graph_from_place(city_name, network_type=network_type,simplify=False)
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
    get_city_graph(city,network_type="drive",console_reading=True)
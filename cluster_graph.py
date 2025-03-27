from sys import maxsize

class ClusterGraph:
    def __init__(self, neighbouring_list: dict[int,list[int]],max_cluster_size=10) -> None:
        self.neighbouring_list = dict(neighbouring_list)
        self.cluster_list = dict()
        self.edges = dict()

        self.cluster_list = self.local_clustering(self.neighbouring_list, max_cluster_size=max_cluster_size)
        self.neighbouring_list = self.create_hypergraph(self.cluster_list, self.neighbouring_list)

        self.nodes = list(self.neighbouring_list.keys())


    def local_clustering(self,graph, max_cluster_size=10):
        visited = set()
        clusters = {}
        cluster_id = 0

        for node in graph:
            if node not in visited:
                cluster = {node}
                visited.add(node)

                for neighbor in graph[node]:
                    if neighbor not in visited and len(cluster) < max_cluster_size:
                        cluster.add(neighbor)
                        visited.add(neighbor)

                clusters[cluster_id] = list(cluster)
                cluster_id += 1

        return clusters



    def create_hypergraph(self,clusters, original_graph : dict[int,list[int]]):
        hypergraph = {}
        cluster_map = {node: cluster for cluster, nodes in clusters.items() for node in nodes}

        for cluster_id, nodes in clusters.items():
            hypergraph[cluster_id] = set()
            for node in nodes:
                for neighbor in original_graph.get(node, []):
                    neighbor_cluster = cluster_map.get(neighbor)
                    if neighbor_cluster is not None and neighbor_cluster != cluster_id:
                        hypergraph[cluster_id].add(neighbor_cluster)
                        self.edges[(node, cluster_id)] = 1
                        self.edges[(cluster_id, node)] = 1

        return {k: list(v) for k, v in hypergraph.items()}



    def shortest_path(self, start: int, end: int) -> list[int] | None:
        if start not in self.neighbouring_list or end not in self.neighbouring_list:
            return None

        dijkstra_paths = self.dijkstra(start)

        path = list()

        current = end

        while current != start:
            path.append(current)
            current = dijkstra_paths[current][0]

        path.append(start)
        path.reverse()
        return path


    def dijkstra(self, start: int|None = None) -> dict[int, tuple[int|None,int]] | None:
        if start is None:
            start = list(self.neighbouring_list.keys())[0]
        if start not in self.neighbouring_list.keys():
            return None

        visited = set()
        dist: dict[int, tuple[int | None, int]] = {key: (None,maxsize) for key in self.neighbouring_list.keys()}
        dist[start] = (None,0)

        for _ in range(len(self.neighbouring_list.keys())):

            x = self.dijkstra_min_distance(dist, visited)

            if x is None:
                return dist

            visited.add(x)

            for neighbour in self.neighbouring_list[x]:
                if neighbour not in self.neighbouring_list.keys():
                    continue
                if (x,neighbour) not in self.edges:
                    weight = 1
                else:
                    weight = self.edges[(x,neighbour)]
                if neighbour not in visited and (dist[neighbour])[1] > dist[x][1] + weight:
                    dist[neighbour] = (x,dist[x][1] + weight)

        return dist


    def dijkstra_min_distance(self,dist : dict[int,tuple[int | None, int]], visited : set[int]) -> int:
        minis = maxsize

        min_index = None

        for u in self.neighbouring_list:

            if dist[u][1] < minis and u not in visited:
                minis = dist[u][1]
                min_index = u

        return min_index

if __name__ == "__main__":

    from city_graphs import *
    from random import choice

    graph_data = graph_from_file("Banja Luka")
    hyper_graph = ClusterGraph(graph_data)

    start_node = choice(list(hyper_graph.neighbouring_list.keys()))
    end_node = choice(list(hyper_graph.neighbouring_list.keys()))
    print(start_node, end_node, hyper_graph.shortest_path(start_node, end_node))



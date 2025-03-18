from sys import maxsize

class Graph:
    def __init__(self, neighbouring_list: dict[int,list[int]]) -> None:
        self.nodes = set(neighbouring_list.keys())
        self.neighbouring_list = neighbouring_list
        self.edges = dict()

        for edge,neighbours in self.neighbouring_list.items():
            for neighbour in neighbours:
                self.edges[(edge,neighbour)] = 1

    def shortest_path(self, start: int, end: int) -> list[int] | None:
        if start not in self.nodes or end not in self.nodes:
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
            start = list(self.nodes)[0]
        if start not in self.nodes:
            return None

        visited = set()
        dist: dict[int, tuple[int | None, int]] = {key: (None,maxsize) for key in self.nodes}
        dist[start] = (None,0)

        for _ in range(len(self.nodes)):

            x = self.dijkstra_min_distance(dist, visited)

            if x is None:
                return dist

            visited.add(x)

            for neighbour in self.neighbouring_list[x]:
                if neighbour not in visited and (dist[neighbour])[1] > dist[x][1] + self.edges[(x,neighbour)]:
                    dist[neighbour] = (x,dist[x][1] + self.edges[(x,neighbour)])

        return dist


    def dijkstra_min_distance(self,dist : dict[int,tuple[int | None, int]], visited : set[int]) -> int:
        minis = maxsize

        min_index = None

        for u in self.nodes:

            if dist[u][1] < minis and u not in visited:
                minis = dist[u][1]
                min_index = u

        return min_index


    def __str__(self):
        return str(self.neighbouring_list)


if __name__ == "__main__":

    import city_graphs as cg
    from random import choice

    graph = Graph(cg.graph_from_file("Banja Luka"))

    start_node = choice(list(graph.nodes))
    end_node = choice(list(graph.nodes))
    print(start_node,end_node,graph.shortest_path(start_node, end_node))

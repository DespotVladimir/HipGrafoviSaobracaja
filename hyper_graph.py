from sys import maxsize

class HyperGraph:
    def __init__(self, neighbouring_list: dict[int, list[int]]) -> None:
        self.nodes = set()
        self.neighbouring_list = dict()
        self.edges = dict()
        self.hyper_edges = dict()


        for node, neighbours in neighbouring_list.items():
            self.nodes.add(node)
            self.neighbouring_list[node] = []
            for neighbour in neighbours:
                self.edges[(node, neighbour)] = 1
                self.edges[(neighbour, node)] = 1
                self.neighbouring_list[node].append(neighbour)

        self.nodes = list(self.nodes)

        self.init_helper()


    def init_helper(self):
        main_queue = list(self.nodes)
        while len(main_queue) > 0:

            # first one in the "queue" is the main node
            node = main_queue[0]
            # "queue" for checking neighbours of main node and deleting them
            neighbour_queue = list(self.neighbouring_list[node])

            # merge neighbours if there are more than 4 on one
            if len(neighbour_queue) >= 4:
                #print("Chosen node: ", node)
                while len(neighbour_queue) > 0:

                    neighbour = neighbour_queue[0]
                    #print("Chosen neighbour: ", neighbour)

                    # remove main node before checking second neighbours
                    if neighbour not in self.neighbouring_list:
                        neighbour_queue.pop(0)
                        continue
                    if neighbour in self.neighbouring_list and node in self.neighbouring_list[neighbour]:
                        self.neighbouring_list[neighbour].remove(node)


                    # make a queue for second neighbours
                    second_neighbour_queue = list(self.neighbouring_list[neighbour])

                    # check if there is only one node connecting it
                    if len(second_neighbour_queue) == 1:
                        # if that one node has 2 edges consider it a neighbour and add it to the neighbour queue
                        if second_neighbour_queue[0] in self.neighbouring_list:
                            if len(self.neighbouring_list[second_neighbour_queue[0]]) == 2:
                                neighbour_queue.append(second_neighbour_queue[0])


                    # remove first neighbour from those second neighbours and add main node
                    while len(second_neighbour_queue) > 0:
                        # remove first neighbour

                        second_neighbour = second_neighbour_queue[0]
                        # print(" Chosen second neighbour: ", second_neighbour)


                        if (neighbour, second_neighbour) in self.edges:
                            self.edges.pop((neighbour, second_neighbour))
                        if (second_neighbour, neighbour) in self.edges:
                            self.edges.pop((second_neighbour, neighbour))

                        if second_neighbour in self.neighbouring_list and neighbour in self.neighbouring_list[second_neighbour]:
                            self.neighbouring_list[second_neighbour].remove(neighbour)

                        # add main node
                        self.edges[(node, second_neighbour)] = 1
                        self.edges[(second_neighbour, node)] = 1
                        self.neighbouring_list.setdefault(node, []).append(second_neighbour)
                        self.neighbouring_list.setdefault(second_neighbour, list()).append(node)



                        second_neighbour_queue.pop(0)


                    # remove neighbour node itself and the connection to the main node
                    if (neighbour, node) in self.edges:
                        self.edges.pop((neighbour, node))
                    if (node, neighbour) in self.edges:
                        self.edges.pop((node, neighbour))
                    if neighbour in self.neighbouring_list:
                        self.neighbouring_list.pop(neighbour)
                    if neighbour in self.nodes:
                        self.nodes.remove(neighbour)
                    self.hyper_edges.setdefault(node, []).append(neighbour)
                    if neighbour in main_queue:
                        main_queue.remove(neighbour)
                    neighbour_queue.pop(0)

            # remove node if they are on the same road and connect neighbours
            elif len(neighbour_queue) == 2:

                neighbour_back = neighbour_queue[0]
                neighbour_front = neighbour_queue[1]

                # connect neighbours in neighbouring list and edges
                prevent = False
                if neighbour_back not in self.neighbouring_list:
                    prevent = True
                    self.neighbouring_list[node].remove(neighbour_back)
                if neighbour_front not in self.neighbouring_list:
                    prevent = True
                    self.neighbouring_list[node].remove(neighbour_front)

                if prevent:
                    main_queue.pop(0)
                    continue
                if neighbour_front not in self.neighbouring_list[neighbour_back]:
                    self.neighbouring_list[neighbour_back].append(neighbour_front)
                if neighbour_back not in self.neighbouring_list[neighbour_front]:
                    self.neighbouring_list[neighbour_front].append(neighbour_back)

                self.edges[(neighbour_back, neighbour_front)] = 1
                self.edges[(neighbour_front, neighbour_back)] = 1

                # remove from neighbouring list and from neighbouring list of the neighbour
                if node in self.neighbouring_list:
                    self.neighbouring_list.pop(node)
                if neighbour_front in self.neighbouring_list and node in self.neighbouring_list[neighbour_front]:
                    self.neighbouring_list[neighbour_front].remove(node)
                if neighbour_back in self.neighbouring_list and node in self.neighbouring_list[neighbour_back]:
                    self.neighbouring_list[neighbour_back].remove(node)

                # remove node from all nodes
                if node in self.nodes:
                    self.nodes.remove(node)

                # remove edges
                if (node, neighbour_front) in self.edges:
                    self.edges.pop((node, neighbour_front))
                if (neighbour_front, node) in self.edges:
                    self.edges.pop((neighbour_front, node))
                if (node, neighbour_back) in self.edges:
                    self.edges.pop((node, neighbour_back))
                if (neighbour_back, node) in self.edges:
                    self.edges.pop((neighbour_back, node))


            # remove node if it's a dead end
            elif len(neighbour_queue) == 1:

                dead_end_neighbour = neighbour_queue[0]
                
                # remove from neighbouring list and from neighbouring list of the neighbour
                if node in self.neighbouring_list:
                    self.neighbouring_list.pop(node)
                if dead_end_neighbour in self.neighbouring_list and node in self.neighbouring_list[dead_end_neighbour]:
                    self.neighbouring_list[dead_end_neighbour].remove(node)

                # remove from all nodes
                if node in self.nodes:
                    self.nodes.remove(node)
                
                # remove edges
                if (node, dead_end_neighbour) in self.edges:
                    self.edges.pop((node, dead_end_neighbour))
                if (dead_end_neighbour, node) in self.edges:
                    self.edges.pop((dead_end_neighbour, node))



            main_queue.pop(0)




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

        for u in self.nodes:

            if dist[u][1] < minis and u not in visited:
                minis = dist[u][1]
                min_index = u

        return min_index




if __name__ == "__main__":

    import city_graphs as cg
    from random import choice
    import graph

    g = graph.Graph(cg.graph_from_file("Banja Luka"))
    print("Number of nodes before: ",len(g.nodes))
    g = HyperGraph(cg.graph_from_file("Banja Luka"))
    print("Number of nodes after: ",len(g.nodes))
    print(g.hyper_edges)
    start_node = choice(list(g.nodes))
    end_node = choice(list(g.nodes))
    print(start_node,end_node,g.shortest_path(start_node, end_node))
# Prim's Algorithm for Minimum Spanning Tree (Greedy Algorithm)

# Minimum spanning tree: a minimum weighted spanning tree for a weighted, connected, undirected graph 
# NOTE: main difference with kruskal is that prim works on
# DISCONNECT graphs

"""Method
1. Determine an arbitray vertex as the starting vertex of MST
    - Basically we have two subsets of vertices: MST's included vertices and fringe vertices
    - They can be considered disjoint subsets of the tree
2. Find edges connecting the tree vertices with the fringe vertices
    - Find the minimum weight among these edges
    - The minimum weight edge cannot form a cycle
    - Add the edge and corresponding ending vertex to the MST
3. Repeat 2 until all fringe vertices are added
4. Return MST
"""

"""Cut(Graph theory)
- Group of edges that connect two sets of vertices in a graph
"""
import numpy as np # using numpy arrays for faster memory
import sys

class Graph: # undirected, weighted graph ds

    def __init__(self, num_vertices) -> None:
        self.v = num_vertices
        # We will try with adjacency matrix representation
        self.graph = np.zeros((num_vertices, num_vertices), dtype=int)
        
    def add_edge(self, u, v, w) -> None:
        self.graph[u, v] = w
        self.graph[v, u] = w

    def print_graph(self) -> None:
        print(self.graph)
    
    # Prim's algorithm utility function to find the minimum weight of the cuts
    def min_weight(self, key, mstset):
        # init min value
        min = sys.maxsize
        for v in range(self.v):
            if key[v]  < min and mstset[v] == False:
                min = key[v]
                min_index = v
        return min_index

    # Function to construct and print MST for a graph
    def Prim_MST(self, u: int = 0): 
        # key values used to pick minimum weight edge in cut
        key = [sys.maxsize] * self.v # use it as a placeholder for infinity notation in the algorithm

        # array to store constructed MST
        parent = [None] * self.v 
        
        # set key as the starting vertex
        key[0] = u # we have it default as 0
        mst = [False] * self.v

        parent[0] = -1 # the first node is the root, so no parent here

        for _ in range (self.v):
            # pick the minimum distance vertex from the set of vertices not in the MST yet (Cut)
            u = self.min_weight(key, mst)

            # put that min dist. vertex in the shortest path tree
            mst[u] = True

            # update distance value of the adjacent vertices from the picked one if current dist. is greater than new dist
            # refresh the remaining vertices to be handled
            for v in range(self.v):
                # graph [u][v] is non zero for adjacent vertices with the current MST
                # mst[v] is false for vertices that are not yet included in the mst 
                # update the key only if graph[u][v] is smaller than key[v]
                if self.graph[u, v] > 0 and mst[v] == False and key[v] > self.graph[u, v]:
                    key[v] = self.graph[u, v]
                    parent[v] = u
        self.print_mst(parent)

    def print_mst(self, parent):
        print("Edge \tWeight")
        for i in range(1, self.v):
            print(parent[i], "-", i, "\t", self.graph[i, parent[i]])


if __name__ == '__main__':
    g = Graph(5)
    g.add_edge(0, 2, 4)
    g.add_edge(1, 4, 8)
    g.add_edge(1, 3, 9)
    g.add_edge(2, 3, 7)
    # g.print_graph()
    print(sys.maxsize)
    g.Prim_MST() # TODO: double-check the algorithm
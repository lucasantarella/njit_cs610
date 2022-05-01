import networkx as nx
import matplotlib.pyplot as plt


class Graph:
    def __init__(self, vertices: list, N: int, zero_indexed: bool = True):
        self.vertices = vertices
        self.N = N
        self.G = from_vertices(vertices, self.N, zero_indexed)

    def transitive_closure(self) -> list:
        Gi = [i[:] for i in self.G]  # clone initial boolean matrix
        for N in range(self.N):
            for a in range(self.N):
                for b in range(self.N):
                    Gi[a][b] = Gi[a][b] or (Gi[a][N] and Gi[N][b])
        return Gi


def from_vertices(vertices: list, N: int, zero_indexed: bool = False) -> list:
    G = [[False] * N for i in range(N)]

    # go through each pair and set the initial boolean matrix
    for i in range(len(vertices)):
        src = vertices[i][0] - int(not zero_indexed)  # compensate for non-zero-indexed
        dst = vertices[i][1] - int(not zero_indexed)
        G[src][dst] = True

    return G


def to_vertices(boolean_matrix: list, zero_indexed: bool = False) -> list:
    vertices = []

    for i in range(len(boolean_matrix)):
        for j in range(len(boolean_matrix[i])):
            if i != j and boolean_matrix[i][j]:
                vertices.append([i + int(not zero_indexed), j + int(not zero_indexed)])

    return vertices


g = Graph([
    [1, 2],
    [2, 3],
    [3, 1],
    [4, 5],
    [5, 6],
    [6, 4],
], 6, zero_indexed=False)
T = g.transitive_closure()

print(to_vertices(T))

G = nx.DiGraph()
G.add_edges_from(to_vertices(T))
nx.draw(G, with_labels=True)
plt.show()


def draw_graph(vertices: list) -> None:
    G = nx.DiGraph()
    G.add_edges_from(vertices)
    nx.draw(G, with_labels=True)
    plt.show()


g3 = Graph([
    [1, 2],
    [2, 3],
    [3, 4],
    [4, 5],
    [5, 6],
    [6, 7],
    [7, 8]
], 8, zero_indexed=False)
draw_graph(g3.vertices)

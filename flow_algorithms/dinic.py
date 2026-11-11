"""Dinic's Algorithm for finding maximum flow in a directed graph.

Description:
    Given a flow network G = (V, E), a source s, and a sink t, Dinic's
    algorithm finds the greatest amount of flow that can travel from s
    to t without exceeding the capacity of any edge. At every vertex
    except the source and sink, incoming flow must equal outgoing flow.

    The algorithm uses a residual graph to track remaining capacity.
    Each edge also has a reverse residual edge, allowing previously
    assigned flow to be adjusted when another route is discovered.

Algorithm:
    1. Build the residual graph from the input network.
    2. Run BFS to give each reachable vertex a level, forming a level
       graph using edges that still have available capacity.
    3. Run DFS along edges leading to the next level to send flow.
    4. Continue DFS until the level graph has a blocking flow, meaning
       no more source-to-sink flow can be sent using those level edges.
    5. Repeat BFS and DFS until the sink can no longer be reached.
       The total amount of flow sent is the maximum flow.

Implementation:
    The graph is stored as adjacency lists. Each residual edge stores
    [destination, remaining capacity, reverse-edge index]. Reverse-edge
    indices allow residual capacities to be updated efficiently.

    Current-edge pointers stop DFS from repeatedly checking edges that
    have already been ruled out in the current BFS phase. DFS uses an
    explicit stack to avoid Python's recursion-depth limit.

Input and output:
    The public max_flow(G, s, t) function accepts a dictionary whose
    keys are vertices 0 through n-1. Each value is a list of outgoing
    (destination, capacity) pairs. Capacities must be finite and
    nonnegative. The function returns the maximum flow value without
    changing the input graph.

Complexity:
    Time: O(V^2 * E) for general directed networks, where V is the
          number of vertices and E is the number of edges. Each
          blocking-flow phase takes O(V * E) time and there are at
          most O(V) phases.
    Space: O(V + E) for residual adjacency lists, reverse edges,
           BFS levels, current-edge pointers, and the DFS stack.

References:
    Y. Dinitz (2006). Dinitz' Algorithm: The Original Version and
    Even's Version. In Theoretical Computer Science (Springer).
    S. Even and R. E. Tarjan (1975). Network Flow and Testing Graph
    Connectivity. SIAM Journal on Computing, 4(4), 507-518.

AI use:
    ChatGPT assisted with documentation, and code checks.
    See the team's README AI Use section for disclosure.
"""

from collections import deque
from numbers import Real


class Dinic:
    """Store a residual network and calculate maximum flow using Dinic."""

    # Validate graph size and initialize storage.
    def __init__(self, n):
        if type(n) is not int or n <= 0:
            raise ValueError("Number of vertices must be a positive integer")

        self.n = n
        # Each residual edge is [destination, capacity, reverse-edge index].
        self.graph = [[] for _ in range(n)]

    # Validate inputs and link reverse residual edges.
    def add_edge(self, u, v, capacity):
        """Add a directed edge and a reverse edge with zero capacity."""
        if (type(u) is not int or type(v) is not int
                or not (0 <= u < self.n and 0 <= v < self.n)):
            raise ValueError("Edge endpoints must be valid vertex indices")
        if (isinstance(capacity, bool) or not isinstance(capacity, Real)
                or not (0 <= capacity < float("inf"))):
            raise ValueError("Capacity must be a finite nonnegative number")

        # Self-loops and zero-capacity edges do not affect maximum flow.
        if u == v or capacity == 0:
            return

        # Save each edge's reverse index for constant-time flow updates.
        forward = [v, capacity, len(self.graph[v])]
        reverse = [u, 0, len(self.graph[u])]
        self.graph[u].append(forward)
        self.graph[v].append(reverse)

    # Build levels using only positive-capacity edges.
    def bfs(self, s, t):
        """Return whether the sink is reachable in the residual graph."""
        self.level = [-1] * self.n
        self.level[s] = 0
        queue = deque([s])

        while queue:
            u = queue.popleft()
            for v, capacity, _ in self.graph[u]:
                # Only visit a vertex once per BFS phase.
                if capacity > 0 and self.level[v] == -1:
                    self.level[v] = self.level[u] + 1
                    queue.append(v)

        return self.level[t] != -1

    # Use an iterative DFS for long paths.
    def dfs(self, s, t):
        """Push one flow amount through the current BFS level graph."""
        nodes = [s]
        path = []  # (vertex, edge index) for the current source-to-node path
        bottleneck = [float("inf")]

        while nodes:
            u = nodes[-1]

            if u == t:
                pushed = bottleneck[-1]

                # Remove flow from forward capacities and add it to reverse edges.
                for node, edge_index in path:
                    edge = self.graph[node][edge_index]
                    edge[1] -= pushed
                    self.graph[edge[0]][edge[2]][1] += pushed

                return pushed

            # If all edges at this node are exhausted, backtrack to its parent.
            if self.ptr[u] == len(self.graph[u]):
                nodes.pop()
                bottleneck.pop()
                if path:
                    parent, _ = path.pop()
                    self.ptr[parent] += 1
                continue

            edge_index = self.ptr[u]
            v, capacity, _ = self.graph[u][edge_index]

            # Valid level edges must go exactly one BFS level forward.
            if capacity > 0 and self.level[v] == self.level[u] + 1:
                path.append((u, edge_index))
                nodes.append(v)
                bottleneck.append(min(bottleneck[-1], capacity))
            else:
                self.ptr[u] += 1

        return 0  # No further path through the current level graph.

    # Add input validation and run blocking-flow phases.
    def max_flow(self, s, t):
        """Return maximum flow from s to t in the stored residual network."""
        if (type(s) is not int or type(t) is not int
                or not (0 <= s < self.n and 0 <= t < self.n)):
            raise ValueError("Source and sink must be valid vertex indices")
        if s == t:
            raise ValueError("Source and sink must be different vertices")

        total_flow = 0

        # Each BFS phase builds a new level graph.
        while self.bfs(s, t):
            self.ptr = [0] * self.n

            # Send a blocking flow using the current levels.
            while True:
                pushed = self.dfs(s, t)
                if pushed == 0:
                    break
                total_flow += pushed

        return total_flow


# Convert the team's adjacency-list input to a solver.
def build_dinic(G):
    """Build a fresh Dinic instance without modifying the input graph."""
    if not isinstance(G, dict) or not G or set(G) != set(range(len(G))):
        raise ValueError("Graph must contain vertices numbered 0 through n-1")

    solver = Dinic(len(G))
    for u, neighbors in G.items():
        for v, capacity in neighbors:
            solver.add_edge(u, v, capacity)
    return solver


# Provide the common API used by the group's tests.
def max_flow(G, s, t):
    """Return maximum flow for adjacency-list graph G from s to t."""
    return build_dinic(G).max_flow(s, t)

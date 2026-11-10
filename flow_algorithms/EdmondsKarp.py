from collections import deque
import time

def edmonds_karp(graph, source, sink):

    """
    Implementation of the Edmonds-Karp algorithm to find the maximum flow in a flow network.

    Input variables:
        - graph: A 2D list (adjacency matrix) representing the directed graph, where graph[u][v] is the capacity of the edge from vertex u to vertex v. If there is no edge, the capacity is 0.
        - source: The index of the source vertex in the graph (The starting vertex from which the flow originates).
        - sink: The index of the sink vertex in the graph (The destination vertex where the flow terminates).
    
    Output:
    - Returns the maximum flow value (max_flow : float) from the source to the sink in the given graph.

    Notes:
    - The algorithm uses Breadth-First Search (BFS) to find augmenting paths in the residual graph.
    - The residual graph is updated after each augmenting path is found, and the process continues until no more augmenting paths can be found.
    - The algorithm assumes that all capacities are non-negative integers.

    Time Complexity:
    - The time complexity of the Edmonds-Karp algorithm is O(V * E^2), where V is the number of vertices and E is the number of edges in the graph.
    
    
    https://github.com/cp-algorithms/cp-algorithms/blob/main/src/graph/edmonds_karp.md
    https://www.w3schools.com/dsa/dsa_algo_graphs_edmondskarp.php
    
    """



    n = len(graph)

    # Create residual graph
    residual = [row[:] for row in graph]

    def bfs(source, sink, parent):
        visited = [False] * n
        queue = deque([source])

        visited[source] = True

        while queue:
            u = queue.popleft()

            for v in range(n):
                if not visited[v] and residual[u][v] > 0:
                    parent[v] = u
                    visited[v] = True

                    if v == sink:
                        return True

                    queue.append(v)

        return False

    max_flow = 0
    parent = [-1] * n

    # Find augmenting paths using BFS
    while bfs(source, sink, parent):

        # Find bottleneck capacity
        path_flow = float('inf')
        v = sink

        while v != source:
            u = parent[v]
            path_flow = min(path_flow, residual[u][v])
            v = u

        # Update residual capacities
        v = sink

        while v != source:
            u = parent[v]

            residual[u][v] -= path_flow
            residual[v][u] += path_flow

            v = u

        max_flow += path_flow

    return max_flow


"""
Test cases for the Edmonds-Karp algorithm implementation. 
This function runs a series of predefined test cases to validate the correctness of the edmonds_karp function.
"""
def test_cases_edmonds_karp():
    # Simple graph
    graph1 = [
        [0, 3, 2, 0],
        [0, 0, 0, 3],
        [0, 0, 0, 2],
        [0, 0, 0, 0]
    ]


    # Graph with multiple paths
    graph2 = [
        [0, 10, 5, 0, 0],
        [0, 0, 0, 10, 0],
        [0, 0, 0, 5, 0],
        [0, 0, 0, 0, 10],
        [0, 0, 0, 0, 0]
    ]

    # Graph with bottleneck
    graph3 = [
        [0, 10, 0, 0],
        [0, 0, 4, 0],
        [0, 0, 0, 10],
        [0, 0, 0, 0]
    ]


    # Graph requiring backward edges
    graph4 = [
        [0, 1, 1, 0],
        [0, 0, 1, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 0]
    ]


    # Disconnected sink 
    graph5 = [
        [0, 5, 0, 0],
        [0, 0, 3, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

    graph6 = [
        [0, 16, 13, 0, 0, 0],
        [0, 0, 10, 12, 0, 0],
        [0, 4, 0, 0, 14, 0],
        [0, 0, 9, 0, 0, 20],
        [0, 0, 0, 7, 0, 4],
        [0, 0, 0, 0, 0, 0]
    ]


    test_cases = [
        (graph1, 0, 3, 5),
        (graph2, 0, 4, 10),
        (graph3, 0, 3, 4),
        (graph4, 0, 3, 2),
        (graph5, 0, 3, 0),
        (graph6, 0, 5, 23)
    ]

    for i, (graph, source, sink, expected) in enumerate(test_cases, 1):
        result = edmonds_karp(graph, source, sink)

        status = "PASS" if result == expected else "FAIL"

        print(
            f"Test {i}: {status} | "
            f"Expected: {expected} | Got: {result}"
        )



# Example graph
graph = [
    [0, 16, 13, 0, 0, 0],
    [0, 0, 10, 12, 0, 0],
    [0, 4, 0, 0, 14, 0],
    [0, 0, 9, 0, 0, 20],
    [0, 0, 0, 7, 0, 4],
    [0, 0, 0, 0, 0, 0]
]

source = 0
sink = 5

start_time = time.perf_counter()
results = edmonds_karp(graph, source, sink)
end_time = time.perf_counter()
execution_time = end_time - start_time

print("Maximum Flow:", results)
print("Execution Time:", execution_time, "seconds")
test_cases_edmonds_karp()
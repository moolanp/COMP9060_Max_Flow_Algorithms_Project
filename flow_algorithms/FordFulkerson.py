import time

def ford_fulkerson(graph, source, sink):

    """
    Implementation of the Ford Fulkerson algorithm to calculate the maximum possible flow through a directed network from a designated source vertex to a destination vertex (sink).
    
    Input variables:
    - graph: A 2D list (adjacency matrix) representing the directed graph, where graph[u][v] is the capacity of the edge from vertex u to vertex v. If there is no edge, the capacity is 0.
    - source: The index of the source vertex in the graph (The starting vertex from which the flow originates).
    - sink: The index of the sink vertex in the graph (The destination vertex where the flow terminates).

    Output:
    - Returns the maximum flow value (max_flow : float) from the source to the sink in the given graph.

    Notes:
    - The algorithm uses Depth-First Search (DFS) to find augmenting paths in the residual graph.
    - The residual graph is updated after each augmenting path is found, and the process continues until no more augmenting paths can be found.
    - The algorithm assumes that all capacities are non-negative integers.

    Time Complexity:
    - The time complexity of the Ford-Fulkerson algorithm is O(E * max_flow), where E is the number of edges in the graph and max_flow is the maximum flow value found. 


    https://www.geeksforgeeks.org/dsa/maximum-flow-problem-in-python/
    https://www.geeksforgeeks.org/dsa/ford-fulkerson-algorithm-for-maximum-flow-problem/
    https://www.cs.princeton.edu/courses/archive/spring13/cos423/lectures/07NetworkFlowI-2x2.pdf
    
    """



    n = len(graph)

    # Create a residual graph
    residual = [row[:] for row in graph]

    def dfs(u, visited, parent):
        visited[u] = True

        if u == sink:
            return True

        for v in range(n):
            if not visited[v] and residual[u][v] > 0:
                parent[v] = u

                if dfs(v, visited, parent):
                    return True

        return False

    max_flow = 0
    parent = [-1] * n

    # Find augmenting paths until none exist
    while True:
        visited = [False] * n

        if not dfs(source, visited, parent):
            break

        # Find the bottleneck capacity
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
Test cases for the Ford-Fulkerson algorithm implementation. 
This function runs a series of predefined test cases to validate the correctness of the ford_fulkerson function.
"""
def test_cases_ford_fulkerson():


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
        result = ford_fulkerson(graph, source, sink)

        status = "PASS" if result == expected else "FAIL"

        print(
            f"Test {i}: {status} | "
            f"Expected: {expected} | Got: {result}"
        )


# Example graph (adjacency matrix)
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
result = ford_fulkerson(graph, source, sink)
end_time = time.perf_counter()
execution_time = end_time - start_time

print("Maximum Flow:", result)
print("Execution Time:", execution_time, "seconds")

test_cases_ford_fulkerson()
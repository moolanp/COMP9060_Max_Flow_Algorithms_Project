import time

def ford_fulkerson(graph, source, sink):

    """
    Implementation of the Ford Fulkerson algorithm to calculate the maximum possible flow through a directed network from a designated source vertex to a destination vertex (sink).
    
    Input variables:
    - graph: A dictionary representing an adjacency list. Each vertex maps to a list of (neighbour, capacity) tuples.
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

    # Create adjacency list and residual graph
    # adj structure contains both forward and reverse neighbours
    adj = {u: [] for u in graph}
    residual = {u: {} for u in graph}

    for u in graph:
        for v, capacity in graph[u]:

            # Add forward and reverse neighbours
            if v not in adj[u]:
                adj[u].append(v)

            if u not in adj[v]:
                adj[v].append(u)

            # Initialize residual capacities
            residual[u][v] = capacity
            residual[v].setdefault(u, 0)


    def dfs(u, visited, parent):
        visited[u] = True

        if u == sink:
            return True

        for v in adj[u]:
            if not visited[v] and residual[u][v] > 0:
                parent[v] = u

                if dfs(v, visited, parent):
                    return True

        return False

    max_flow = 0
    parent = {u: -1 for u in graph} # dictionary to store the parent of each vertex in the augmenting path

    # Find augmenting paths until none exist
    while True:
        visited = {u: False for u in graph} # dictionary to keep track of visited vertices during DFS

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


    # Test 1: Simple graph
    graph1 = {
        0: [(1, 3), (2, 2)],
        1: [(3, 3)],
        2: [(3, 2)],
        3: []
    }

    # Test 2: Graph with multiple paths
    graph2 = {
        0: [(1, 10), (2, 5)],
        1: [(3, 10)],
        2: [(3, 5)],
        3: [(4, 10)],
        4: []
    }

    # Test 3: Graph with bottleneck
    graph3 = {
        0: [(1, 10)],
        1: [(2, 4)],
        2: [(3, 10)],
        3: []
    }

    # Test 4: Graph requiring backward edges
    graph4 = {
        0: [(1, 1), (2, 1)],
        1: [(2, 1), (3, 1)],
        2: [(3, 1)],
        3: []
    }

    # Test 5: Disconnected sink
    graph5 = {
        0: [(1, 5)],
        1: [(2, 3)],
        2: [],
        3: []
    }

    # Test 6: Classic maximum flow example
    graph6 = {
        0: [(1, 16), (2, 13)],
        1: [(2, 10), (3, 12)],
        2: [(1, 4), (4, 14)],
        3: [(2, 9), (5, 20)],
        4: [(3, 7), (5, 4)],
        5: []
    }

    # Test 7: Original edges in both directions
    graph7 = {
        0: [(1, 10)],
        1: [(0, 5), (2, 7)],
        2: []
    }

    # Test 8: Large graph with multiple paths, cycles,
    # bottlenecks, and original reverse edges
    graph8 = {
        0: [(1, 20), (2, 15), (3, 10)],

        1: [(0, 5), (4, 12), (5, 10)],
        2: [(1, 8), (5, 10), (6, 12)],
        3: [(2, 5), (6, 10), (7, 8)],
        4: [(1, 4), (8, 10), (9, 8)],
        5: [(4, 6), (8, 10), (9, 12), (6, 5)],
        6: [(5, 3), (9, 10), (10, 12)],
        7: [(6, 4), (10, 10)],
        8: [(11, 12), (12, 8)],
        9: [(8, 5), (11, 10), (12, 10)],
        10: [(9, 6), (12, 12)],
        11: [(13, 15)],
        12: [(11, 5), (13, 15)],
        13: [(12, 4), (14, 25)],
        14: []
    }

    # source, sink, expected max flow
    test_cases = [
        (graph1, 0, 3, 5),
        (graph2, 0, 4, 10),
        (graph3, 0, 3, 4),
        (graph4, 0, 3, 2),
        (graph5, 0, 3, 0),
        (graph6, 0, 5, 23),
        (graph7, 0, 2, 7),
        (graph8, 0, 14, 25)
    ]

    print("Ford Fulkerson test cases: \n")

    for i, (graph, source, sink, expected) in enumerate(test_cases, 1):
        result = ford_fulkerson(graph, source, sink)

        status = "PASS" if result == expected else "FAIL"

        print(
            f"Test {i}: {status} | "
            f"Expected: {expected} | Got: {result}"
        )


# Example graph (adjacency matrix)
graph_input = {
    0: [(1, 16), (2, 13)],
    1: [(2, 10), (3, 12)],
    2: [(1, 4), (4, 14)],
    3: [(2, 9), (5, 20)],
    4: [(3, 7), (5, 4)],
    5: []
}



source = 0
sink = 5

start_time = time.perf_counter()
max_flow = ford_fulkerson(graph_input, source, sink)
end_time = time.perf_counter()
execution_time = end_time - start_time

print("Maximum Flow:", max_flow)
print("Execution Time:", execution_time, "seconds")

test_cases_ford_fulkerson()
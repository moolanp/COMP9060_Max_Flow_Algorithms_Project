def max_flow(graph, s, t):
    """Calculate maximum flow using the Ahuja-Orlin excess scaling algorithm.

    graph: adjacency list with vertices numbered 0 through n-1.
    s, t: source and sink vertices.
    Capacities must be nonnegative integers.
    Returns the maximum flow value without changing the input graph.

    Reference: Ahuja and Orlin (1989), A Fast and Simple Algorithm for
    the Maximum Flow Problem.

    """
    n = len(graph)
    if set(graph) != set(range(n)):
        raise ValueError("Vertices must be numbered 0 through n-1")
    if s == t:
        raise ValueError("Source and sink must be different")
    if s not in graph or t not in graph:
        raise ValueError("Invalid source or sink")

    # Each residual edge stores [destination, capacity, reverse index].
    residual = [[] for _ in range(n)]
    for u in graph:
        for v, capacity in graph[u]:
            if v not in graph:
                raise ValueError("Invalid edge endpoint")
            if type(capacity) is not int or capacity < 0:
                raise ValueError("Capacity must be a nonnegative integer")
            if u == v or capacity == 0:
                continue
            forward = [v, capacity, len(residual[v])]
            reverse = [u, 0, len(residual[u])]
            residual[u].append(forward)
            residual[v].append(reverse)

    excess = [0] * n
    height = [1] * n
    current = [0] * n
    height[s] = n
    height[t] = 0

    # Initialize preflow by saturating edges leaving the source.
    for edge in residual[s]:
        v, amount, rev = edge
        edge[1] = 0
        residual[v][rev][1] += amount
        excess[s] -= amount
        excess[v] += amount

    # Start with a power of two covering the largest intermediate excess.
    largest = max((excess[u] for u in range(n) if u != s and u != t), default=0)
    delta = 1
    while delta < largest:
        delta *= 2

    def push(u, edge, delta):
        v, capacity, rev = edge
        amount = min(excess[u], capacity)
        if v != s and v != t:
            amount = min(amount, delta - excess[v])

        edge[1] -= amount
        residual[v][rev][1] += amount
        excess[u] -= amount
        excess[v] += amount

    def relabel(u):
        height[u] = 1 + min(height[v] for v, capacity, _ in residual[u]
                            if capacity > 0)
        current[u] = 0

    # Only vertices with excess greater than delta / 2 are active in a phase.
    while delta >= 1:
        buckets = [set() for _ in range(2 * n)]
        for u in range(n):
            if u != s and u != t and 2 * excess[u] > delta:
                buckets[height[u]].add(u)

        level = 1
        while level < 2 * n:
            if not buckets[level]:
                level += 1
                continue

            # Select an active vertex with the lowest height.
            u = buckets[level].pop()

            # Current-arc pointer avoids checking the same edges again.
            while current[u] < len(residual[u]):
                edge = residual[u][current[u]]
                v = edge[0]
                if edge[1] > 0 and height[u] == height[v] + 1:
                    break
                current[u] += 1

            if current[u] == len(residual[u]):
                relabel(u)
                buckets[height[u]].add(u)
                continue

            push(u, edge, delta)

            if edge[1] == 0:
                current[u] += 1
            if 2 * excess[u] > delta:
                buckets[height[u]].add(u)
            if v != s and v != t and 2 * excess[v] > delta:
                buckets[height[v]].add(v)
                level = min(level, height[v])

        delta //= 2

    return excess[t]


def test_cases_ahuja_orlin():


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
    #Residual flow sahil's tests 
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
    #Bigger graphs with cycles sahil's tests  
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
    # Sahil's proposed tests (Simple test)
    graph9 = {
        0: [(1, 10)],
        1: [(2, 5)],
        2: []
    }
    # Multiple paths 
    graph10 = {
             0: [(1, 10), (2, 5)],
             1: [(3, 10)],
             2: [(3, 5)],
             3: []

    }
   
    #Disconnected Grapg
    graph11 = {
        0: [(1, 7)],
        1: [(2, 3)],
        2: [],
        3: []
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

    test_cases_Sahil = [
        (graph9, 0, 2, 5),
        (graph10, 0, 3, 15),
        (graph11, 0, 3, 0)
]

    all_tests = test_cases + test_cases_Sahil

    print("Ahuja-Orlin test cases: \n")

    for i, (graph, source, sink, expected) in enumerate(all_tests, 1):
        result = max_flow(graph, source, sink)

        status = "PASS" if result == expected else "FAIL"

        print(
            f"Test {i}: {status} | "
            f"Expected: {expected} | Got: {result}"
        )


if __name__ == "__main__":
    test_cases_ahuja_orlin()

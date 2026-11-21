"""Correctness tests for max flow algorithms using shared adjacency lists.

Each graph maps a vertex to outgoing (destination, capacity) pairs.
Run from the repository root: python -m pytest tests/test_.py -v
"""

import pytest
from flow_algorithms.dinic import max_flow
from flow_algorithms import preflow_push
from flow_algorithms.EdmondsKarp import edmonds_karp_max_flow
from flow_algorithms.FordFulkerson import ford_fulkerson as ford_fulkerson_max_flow
from flow_algorithms import Ahuja_Orlin_Max_Flow


# Verify all seven shared adjacency-list scenarios.
@pytest.mark.parametrize(
    "graph, source, sink, expected",
    [
        pytest.param(
            {0: [(1, 10)], 1: [(2, 5)], 2: []},
            0, 2, 5,
            id="simple_path",
        ),
        pytest.param(
            {0: [(1, 10), (2, 5)], 1: [(3, 10)], 2: [(3, 5)], 3: []},
            0, 3, 15,
            id="multiple_paths",
        ),
        pytest.param(
            {0: [(1, 1), (2, 1)], 1: [(2, 1), (3, 1)], 2: [(3, 1)], 3: []},
            0, 3, 2,
            id="residual_flow",
        ),
        pytest.param(
            {0: [(1, 7)], 1: [(2, 3)], 2: [], 3: []},
            0, 3, 0,
            id="disconnected_sink",
        ),
        pytest.param(
            {
                0: [(1, 16), (2, 13)],
                1: [(2, 10), (3, 12)],
                2: [(1, 4), (4, 14)],
                3: [(2, 9), (5, 20)],
                4: [(3, 7), (5, 4)],
                5: [],
            },
            0, 5, 23,
            id="complex_network",
        ),
        pytest.param(
            {0: [(1, 3), (1, 4)], 1: [(2, 6)], 2: []},
            0, 2, 6,
            id="parallel_edges",
        ),
        pytest.param(
            {0: [(1, 0), (2, 5)], 1: [(3, 6)], 2: [(3, 2)], 3: []},
            0, 3, 2,
            id="zero_capacity",
        ),
        pytest.param(
            {
                0: [(1, 3), (2, 2)],
                1: [(3, 3)],
                2: [(3, 2)],
                3: [],
            },
            0, 3, 5,
            id="different_path_capacities",
        ),
        pytest.param(
            {
                0: [(1, 10), (2, 5)],
                1: [(3, 10)],
                2: [(3, 5)],
                3: [(4, 10)],
                4: [],
            },
            0, 4, 10,
            id="multiple_paths_longer_network",
        ),
        pytest.param(
            {
                0: [(1, 10)],
                1: [(2, 4)],
                2: [(3, 10)],
                3: [],
            },
            0, 3, 4,
            id="bottleneck",
        ),
        pytest.param(
            {
                0: [(1, 10)],
                1: [(0, 5), (2, 7)],
                2: [],
            },
            0, 2, 7,
            id="original_reverse_edges",
        ),
        pytest.param(
            {
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
                14: [],
            },
            0, 14, 25,
            id="large_network_cycles_reverse_edges",
        ),
        pytest.param(
            {
                0: [(1, 1), (2, 1)],
                1: [(3, 1), (4, 1)],
                2: [(3, 1)],
                3: [(5, 1)],
                4: [(5, 1)],
                5: [],
            },
            0, 5, 2,
            id="residual_rerouting",
        ),
        pytest.param(
            {
                0: [(1, 1), (2, 1), (3, 1)],
                1: [(4, 1), (5, 1)],
                2: [(4, 1)],
                3: [(6, 1)],
                4: [(7, 1)],
                5: [(7, 1)],
                6: [(7, 1)],
                7: [],
            },
            0, 7, 3,
            id="residual_three_paths",
        ),
        pytest.param(
            {
                0: [(1, 8), (2, 5)],
                1: [(3, 3)],
                2: [(3, 2)],
                3: [(4, 20)],
                4: [],
            },
            0, 4, 5,
            id="bottleneck_multiple_paths",
        ),
        pytest.param(
            {
                0: [(1, 50), (2, 50)],
                1: [(3, 50)],
                2: [(3, 50)],
                3: [(4, 1)],
                4: [(5, 100)],
                5: [],
            },
            0, 5, 1,
            id="bottleneck_narrow_edge",
        ),
        pytest.param(
            {
                0: [],
                1: [(2, 10)],
                2: [(3, 10)],
                3: [],
            },
            0, 3, 0,
            id="disconnected_source",
        ),
        pytest.param(
            {
                0: [(1, 7)],
                1: [(2, 4)],
                2: [],
                3: [(4, 99)],
                4: [],
            },
            0, 2, 4,
            id="disconnected_extra_component",
        ),
        pytest.param(
            {
                0: [(1, 1024), (2, 1)],
                1: [(3, 3)],
                2: [(3, 1)],
                3: [],
            },
            0, 3, 4,
            id="unequal_capacities",
        ),
        pytest.param(
            {
                0: [(1, 15), (2, 16), (3, 17)],
                1: [(4, 15)],
                2: [(4, 16)],
                3: [(4, 17)],
                4: [],
            },
            0, 4, 48,
            id="power_two_boundaries",
        ),
        pytest.param(
            {
                0: [(1, 16), (2, 8)],
                1: [(3, 9)],
                2: [(3, 8)],
                3: [],
            },
            0, 3, 17,
            id="half_scaling_threshold",
        ),
    ],
)
# Call the public function used by other team algorithms.
def test_max_flow(graph, source, sink, expected):
    """Check the returned flow against the known maximum for each graph."""
    assert max_flow(graph, source, sink) == expected
    
    assert preflow_push.max_flow(graph, source, sink) == expected

    assert edmonds_karp_max_flow(graph, source, sink) == expected
    assert ford_fulkerson_max_flow(graph, source, sink) == expected

    assert Ahuja_Orlin_Max_Flow.max_flow(graph, source, sink) == expected

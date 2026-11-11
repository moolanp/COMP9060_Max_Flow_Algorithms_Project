"""Correctness tests for Dinic's algorithm using shared adjacency lists.

Each graph maps a vertex to outgoing (destination, capacity) pairs.
Run from the repository root: python -m pytest tests/test_dinic.py -v
"""

import pytest
from flow_algorithms.dinic import max_flow


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
    ],
)
# Call the public function used by other team algorithms.
def test_max_flow(graph, source, sink, expected):
    """Check the returned flow against the known maximum for each graph."""
    assert max_flow(graph, source, sink) == expected

import pytest
import networkx as nx

from flow_algorithms import preflow_push

@pytest.mark.parametrize("edges, expected", [
    ([('s', 't', 10)],10), # Single edge
    ([('s', 'a', 19), ('b', 't', 2)], 0), # Disconnected source and sink
    ([('s', 'a', 13), ('a', 't', 7)], 7), # Two edges of different capacity.
    ([('s', 'a', 11.5), ('a', 't', 7.3)], 7.3), # Two edges of different float capacity.
])

def test_cases(edges, expected):
    G = nx.DiGraph()
    G.add_weighted_edges_from(edges, weight='capacity')

    flow_val = preflow_push.max_flow(G, 's', 't')
    assert flow_val == expected
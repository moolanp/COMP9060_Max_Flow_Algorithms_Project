# COMP9060_Max_Flow_Algorithms_Project
BCIT COMP 9060 Applied Algorithm Analysis Project

## Algorithms

Preflow-Push (`flow_algorithms/preflow_push.py`)

## Setup

    pip install -r requirements.txt

## Running tests

    TODO

## Running benchmarks

    TODO

## Implementation Notes

### Preflow-Push - Algorithm Design Chapter 7.4: The Preflow-Push Maximum-Flow Algorithm. 357–367

The Preflow-Push Algorithm will maintain a preflow and work on converting the preflow into a flow

Flow maintains edge capacity requirements 0 <= flow(e) <= capacity(e), excess(v) = 0, (except for s,t)
Preflow maintains edge capacity requirements 0 <= preflow(e) <= capacity(e), but relaxes node flow conservation such that excess(v) >= 0, (except for s,t)

excess(v) = sum(preflow(e) into v) - sum(preflow(e) out of v) >= 0
labeling h: height(v) >= 0

Residual graph G_f of G:
    - The node set of G_f is the same as that of G.
    - For each edge e = (u, v) of G on which f(e) < c_e, there are c_e − f(e) “leftover” units of capacity on which we could
    try pushing flow forward.
    - For each edge e = (u, v) of G on which f(e) > 0, there are f(e) units of flow that we can “undo” if we want to, by
    pushing flow backward. 

A labeling height and s-t preflow are "compatible" if
(i) (Source and sink conditions) height(t) = 0 and height(s) = n,
(ii) (Steepness conditions) For all edges (v, w) in the residual graph, we have height(v) ≤ height(w) + 1.

a) s-t preflow is "compatible" with a labeling h ==> there is no s-t path in the residual graph G_f (proof by contradiction with induction)
b) no s-t path in the residual graph of a flow f  ==> flow of maximum value
c) By definition a flow is a stricter preflow where all excess[u] = 0 (except s,t). 

Combine a, b, c:

s-t flow is "compatible" with a labeling h ==> flow of maximum value.
A preflow where all nodes other than s and t have zero excess is a flow, if compatibility is maintained(Invariant) ==> the value of the max flow is exactly excess(t) = −excess(s).
Preflow-Push Algorithm will maintain a compatible preflow and labeling h , and it will work on modifying preflow and labeling h so as to transform preflow into a flow. 

Convert preflow to flow: push flow through active nodes (excess[u] > 0), or relabel when push not possible for an active node.
INVARIANT - compatibility

Throughout the Preflow-Push Algorithm:
    (i) the labels h are non-negative integers;
    (ii) f is a preflow, and if the capacities are integral, then the preflow f is integral; and
    (iii) the preflow f and labeling h are compatible.
If the algorithm returns a preflow f, then f is a flow of maximum value.

Implementations(how to choose active nodes and associated edges efficiently in order to perform push or relabel):

Uses current-arc/discharge operation for efficient indexing of admissible edges to push flow through.

active nodes ==> (excess[u] > 0)
avoids duplicate active nodes in queue or bucket array using boolean_dict[node]

FIFO (uses queue to keep track of active nodes): O(n^3) and O(n+m) space. Initialize O(n+m), Push/Relabel O(1), loop O(n^3)

Max Height (uses bucket array (list[list]) to keep track of active nodes): O(n^2 sqrt(m)) and O(n+m) space. Initialize O(n+m), Push/Relabel O(1), loop O(n^2 sqrt(m))

Future Improvements: gap heuristic for height relabel, global relabeling heuristic, link/cut tree variant.


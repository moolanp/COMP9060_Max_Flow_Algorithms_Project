from collections import deque, defaultdict

def max_flow(graph, s, t, variant = "max_height"):

    """
    Maximum flow from source s to sink t in a directed graph G using the Push-Relabel algorithm.

    Parameters
    ----------
    graph : directed graph (adjacency list) where each edge has a finite positive 'capacity' attribute.

    s : source node.

    t : sink node.
    
    variant : str, option for different variants of push-relabel, {'fifo','max_height'}
    
    "fifo": Uses queue to keep track of active nodes (excess[u] > 0), alongside current-arc/discharge operation.
    
    "max_height": Uses list of lists, indexed by node height in [0,2n-1], to keep track of active nodes (excess[u] > 0), alongside current-arc/discharge operation.

    Returns
    -------
    flow_max: float, Maximum flow value from s to t, which is excess[t].

    Notes
    -----
    The algorithm keeps track of a residual graph, vertex excess, and vertex height.
    Keeps track of active nodes(excess[node]>0) using a queue('fifo') or a list of lists('max_height'). Avoids duplicate active nodes with boolean dict.
    Uses current-arc structure and discharge operation.
    Implements global relabeling heuristic.

    References
    -----
    https://en.wikipedia.org/wiki/Push%E2%80%93relabel_maximum_flow_algorithm
    
    Éva Tardos and John Kleinberg. Algorithm Design Chapter 7.4: The Preflow-Push Maximum-Flow Algorithm. In Algorithm Design (1st ed.). Addison-Wesley ,Pearson Education, Inc., 357–367.
    
    Andrew V. Goldberg and Robert E. Tarjan. 1988. A new approach to the maximum-flow problem. J. ACM 35, 4 (October 1988), 921–940. https://doi.org/10.1145/48014.61051

    Boris V. Cherkassky and Andrew V. Goldberg. 1995. On implementing push-relabel method for the maximum flow problem. In Integer Programming and Combinatorial Optimization, Egon Balas and Jens Clausen (eds.). Springer Berlin Heidelberg, Berlin, Heidelberg, 157–171. https://doi.org/10.1007/3-540-59408-6_49

    AI: Used for documentation and code checks. See the team's README AI Use section for disclosure.

    """

    ### Edge Cases ###

    #If source and sink are the same, infinite flow possible
    if(s == t):
        raise ValueError("Source and sink are the same.")

    #Need valid sink/source nodes s/t in given graph G.
    if(s not in graph or t not in graph):
        raise KeyError("Either source or sink provided not in G.")

    if(variant not in ('fifo', 'max_height')):
        raise ValueError(f"Unexpected variant '{variant}' given.")
    
    ### Initialization ###

    residual = defaultdict(lambda: defaultdict(int))
    excess = defaultdict(int)

    # Large improvement using global relabeling heuristic. 
    # Periodically (after n relabels) performs a BFS from t backwards through the residual graph to update height[v], where height[t] = 0
    # Nodes that cannot reach t are raised to at least height n, saving multiple steps/loops of incrementing height.
    relabels_performed = 0

    #Initialize excess and the residual graph.
    for u, neighbors in graph.items():
        residual[u] # init defaultdict
        excess[u] # init defaultdict

        for v, cap in neighbors:
            residual[u][v] += cap
            residual[v][u] += 0 

    #Current-Arc Storage, used within discharge(v) function for efficient indexing of admissable edges.
    neighbors = {v: list(residual[v]) for v in residual} #neighbors in both directions since residual graph can include backward edges to push on.
    current = {v: 0 for v in residual} #current-arc index: dict of pointers, starts at 0, pointing to the first edge in neighbors[v]

    # All nodes start at height 0 , except for s at height n.
    n = len(residual)
    height = {v: 0 for v in residual}
    height[s] = n
    
    #Initialize active node storage. During initialization, only successors of s can become active.
    #Stores nodes in queue or height-indexed list[list], to keep track of active nodes for main loop. 
    #Use boolean dict to avoid duplicate nodes added to node storage.
    active_node = {v: False for v in residual}
    if(variant=='fifo'):
        node_queue = deque()
    elif(variant=='max_height'):
        nodes_at_height = [[] for i in range(2*n)] #2n is the upper bound on possible height.
        top = 0 

    # Only successors of s can receive excess/saturate (ie become active) during initialization. 
    for v, cap in graph[s]:    
        residual[s][v] -= cap
        residual[v][s] += cap
        excess[v] += cap
        excess[s] -= cap

    #Nodes with excess(active) will join the active node storage during the first global relabeling in the main loop.

    ### Define Push and Relabel ###
    
    def push(v,w):        
        #Applicable if excess(v) > 0, height(w)+1 = height(v) and (v, w) in residual graph.
        #Works on both forward and backward edges. Updates residual graph and excess.
        #Adjust excess of v and w, due to pushing d from v to w.
        
        d = min(excess[v], residual[v][w])
        residual[v][w] -= d
        residual[w][v] += d
        excess[v] -= d
        excess[w] += d
        
        return

    def relabel(v):
        #Increments relabels_performed for global relabeling heuristic
        nonlocal relabels_performed
        relabels_performed += 1

        #Applicable if excess(v) > 0, and for all edges (v, w) in residual graph: h(w) ≥ h(v)        
        height[v] = 1 + min(height[w] for w in neighbors[v] if residual[v][w] > 0)

        return
    
    # Note AI (Claude 5.5) was used to help review the code when implementing the global relabel heuristic. 
    def global_relabel():
        #Backwards BFS from the sink, on the residual graph, to update node heights.
        dist = {t: 0}
        q = deque([t])
        
        while q:
            w = q.popleft()

            for v in neighbors[w]:
                
                if(v not in dist and v != s and residual[v][w] > 0):
                    dist[v] = dist[w] + 1
                    q.append(v)

        
        #Second backwards BFS, from the source, over nodes that cannot reach t.
        #Gives them height n + (distance to s), the exact label for returning excess to s.
        dist_s = {s: 0}
        q = deque([s])

        while q:
            w = q.popleft()

            for v in neighbors[w]:

                if(v not in dist and v not in dist_s and residual[v][w] > 0):
                    dist_s[v] = dist_s[w] + 1
                    q.append(v)
        
        #Nodes that reach t get their distance to t. Nodes that only reach s get n + distance to s.
        #Nodes that reach neither get the maximum label 2n-1 (they hold no excess).
        for u in height:

            if(u == s):
                continue
            if(u in dist):
                height[u] = dist[u]
            elif(u in dist_s):
                height[u] = max(height[u], n + dist_s[u])
            else:
                height[u] = max(height[u], 2*n - 1)

        #Since heights are changed, need to re-initialize active node storage per node selection rule.
        #And re-initialize active_node (boolean dict that keeps track of nodes that are in active node storage)
        #Also since heights are changed, we need to re-initialize current-arc index (dict of pointers used with current-arc structure).
        if(variant == "fifo"):
            node_queue.clear()
        elif(variant == "max_height"):
            nonlocal top
            for row in nodes_at_height:
                row.clear()
            top = 0

        for u in height:
            current[u] = 0
            active_node[u] = False
            
            if(u != s and u != t and excess[u] > 0):
                active_node[u] = True
                
                if(variant == "fifo"):
                    node_queue.append(u)
                elif(variant == "max_height"):
                    nodes_at_height[height[u]].append(u)
                    top = max(top, height[u])

        #Reset count of relabels_performed.
        nonlocal relabels_performed
        relabels_performed = 0
   
    def discharge(v):
        #Current-arc/discharge operation to avoid looping over neighbors of v. Ie avoid repeated work in main loop
        
        #Push until v has no excess
        while(excess[v] > 0):

            #Relabel and rewind the pointer to start of v's neighbors whenever the current-arc list is exhausted.
            if(current[v] == len(neighbors[v])):
                relabel(v)
                current[v] = 0
            else:
                w = neighbors[v][current[v]]

                #Push requires excess(v) > 0, height(w)+1 = height(v) (maintains validity) and (v, w) in residual graph.
                if(residual[v][w] > 0 and height[v] == 1+height[w]):
                    push(v,w)

                    #Avoid duplicates in queue and explicitly exclude sink, source excess is always non-positive.
                    if(not active_node[w] and excess[w] > 0 and w != t):
                        active_node[w] = True
                        
                        if(variant=='fifo'): 
                            node_queue.append(w)
                
                        elif(variant=='max_height'):
                            nonlocal top
                            nodes_at_height[height[w]].append(w)
                            top = max(top, height[w])
                    
                else:
                    #Increment current[v] pointer if w was not admissible
                    current[v] += 1   
    
    ### Main Loop ###

    #Perform a global relabel to initialize node heights, saving multiple steps/loops of incrementing height.
    global_relabel()

    if(variant=="fifo"):
        
        #While there is a vertex v with excess[v] > 0.
        while node_queue:
            
            v = node_queue.popleft()
            active_node[v] = False
            
            discharge(v) # Fully exhausts excess[v] until <= 0

            #Perform global relabel heuristic after n relabels
            if(relabels_performed >= n):
                global_relabel()
    
    elif(variant=="max_height"):
        
        while True:
            while(top >= 0 and not nodes_at_height[top]):
                top -= 1
            
            if(top < 0): break
        
            v = nodes_at_height[top].pop()
            active_node[v] = False
            
            discharge(v)

            #Perform global relabel heuristic after n relabels
            if(relabels_performed >= n):
                global_relabel()
    
    ### Return ###
    
    # A preflow where all nodes other than s and t have zero excess is a flow, and the value of the max flow is exactly excess(t) = −excess(s).
    return excess[t]


# Algorithm Notes:

# Reference: Algorithm Design Chapter 7.4: The Preflow-Push Maximum-Flow Algorithm. 357–367

# The Preflow-Push Algorithm will maintain a preflow and work on converting the preflow into a flow

# Flow maintains edge capacity requirements 0 <= flow(e) <= capacity(e), excess(v) = 0, (except for s,t)
# Preflow maintains edge capacity requirements 0 <= preflow(e) <= capacity(e), but relaxes node flow conservation such that excess(v) >= 0, (except for s,t)

# excess(v) = sum(preflow(e) into v) - sum(preflow(e) out of v) >= 0
# labeling h: 0 <= height(v) < 2n

# Residual graph G_f of G:
#     - The node set of G_f is the same as that of G.
#     - For each edge e = (u, v) of G on which f(e) < c_e, there are c_e − f(e) “leftover” units of capacity on which we could
#     try pushing flow forward.
#     - For each edge e = (u, v) of G on which f(e) > 0, there are f(e) units of flow that we can “undo” if we want to, by
#     pushing flow backward.

# A labeling height and s-t preflow are "compatible" if
# (i) (Source and sink conditions) height(t) = 0 and height(s) = n,
# (ii) (Steepness conditions) For all edges (v, w) in the residual graph, we have height(v) ≤ height(w) + 1.

# a) s-t preflow is "compatible" with a labeling h ==> there is no s-t path in the residual graph G_f (proof by contradiction with induction)
# b) no s-t path in the residual graph of a flow f  ==> flow of maximum value
# c) By definition a flow is a stricter preflow where all excess[u] = 0 (except s,t).

# Combine a, b, c:

# s-t flow is "compatible" with a labeling h ==> flow of maximum value.
# A preflow where all nodes other than s and t have zero excess is a flow, if compatibility is maintained(Invariant) ==> the value of the max flow is exactly excess(t) = −excess(s).
# Preflow-Push Algorithm will maintain a compatible preflow and labeling h , and it will work on modifying preflow and labeling h so as to transform preflow into a flow.

# Convert preflow to flow: push flow through active nodes (excess[u] > 0), or relabel when push not possible for an active node.
# INVARIANT - compatibility

# Throughout the Preflow-Push Algorithm:
#     (i) the labels h are non-negative integers;
#     (ii) f is a preflow, and if the capacities are integral, then the preflow f is integral; and
#     (iii) the preflow f and labeling h are compatible.
# If the algorithm returns a preflow f, then f is a flow of maximum value.

# Implementations(how to choose active nodes and associated edges efficiently in order to perform push or relabel):

# Uses current-arc/discharge operation for efficient indexing of admissible edges to push flow through. Ie less repeated checking of residual edges per node.

# active nodes ==> (excess[u] > 0)
# avoids duplicate active nodes in queue(FIFO) or bucket array (Max Height) using boolean_dict[node]

# FIFO (uses queue to keep track of active nodes): O(n^3) and O(n+m) space. Initialize O(n+m), Push/Relabel O(1) per operation, loop O(n^3)

# Max Height (uses bucket array (list[list]) to keep track of active nodes): O(n^2 sqrt(m)) and O(n+m) space. Initialize O(n+m), Push/Relabel O(1) per operation, loop O(n^2 sqrt(m))

# Heuristics: (practical ways to speed up execution of push/relabels, significant speedups)

# Global relabeling heuristic: Periodically (after n relabels) performs a BFS from t backwards through the residual graph to update height[v], where height[t] = 0. Nodes that cannot reach t are raised to at least height n, saving multiple steps/loops of incrementing height. Implemented.

# Other: gap label heuristic (not implemented).
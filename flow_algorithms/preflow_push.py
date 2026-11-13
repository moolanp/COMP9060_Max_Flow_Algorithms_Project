import networkx as nx
from collections import deque

def max_flow(graph, s, t, variant = "max_height"):

    """
    Maximum flow from source s to sink t in a directed graph G using the Push-Relabel algorithm.

    Parameters
    ----------
    graph : directed graph (adjacency list) where each edge has a finite 'capacity' attribute.

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

    """

    ### Edge Cases ###

    #If source and sink are the same, infinite flow possible
    if(s == t):
        raise KeyError("Source and sink are the same.")

    #Need valid sink/source nodes s/t in given graph G.
    if(s not in graph.keys() or t not in graph.keys()):
        raise KeyError("Either source or sink provided not in G.")

    if(variant not in ('fifo', 'max_height')):
        raise ValueError(f"Unexpected variant '{variant}' given.")
    
    ### Initialization ###

    #Store info as nx.Digraph(), helper functions available.
    G = nx.DiGraph()
    for u, neighbors in graph.items():

        G.add_node(u)

        for v, cap in neighbors:

            if(G.has_edge(u, v)):
                G[u][v]['capacity'] += cap 
            else:
                G.add_edge(u, v, capacity = cap)

    num_nodes = G.number_of_nodes()

    #Storage for node selection during main loop. 
    #Boolean dict keeps track if a node is present in either node_queue or nodes_at_height, avoids duplicate active nodes.
    active_node = {}

    if(variant=='fifo'):
        node_queue = deque()
    elif(variant=='max_height'):
        nodes_at_height = [[] for i in range(2*num_nodes)] #2n is the upper bound on possible height.
        top = 0 
        
    #Current-Arc Storage, used within discharge(v) function for efficient indexing of admissable edges.
    neighbors = {} # neighbours in both directions since residual graph can include backward edges to push on.
    current = {}   # current-arc index - essentially a dict of pointers

    preflows = {}
    residual_G = nx.DiGraph()
    excess = {}
    height = {}

    # Large improvement using global relabeling heuristic. 
    # Periodically (after n relabels) performs a BFS from t backwards through the residual graph to update height[v], where height[t] = 0
    # Nodes that cannot reach t are raised to at least height n, saving multiple steps/loops of incrementing height.
    # Global relabeling preserves the labeling invariant requirement. Initialize at 0.
    relabels_performed = 0

    for u,v in G.edges:
        #Initialize preflows and residual graph.
        
        #For edges leaving s, preflow is equal to capacity (to avoid inclusion in residual graph as forward edge). 0 otherwise.
        if(u == s):
            preflows[(u,v)] = G[u][v]['capacity']
        else:
            preflows[(u,v)] = 0

        #Add necessary forward and backward edges into residual graph using the previously initialized preflow values.
        
        #Forward Edge into residual graph, with residual_capacity += capacity((u,v)) - preflow((u,v))
        if(G[u][v]['capacity'] > preflows[(u,v)]):

            #Check for (u,v) already in residual graph due to anti-parallel edges in G. ie (u,v) and (v,u) both in G.
            if(residual_G.has_edge(u, v)):
                residual_G[u][v]['residual_capacity'] += G[u][v]['capacity'] - preflows[(u,v)] 
            else:
                residual_G.add_edge(u, v, residual_capacity = G[u][v]['capacity'] - preflows[(u,v)])
        
        #Backward Edge into residual graph, with residual_capacity += preflow((u,v))
        if(preflows[(u,v)] > 0):
            
            #Check for (v,u) already in residual graph due to anti-parallel edges in G. ie (u,v) and (v,u) both in G.
            if(residual_G.has_edge(v, u)):
                residual_G[v][u]['residual_capacity'] += preflows[(u,v)] 
            else:
                residual_G.add_edge(v, u, residual_capacity = preflows[(u,v)] )

    for v in G.nodes:

        successors = list(G.successors(v))
        predecessors = list(G.predecessors(v))

        #Initialize excess, height, neighbours, current, and active node storage.  
    
        #neighbours in both directions since residual graph can include backward edges to push on.
        neighbors[v] = list(set(successors) | set(predecessors))

        #Each current starts at 0, corresponding to a pointer to the first neighbour/edge in neighbours[v]
        current[v] = 0     
        
        #Excess defined as sum of preflows into node - sum of preflows out of a node.
        excess[v] = sum(preflows[(u,v)] for u in predecessors) - sum(preflows[(v,w)] for w in successors)
        
        #Height initialized at 0, except for source node which starts at n. 
        if(v == s):
            height[v] = num_nodes
        else:
            height[v] = 0

        #Adds nodes to queue or height-indexed list[list], to keep track of active nodes for main loop. 
        #Use boolean dict to avoid duplicate nodes added to node storage.
        if(excess[v] > 0 and v!=t):    
            active_node[v] = True
            
            if(variant=='fifo'):
                node_queue.append(v)
            
            elif(variant=='max_height'):
                nodes_at_height[height[v]].append(v)
                top = max(top, height[v])
                
        else:
            active_node[v] = False

    # No longer need G, preflows, successors and predecessors after initialization.
    del G, preflows, successors, predecessors
    
    ### Define Push and Relabel ###
    
    def push(v,w):        
        #Applicable if excess(v) > 0, height(w) < height(v) and (v, w) in residual graph.
        #Works on both forward and backward edges. Updates residual graph and excess.
        #Note that preflow is updated at the end of the algorithm, using the final residual graph.
        
        d = min(excess[v], residual_G[v][w]['residual_capacity'])
        residual_G[v][w]['residual_capacity'] -= d

        #Adjust excess of v and w, due to pushing d from v to w.
        excess[v] -= d
        excess[w] += d
        
        #Remove forward/backward edge if no residual capacity leftover.
        if(residual_G[v][w]['residual_capacity'] == 0):
            residual_G.remove_edge(v, w)

        #Add backward/forward edge if necessary or update
        if(not residual_G.has_edge(w, v)):
            residual_G.add_edge(w, v, residual_capacity = d)
        else:
            residual_G[w][v]['residual_capacity'] += d
        
        return

    def relabel(v):
        #Increments relabels_performed for global relabeling heuristic
        nonlocal relabels_performed
        relabels_performed += 1

        #Applicable if excess(v) > 0, and for all edges (v, w) in residual graph: h(w) ≥ h(v)        
        height[v] = 1 + min(height[w] for w in residual_G.successors(v))

        return
    
    # Note AI (Claude 5.5) was used to help review the code when implementing the global relabel heuristic. 
    def global_relabel():
        #Backwards BFS from the sink, on the residual graph, to update node heights.
        dist = {t: 0}
        q = deque([t])
        
        while q:
            w = q.popleft()

            #If node not in residual graph, can skip the rest of the loop, go to next node.     
            if(w not in residual_G):
                continue
            
            for v in residual_G.predecessors(w):
                
                if(v not in dist and v != s):
                    dist[v] = dist[w] + 1
                    q.append(v)

        #Nodes that can reach t get assigned their new height, all others are raised to num_nodes (unless they have a higher height already)
        for u in height:
            
            if(u == s):
                continue
            if(u in dist):
                height[u] = dist[u]
            else:
                height[u] = max(height[u], num_nodes)

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
        #Current-arc/discharge operation to avoid looping over neighbours of v. Ie avoid repeated work in main loop
        
        #Push until v has no excess
        while(excess[v] > 0):

            #Relabel and rewind the pointer to start of v's neighbours whenever the current-arc list is exhausted.
            if(current[v] == len(neighbors[v])):
                relabel(v)
                current[v] = 0
            else:
                w = neighbors[v][current[v]]

                #Push requires excess(v) > 0, height(w) < height(v) and (v, w) in residual graph.
                if(residual_G.has_edge(v,w) and height[v] > height[w]):
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
            if(relabels_performed >= num_nodes):
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
            if(relabels_performed >= num_nodes):
                global_relabel()
    
    ### Return ###
    
    # A preflow where all nodes other than s and t have zero excess is a flow, and the value of the max flow is exactly excess(t) = −excess(s).
    return excess[t]
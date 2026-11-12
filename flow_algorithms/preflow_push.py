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

    References
    -----
    https://en.wikipedia.org/wiki/Push%E2%80%93relabel_maximum_flow_algorithm
    
    Éva Tardos and John Kleinberg. Algorithm Design Chapter 7.4: The Preflow-Push Maximum-Flow Algorithm. In Algorithm Design (1st ed.). Addison-Wesley ,Pearson Education, Inc., 357–367.
    
    Andrew V. Goldberg and Robert E. Tarjan. 1988. A new approach to the maximum-flow problem. J. ACM 35, 4 (October 1988), 921–940. https://doi.org/10.1145/48014.61051
    """

    #Store info as nx.Digraph(), helper functions available.
    G = nx.DiGraph()
    for u, neighbors in graph.items():

        G.add_node(u)

        for v, cap in neighbors:

            if(G.has_edge(u, v)):
                G[u][v]['capacity'] += cap 
            else:
                G.add_edge(u, v, capacity = cap)

    ### Edge Cases ###

    #If source and sink are the same, infinite flow possible
    if(s == t):
        raise KeyError("Source and sink are the same.")

    #Need valid sink/source nodes s/t in given graph G.
    if(s not in G.nodes() or t not in G.nodes()):
        raise KeyError("Either source or sink provided not in G.")

    if(variant not in ('fifo', 'max_height')):
        raise ValueError(f"Unexpected variant '{variant}' given.")
    
    ### Initialization ###

    #Storage for node selection during main loop. 
    #Boolean dict keeps track if a node is present in either node_queue or nodes_at_height, avoids duplicate active nodes.
    active_node = {v: False for v in G.nodes}
    
    if(variant=='fifo'):
        node_queue = deque()
    elif(variant=='max_height'):
        nodes_at_height = [[] for i in range(2*G.number_of_nodes())]
        top = 0 
        
    #Current-Arc Storage, used within discharge(v) function for efficient indexing of admissable edges.
    #neighbours in both directions since residual graph can include backward edges to push on.
    neighbors = {v: list(set(G.successors(v)) | set(G.predecessors(v))) for v in G.nodes}
    current = {v: 0 for v in G.nodes}   # current-arc index - essentially a pointer

    preflows = {}
    residual_G = nx.DiGraph()
    excess = {}
    height = {}

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
        #Initialize excess, height, and active node storage.        
        
        #Excess defined as sum of preflows into node - sum of preflows out of a node.
        excess[v] = sum(preflows[(u,v)] for u in G.predecessors(v)) - sum(preflows[(v,w)] for w in G.successors(v))
        
        #Height initialized at 0, except for source node which starts at n. 
        if(v == s):
            height[v] = G.number_of_nodes()
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

    # No longer need G, preflows after initialization.
    del G, preflows
    
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
        #Applicable if excess(v) > 0, and for all edges (v, w) in residual graph: h(w) ≥ h(v)        

        height[v] = 1 + min(height[w] for w in residual_G.successors(v))

        return
   
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

    if(variant=="fifo"):
        
        #While there is a vertex v with excess[v] > 0.
        while node_queue:
            
            v = node_queue.popleft()
            active_node[v] = False
            
            discharge(v) # Fully exhausts excess[v] until <= 0
    
    elif(variant=="max_height"):
        
        while True:
            while(top >= 0 and not nodes_at_height[top]):
                top -= 1
            
            if(top < 0): break
        
            v = nodes_at_height[top].pop()
            active_node[v] = False
            
            discharge(v)
    
    ### Return ###
    
    # A preflow where all nodes other than s and t have zero excess is a flow, and the value of the max flow is exactly excess(t) = −excess(s).
    return excess[t]
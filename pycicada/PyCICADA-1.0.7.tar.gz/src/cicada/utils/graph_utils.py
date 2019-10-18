
def welsh_powell(graph):
    """
    Implementation of the Welsh-Powell algorithm
    From: https://repl.it/repls/SpatialIgnorantList
    Args:
        graph: NetworkX graph instance

    Returns:

    """
    # sorting the nodes based on it's valency
    node_list = sorted(graph.nodes(), key=lambda x: graph.degree(x))
    # dictionary to store the colors assigned to each node
    col_val = {}
    # assign the first color to the first node
    col_val[node_list[0]] = 0
    # Assign colors to remaining N-1 nodes
    for node in node_list[1:]:
        available = [True] * len(graph.nodes())  # boolean list[i] contains false if the node color 'i' is not available

        # iterates through all the adjacent nodes and marks it's color as unavailable, if it's color has been set already
        for adj_node in graph.neighbors(node):
            if adj_node in col_val.keys():
                col = col_val[adj_node]
                available[col] = False
        clr = 0
        for clr in range(len(available)):
            if available[clr] == True:
                break
        col_val[node] = clr
    return col_val

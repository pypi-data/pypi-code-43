Ans="""

For math induction

Assume n=1,n=k,n=k+1
Prove LHS=RHS

An Euler path is a path that uses every edge of a graph exactly once.
An Euler circuit is a circuit that uses every edge of a graph exactly once.
An Euler path starts and ends at different vertices. 
An Euler circuit starts and ends at the same vertex.

A simple path in a graph G that passes through every vertex exactly once is called a Hamiltonian path.
A simple circuit in a graph G that passes through every vertex exactly once is called a Hamiltonian circuit.

Djkstra solves Shortest path problem

Kruskal (global approach): At each step, choose the cheapest available edge anywhere which does not violate the goal of creating a spanning tree.
Prim (local approach): Choose a starting vertex. At each successive step, choose the cheapest available edge attached to any previously chosen vertex which does not violate the goal of creating a spanning tree.

To find a shortest-path spanning tree:

Dijkstra: At each step, choose the edge attached to any previously chosen vertex (the local aspect) which makes the total distance from the starting vertex (the global aspect) as small as possible, and does not violate the goal of creating a spanning tree.

An augmenting path is a simple path - a path that does not contain cycles - through the graph using only edges with positive capacity from the source to the sink. 

The Ford–Fulkerson method or Ford–Fulkerson algorithm is a greedy algorithm that computes the maximum flow in a flow network

"""
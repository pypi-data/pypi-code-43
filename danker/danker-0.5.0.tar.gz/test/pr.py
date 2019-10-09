#!/usr/bin/env python3

"""
PageRank with NetworkX library
"""
import time
import sys
import networkx as nx

def main(link_file):
    """
    Main method that calls the NetworkX main function and prints the results.
    """
    start = time.time()
    graph = nx.read_edgelist(link_file, create_using=nx.DiGraph, nodetype=str, delimiter='\t')
    page_rank = nx.pagerank(graph)
    print("Computation of PageRank on '{0}' with {1} took {2:.2f} seconds.".format(
        link_file, 'NetworkX', time.time() - start), file=sys.stderr)
    for i in page_rank:
        print("{0}\t{1:.17g}".format(i, page_rank[i]))

if __name__ == "__main__":
    main(sys.argv[1])

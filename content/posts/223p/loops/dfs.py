# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "rdflib",
#   "networkx",
# ]
# ///
from rdflib import Graph, URIRef, Namespace
from rdflib.extras.external_graph_libs import rdflib_to_networkx_digraph
from networkx.algorithms import edge_dfs
import networkx as nx

EX = Namespace("http://example.com/hvac/") # from the turtle file
S223 = Namespace("http://data.ashrae.org/standard223#")

# load in the compiled graph
g = Graph().parse("hvac223p-compiled.ttl")

# turn the rdflib graph into a networkx graph so we can do traversals
g = rdflib_to_networkx_digraph(g)

# get the starting node (VAV1)
start = EX["VAV1"]
# This computes all the cycles in the graph. We only want the ones that include VAV1.
# We do this by checking if VAV1 is in the cycle.
for cycle in nx.simple_cycles(g):
    if start not in cycle:
        continue
    cycle.append(cycle[0]) # add the first node to the end to make it a cycle
    print(" -> ".join(cycle))
    print()

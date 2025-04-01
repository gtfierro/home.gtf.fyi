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
OWL = Namespace("http://www.w3.org/2002/07/owl#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

# load in the compiled graph
g = Graph().parse("hvac223p-compiled.ttl")
# use a second graph with the ontology to check if a node is of type S223:Equipment
ontg = Graph().parse("hvac223p-compiled-all.ttl")

# turn *both* rdflib graph into a networkx graphs so we can do traversals
g = rdflib_to_networkx_digraph(g)
ontg = rdflib_to_networkx_digraph(ontg)

# set of root classes; all nodes in the cycle must be a subclass of one of these
root_classes = [
    S223["Equipment"],
    S223["DomainSpace"],
    S223["Connectable"],
    S223["Connection"],
    S223["ConnectionPoint"],
]


# keep only nodes that are of type S223:Equipment or S223:DomainSpace
keep = [S223["Equipment"], S223["DomainSpace"]]


# get the root class of a node
def get_root_class(node):
    # returns the node from root_classes which has the shortest "rdfs:subClassOf" path to the node's rdf:type
    # if the node's rdf:type is not a subclass of any of the root_classes, return None
    shortest_path = None
    root_class = None
    for rc in root_classes:
        path = nx.shortest_path(ontg, node, rc)
        # only keep paths that are only classes (this means we are traversing the class structure
        # in the ontology). STart at the second node, because the first node is the node itself which
        # is not a class
        path_is_classes = all(
                ontg.has_edge(node, S223["Class"]) for node in path[1:]
        )
        if path_is_classes and (shortest_path is None or len(path) < shortest_path):
            shortest_path = len(path)
            root_class = rc
    return root_class


# get the starting node (VAV1)
start = EX["VAV1"]

# This computes all the cycles in the graph. We only want the ones that:
# - include VAV1
# - contain at least one of S223:Equipment *and* S223:DomainSpace
# Then filter out all nodes that are not of type S223:Equipment or S223:DomainSpace
new_cycles = set()
for cycle in nx.simple_cycles(g):
    if start not in cycle:
        continue
    # add types to the cycle
    typed_cycle = [
        (node, get_root_class(node)) for node in cycle
    ]
    # check if the cycle contains at least one of S223:Equipment and at least one S223:DomainSpace
    if not any(node[1] == S223["Equipment"] for node in typed_cycle) or not any(
        node[1] == S223["DomainSpace"] for node in typed_cycle
    ):
        continue
    # remove all nodes that are not of type S223:Equipment or S223:DomainSpace
    typed_cycle = [node[0] for node in typed_cycle if node[1] in keep]
    # add the first node to the end to make it a cycle
    typed_cycle.append(typed_cycle[0])
    # add the cycle to the set
    new_cycles.add(tuple(typed_cycle))

# print the cycles
for cycle in new_cycles:
    print(" -> ".join(node for node in cycle))

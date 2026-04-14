# /// script
# requires-python = "==3.10"
# dependencies = [
#   "pyontoenv==0.1.10a8",
#   "buildingmotif @ https://github.com/NREL/BuildingMOTIF.git#develop",
#   "rdflib",
# ]
# ///
from rdflib import Graph
from buildingmotif.utils import shacl_validate, shacl_infer
from ontoenv import OntoEnv, Config

# initialize the ontology environment
env = OntoEnv(Config(offline=False))

# Load the Brick model into a graph
g = Graph()
g.parse("tutorial.ttl", format="ttl")

# import the contents of all dependencies into a new graph
dep_graph = env.get_closure("urn:tutorial")

# run the SHACL inference rules on the graph
g = shacl_infer(g, dep_graph)

# validate the graph against the SHACL shapes defined in the imported ontologies
valid, report_graph, report_string = shacl_validate(g, dep_graph)
print(report_string)
print(f"Is valid: {valid}")


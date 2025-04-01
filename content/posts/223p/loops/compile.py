# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "buildingmotif[topquadrant] @ https://github.com/NREL/BuildingMOTIF.git#develop",
# ]
# ///
from buildingmotif import BuildingMOTIF
from buildingmotif.dataclasses import Library, Model

# first, we need to compile the model against the 223P ontology to get the full graph.
bm = BuildingMOTIF("sqlite://")
s223 = Library.load(ontology_graph="https://open223.info/223p.ttl")
model = Model.from_file("2025-02-23-hvac223p.ttl")
g = model.compile([s223.get_shape_collection()])
v = model.validate([s223.get_shape_collection()], error_on_missing_imports=False)
print(v.valid)
print(v.report_string)
(s223.get_shape_collection().graph + g).serialize("hvac223p-compiled-all.ttl", format="turtle")
g.serialize("hvac223p-compiled.ttl", format="turtle")

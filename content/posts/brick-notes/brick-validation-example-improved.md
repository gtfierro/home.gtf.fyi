---
title: "223P Validation Example (improved!)"
date: 2025-12-04
categories: ['Brick', 'SHACL', 'BuildingMOTIF']
type: post
---

We will use the Brick model from the previous post:

<details>
<summary>Expand for Brick Model</summary>

```ttl
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rec: <http://w3id.org/rec/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix : <urn:tutorial/> .

<urn:tutorial> a owl:Ontology ;
    owl:imports <https://brickschema.org/schema/1.4/Brick> ;
    owl:imports <http://qudt.org/2.1/vocab/unit> .

:building1 a rec:Building ;
    rdfs:label "Building 1" .

:floor1 a rec:Floor ;
    rdfs:label "Floor 1" .

:room1 a rec:Room ;
    rdfs:label "Room 1" ;
    rec:isPartOf :floor1 ;
    rec:isLocationOf :thermostat1 .

:thermostat1 a brick:Thermostat ;
    rdfs:label "Room 1 Thermostat" ;
    brick:hasPoint :room1-sp, :sensor1, :room1-occ .

:room1-sp a brick:Air_Temperature_Setpoint ;
    rdfs:label "Room 1 Setpoint" ;
    brick:hasUnit unit:DEG_F .

:sensor1 a brick:Air_Temperature_Sensor ;
    rdfs:label "Room 1 Temperature" ;
    brick:hasUnit unit:DEG_F .

:room1-occ a brick:Occupancy_Sensor ;
    rdfs:label "Room 1 Occupancy" .
```
</details>

I recommend installing [uv](https://docs.astral.sh/uv/) to handle Python dependencies and versions.

Here's the new and improved script for doing 223P validation+inference in Python.
This uses the new OntoEnv API to manage ontology dependencies, and I'm pretty happy with how it looks now.
(I have one more simplifying change to make to the API that I'll include in the next release; I'd like to just write
`s223_with_dependencies = env.get_closure(s223_id)` to both get the ontology and its dependencies in one step.)

```python
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "rdflib",
#   "pyshacl",
#   "pyontoenv>=0.4.1a1",
# ]
# ///
from rdflib import Graph
import pyshacl
from ontoenv import OntoEnv

env = OntoEnv(temporary=True, no_search=True)
model_graph = Graph().parse(sys.argv[1], format="turtle")

# add a local copy of 223p.ttl to the environment
s223_id = env.add("223p.ttl")
# returns an rdflib Graph of the ontology with all its dependencies, e.g. QUDT
s223_with_dependencies = env.get_graph(s223_id)
env.import_dependencies(s223_with_dependencies)
print(len(s223_with_dependencies))

# validate your model against the SHACL shapes
valid, report_graph, report_human = pyshacl.validate(
    data_graph=model_graph,
    shacl_graph=s223_with_dependencies,
    ont_graph=s223_with_dependencies,
    advanced=True,
    inplace=True, # this will add inferred triples to 'model_graph'
    js=True,
    allow_warnings=True,
)

print(report_human)
print(f"Is the data graph valid? {valid}")
```

Run the script with `uv run python validate_223p.py <path/to/my_building_model.ttl>`.

I recommend downloading the 223P ontology from [my website](../223p-2025-12-04.ttl). It disables some long-running rules and has a couple minor bug fixes.

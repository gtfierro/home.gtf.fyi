---
title: "Minimal Brick Validation Example"
date: 2025-01-20
categories: ['Brick']
type: post
---


This document provides a minimal example of how to validate a Brick model in Python.

## Brick Model

A Brick model is a semantic model of a specific building. It is typically represented in the [Turtle](https://www.w3.org/TR/turtle/) format. Here is an example of a simple Brick model:

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

For the purpose of validation, the most important part is the 3 lines near the top declaring the ontology and its imports:

```ttl
<urn:tutorial> a owl:Ontology ;
    owl:imports <https://brickschema.org/schema/1.4/Brick> ;
    owl:imports <http://qudt.org/2.1/vocab/unit> .
```

The first line declares the name of our graph to be `urn:tutorial`.
The `owl:imports` lines specify the ontologies that the `urn:tutorial` graph imports. In this case, the `urn:tutorial` ontology imports the Brick and QUDT ontologies.
We need to provide copies of those two dependencies to the validator; otherwise, it will not be able to resolve the classes and properties defined in those ontologies.

## Python Script

We can use the `pyontoenv` library to manage the dependencies and the `buildingmotif` library to validate the Brick model.
{{< sn >}}Eventually, `pyontoenv` will be integrated directly into `buildingmotif` but I haven't gotten around to it yet.{{< /sn >}}

Put the text containing the Brick model in a file called `tutorial.ttl`. Load this into an RDFlib graph object.

```python
# Load the Brick model into a graph
g = Graph()
g.parse("tutorial.ttl", format="ttl")
```

---

Next, we create an ontology environment. Most of the defaults are ok, but I set `offline=False` to ensure that it can fetch the ontologies from the internet.
This is necessary because we do'nt have a copy of the Brick or QUDT ontologies on our local machine.

```python
env = OntoEnv(Config(offline=False))
```

---

Now, let's calculate the *imports closure* of the `urn:tutorial` ontology. This is the set of all ontologies that are imported by `urn:tutorial`, and all ontologies imported by those ontologies, and so on.
`list_closure` calculates and outputs the names of all the ontologies in the closure.
`get_closure` returns a new RDFlib graph containing the contents of all the ontologies in the closure.

```python
for ontology in env.list_closure("urn:tutorial"):
    print(ontology)

dep_graph = env.get_closure("urn:tutorial")
```

We can see from the output that the imports closure is:

```
<urn:tutorial>
<http://qudt.org/2.1/vocab/sou>
<https://brickschema.org/schema/1.4/Brick>
<http://qudt.org/2.1/schema/facade/qudt>
<http://qudt.org/2.1/vocab/unit>
<http://spinrdf.org/spin>
<http://www.linkedmodel.org/schema/vaem>
<http://qudt.org/2.1/schema/qudt>
<http://spinrdf.org/spl>
<http://qudt.org/2.1/vocab/quantitykind>
<http://qudt.org/2.1/vocab/prefix>
<http://www.w3.org/2004/02/skos/core>
<http://qudt.org/2.1/vocab/dimensionvector>
<http://spinrdf.org/sp>
<http://www.linkedmodel.org/schema/dtype>
<http://qudt.org/2.1/schema/extensions/functions>
```

When we run the `get_closure` method, it will output a new graph containing the contents of all these ontologies.

---

Now, we can run the SHACL inference rules on the graph. This will add inferred triples to the graph based on the SHACL shapes defined in the imported ontologies.

```python
g = shacl_inference(g, dep_graph)
```

---

Finally, we can validate the graph against the SHACL shapes defined in the imported ontologies.
This will return a boolean indicating whether the graph is valid, a graph containing the validation report, and a string representation of the report.

```python
valid, report_graph, report_string = shacl_validate(g, dep_graph)
print(report_string)
print(f"Is valid: {valid}")
```

## Complete Demo

```python
# /// script
# requires-python = "==3.10"
# dependencies = [
#   "pyontoenv==0.1.10a8",
#   "buildingmotif @ https://github.com/NREL/BuildingMOTIF.git#develop",
#   "rdflib",
# ]
# ///
from rdflib import Graph
from buildingmotif.utils import shacl_validate, shacl_inference
from ontoenv import OntoEnv, Config

# initialize the ontology environment
env = OntoEnv(Config(offline=False))

# Load the Brick model into a graph
g = Graph()
g.parse("tutorial.ttl", format="ttl")

# import the contents of all dependencies into a new graph
dep_graph = env.get_closure("urn:tutorial")

# run the SHACL inference rules on the graph
g = shacl_inference(g, dep_graph)

# validate the graph against the SHACL shapes defined in the imported ontologies
valid, report_graph, report_string = shacl_validate(g, dep_graph)
print(report_string)
print(f"Is valid: {valid}")
```

You can run this script using the [`uv`](https://docs.astral.sh/uv/) tool. Simply copy the script into a file called `validate.py` and run `uv run validate.py`.
This uses a very cool [uv script feature](https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies) to automatically install the dependencies and run the script.

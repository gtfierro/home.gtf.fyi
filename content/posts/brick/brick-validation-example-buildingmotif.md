---
title: "Brick Validation Example (with BuildingMOTIF)"
date: 2025-02-04
categories: ['Brick', 'SHACL', 'BuildingMOTIF']
type: post
maturity: seedling
lastmod: 2026-04-28
updates:
  - date: "2025-02-04"
    note: "Initial draft"
  - date: "2026-04-28"
    note: "Added compiled model example"
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

We first set up the BuidlingMOTIF instance. The easiest thing to do here is create an in-memory instance so you can start fresh each time. Keep in mind that it can take a few seconds to load some
of the larger ontologies, so for "real" projects you should consider using a persistent instance.

```python
from buildingmotif import BuildingMOTIF

bm = BuildingMOTIF("sqlite://") # in-memory
```

Next, we load our model into BuildingMOTIF.
Create a `Model` object, give it a name, and load the graph from the file.

```python
from buildingmotif.dataclasses import Model

bldg = Model.from_file("tutorial.ttl")
```

Annoyingly, I haven't yet gotten around to integrating the automatic handling of ontology dependencies like in [the previous example](/posts/brick/minimal-brick-validation-example/).
So, we need to manually load the Brick and QUDT ontologies into `Library` objects.

```python
from buildingmotif.dataclasses import Library

brick = Library.load(ontology_graph="https://brickschema.org/schema/1.4/Brick")
qudt_unit = Library.load(ontology_graph="http://qudt.org/2.1/vocab/unit")
```

At this point, our `Model` and the two `Library` objects are stored in our (in-memory) BuildingMOTIF instance.
We can now validate the model against the ontologies.

```python
# the result is a ValidationContext object
context = bldg.validate([brick.get_shape_collection(), qudt_unit.get_shape_collection()])
```

The `ValidationContext` object contains the results of the validation.
It can also interpret the raw validation results into a more human-readable format.

Specifically, `ValidationContext` has the following attributes:
- `report_string`: a formatted version of the SHACL validation report
- `report`: the raw SHACL validation report as an rdflib Graph object
- `valid`: a boolean indicating whether the model is valid
- `get_broken_entities()`: lists all entities which failed validation
- `get_diffs_for_entity(entity)`: lists all reasons why a specific entity failed validation
- `diffset`: a set of human-readable reasons why the model is invalid
    - this interprets the raw SHACL results into a more human-readable format

---

## Accessing the Compiled Graph

BuildingMOTIF can also *compile* a model, which merges the model graph together with all of the ontology graphs it depends on into a single rdflib `Graph`.
It then runs SHACL inference over this merged graph, so the resulting compiled graph includes all inferred triples as well.
This is useful when you want to run SPARQL queries or other graph operations that need the full, resolved graph; for example, to traverse inferred relationships or to export a self-contained snapshot.

`Model.validate()` automatically compiles the model as part of the validation process, but you can also explicitly compile the model yourself if you just want to access the merged graph without validating.

Use `Model.compile()`. It takes the same list of shape collections and returns a `CompiledModel` whose underlying rdflib graph is available at `.graph`.

```python
# compile merges the model + all ontology graphs into one rdflib Graph
compiled = bldg.compile([brick.get_shape_collection(), qudt_unit.get_shape_collection()])

# you can also validate the compiled graph (the normal model.validate() does this automatically)
context = compiled.validate()
print(context.report_string)
print(f"Is valid: {context.valid}")

# compiled.graph is a plain rdflib Graph — use it like any other
g = compiled.graph

# example: count all triples in the compiled graph
print(f"Triples in compiled graph: {len(g)}")

# example: run a SPARQL query over the fully-resolved graph
results = g.query("""
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    SELECT ?ahu_downstream WHERE {
        ?ahu a brick:Air_Handling_Unit .
        ?ahu brick:feeds+ ?ahu_downstream .
    }
""")
for row in results:
    print(row.point)
```

---


## Complete Demo

```python
# /// script
# requires-python = "==3.10"
# dependencies = [
#   "buildingmotif @ https://github.com/NREL/BuildingMOTIF.git#develop",
# ]
# ///
from buildingmotif import BuildingMOTIF
from buildingmotif.dataclasses import Model
from buildingmotif.dataclasses import Library

bm = BuildingMOTIF("sqlite://") # in-memory

# load ontologies
brick = Library.load(ontology_graph="https://brickschema.org/schema/1.4/Brick")
qudt_unit = Library.load(ontology_graph="http://qudt.org/2.1/vocab/unit")

# create model
bldg = Model.from_file("tutorial.ttl")

# validate the model (includes running SHACL inference)
context = bldg.validate([brick.get_shape_collection(), qudt_unit.get_shape_collection()])

print(context.report_string)
print(f"Is valid: {context.valid}")
```

You can run this script using the [`uv`](https://docs.astral.sh/uv/) tool. Simply copy the script into a file called `validate.py` and run `uv run validate.py`.
This uses a very cool [uv script feature](https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies) to automatically install the dependencies and run the script.

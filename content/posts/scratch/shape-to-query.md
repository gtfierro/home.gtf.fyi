---
title: "Shape to Query"
categories: ['BuildingMOTIF','scratch']
date: 2023-06-19T17:54:57-06:00
type: post
---

# SHACL Shape to SPARQL Query Transformation

SHACL shapes can be thought of as functions that take an RDF graph as an
argument and return:
- a boolean indicating if the shape was fulfilled on the graph, and
- some extra metadata indicating why the shape was not fulfilled on the graph
  (if this is the case)

The SHACL **validation** is the process of evaluating the shapes on a given RDF
graph. This checks the conditions associated with each shape and also adds any
inferred information. The SHACL validation/inference process does *not* tell
you how the shapes came to be fulfilled on the graph, only that they were.

Because BuildingMOTIF uses SHACL shapes to validate that an RDF graph contains
the metadata necessary to run an application, we have a challenge: how to get
the metadata for the application out of the graph. Ideally, we would not have
to write a whole SPARQL query to handle this -- validation of the RDF graph should
be sufficient for extracting the necessary information out of the graph.

Inspired by tools like [SHACL Play](https://shacl-play.sparna.fr/play/sparql;),
I've written some code in a BuildingMOTIF branch to do the automated generation
of SPARQL queries from SHACL shapes.

## Example

Consider the following data graph and shape graph:

```ttl
# inside data.ttl
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix data: <urn:data/> .

<urn:data> a owl:Ontology .

data:temp_sensor1 a brick:Air_Temperature_Sensor ;
    brick:hasUnits unit:DEG_F ;
    brick:isPointOf data:vav1 .

data:temp_setpoint1 a brick:Air_Temperature_Setpoint ;
    brick:hasUnits unit:DEG_F ;
    brick:isPointOf data:vav1 .

data:vav1 a brick:Variable_Air_Volume_Box .
```

```ttl
# inside shapes.ttl
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix ref: <https://brickschema.org/schema/Brick/ref#> .
@prefix shape: <urn:shape/> .

<urn:shape> a owl:Ontology .

shape:vavApplicationShape a sh:NodeShape ;
    sh:targetClass brick:Variable_Air_Volume_Box ;
    sh:property [
        sh:name "sensor" ;
        sh:path brick:hasPoint ;
        sh:qualifiedValueShape [ sh:class brick:Air_Temperature_Sensor ] ;
        sh:qualifiedMinCount 1 ;
    ] ;
    sh:property [
        sh:name "setpoint" ;
        sh:path brick:hasPoint ;
        sh:qualifiedValueShape [ sh:class brick:Air_Temperature_Setpoint ] ;
        sh:qualifiedMinCount 1 ;
    ] ;
.
```

Assuming these files are in the current directory, we can load the `data.ttl` file into a
BuildingMOTIF model and load the `shapes.ttl` file into a shape library that we will use
to validate the model.

```python
from rdflib import URIRef, Namespace
from buildingmotif import BuildingMOTIF
from buildingmotif.dataclasses import Model, Library

# setup in-memory BuildingMOTIF (for demo purposes)
bm = BuildingMOTIF("sqlite://")

# create model and load data.ttl
model = Model.create(Namespace("urn:data/"))
model.graph.parse("data.ttl")

# get Brick ontology for definitions
brick = Library.load(ontology_graph="https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl")
# add shape.ttl to BuildingMOTIF
lib = Library.load(ontology_graph="shapes.ttl")

# ensure the model validates
result = model.validate([lib.get_shape_collection()])
print(result.valid)
```

This will output `True`: we know that the `vav1` instance fulfills the
`vavApplicationShape` shape, but we don't know the names of the sensor and
setpoint that make `vav1` valid for that application.

To fetch the configuration information from the graph, we can use the
`buildingmotif.dataclasses.ShapeCollection.shape_to_query` method:

```python
# generate the query corresponding to the vavApplicationShape shape
vav_app_shape = URIRef("urn:shape/vavApplicationShape")
query = lib.get_shape_collection().shape_to_query(vav_app_shape)
print("Generated query: ")
print(query)
```

This will output the following SPARQL query:

```sparql
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
 SELECT ?target ?setpoint ?sensor WHERE {
    ?target rdf:type/rdfs:subClassOf* <https://brickschema.org/schema/Brick#Variable_Air_Volume_Box> .
    ?target <https://brickschema.org/schema/Brick#hasPoint> ?sensor .
     ?sensor rdf:type/rdfs:subClassOf <https://brickschema.org/schema/Brick#Temperature_Sensor> .
    ?target <https://brickschema.org/schema/Brick#hasPoint> ?setpoint .
     ?setpoint rdf:type/rdfs:subClassOf <https://brickschema.org/schema/Brick#Temperature_Setpoint> .
}
```

which, cleaned up a bit, looks like:

```sparql
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
 SELECT ?target ?setpoint ?sensor WHERE {
    ?target rdf:type/rdfs:subClassOf* brick:Variable_Air_Volume_Box .
    ?target brick:hasPoint ?sensor .
     ?sensor rdf:type/rdfs:subClassOf brick:Temperature_Sensor .
    ?target brick:hasPoint ?setpoint .
     ?setpoint rdf:type/rdfs:subClassOf brick:Temperature_Setpoint .
}
```

We can see that the query has inherited the variable names specified in
`sh:name`, which assists with readability. If these names are not provided,
BuildingMOTIF will invent some names.

Running this query on our model yields the configuration info necessary to run the application:

```python
# "compile" the model to get all the inferred information from SHACL
expanded_graph = model.compile([brick.get_shape_collection(), lib.get_shape_collection()])
for row in expanded_graph.query(query):
    print(row.asdict())
```

This prints

```text
{'target': rdflib.term.URIRef('urn:data/vav1'),
 'sensor': rdflib.term.URIRef('urn:data/temp_sensor1'),
 'setpoint': rdflib.term.URIRef('urn:data/temp_setpoint1')}
```

which gives the developer the URIs for the sensor, setpoint and target identified in the shape.

## Approach

<details>
<summary>
Here's the rough code for generating the SPARQL queries. It is far from complete but shouldn't be too
hard to add extra cases
</summary>

```python
def shape_to_query(graph: Graph, shape: URIRef) -> str:
    clauses, project = _shape_to_where(graph, shape)
    preamble = """PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    """
    return f"{preamble} SELECT {' '.join(project)} WHERE {{\n{clauses}\n}}"


def _shape_to_where(graph: Graph, shape: URIRef) -> Tuple[str, List[str]]:
    # we will build the query as a string
    clauses: str = ""
    # build up the SELECT clause as a set of vars
    project: Set[str] = {"?target"}

    # local state for generating unique variable names
    prefix = "".join(random.choice(string.ascii_lowercase) for _ in range(2))
    variable_counter = 0

    def gensym():
        nonlocal variable_counter
        varname = f"{prefix}{variable_counter}"
        variable_counter += 1
        return varname

    # `<shape> sh:targetClass <class>` -> `?target rdf:type/rdfs:subClassOf* <class>`
    targetClasses = graph.objects(shape, SH.targetClass)
    tc_clauses = [
        f"?target rdf:type/rdfs:subClassOf* {tc.n3()} .\n" for tc in targetClasses  # type: ignore
    ]
    clauses += " UNION ".join(tc_clauses)

    # find all of the non-qualified property shapes. All of these will use the same variable
    # for all uses of the same sh:path value
    pshapes_by_path: Dict[Node, List[Node]] = defaultdict(list)
    for pshape in graph.objects(shape, SH.property):
        path = graph.value(pshape, SH.path)
        if not graph.value(pshape, SH.qualifiedValueShape):
            pshapes_by_path[path].append(pshape)  # type: ignore
    # assign a unique variable for each sh:path w/o a qualified shape
    pshape_vars: Dict[Node, str] = {}
    for pshape_list in pshapes_by_path.values():
        varname = f"?{gensym()}"
        for pshape in pshape_list:
            pshape_vars[pshape] = varname

    for pshape in graph.objects(shape, SH.property):
        # get the varname if we've already assigned one for this pshape above,
        # or generate a new one. When generating a name, use the SH.name field
        # in the PropertyShape or generate a unique one
        name = pshape_vars.get(
            pshape, f"?{graph.value(pshape, SH.name) or gensym()}".replace(" ", "_")
        )
        path = graph.value(pshape, SH.path)
        qMinCount = graph.value(pshape, SH.qualifiedMinCount) or 0

        pclass = graph.value(
            pshape, (SH["qualifiedValueShape"] * ZeroOrOne / SH["class"])  # type: ignore
        )
        if pclass:
            clause = f"?target {path.n3()} {name} .\n {name} rdf:type/rdfs:subClassOf* {pclass.n3()} .\n"
            if qMinCount == 0:
                clause = f"OPTIONAL {{ {clause} }} .\n"
            clauses += clause
            project.add(name)

        pnode = graph.value(
            pshape, (SH["qualifiedValueShape"] * ZeroOrOne / SH["node"])  # type: ignore
        )
        if pnode:
            node_clauses, node_project = _shape_to_where(graph, pnode)
            clause = f"?target {path.n3()} {name} .\n"
            clause += node_clauses.replace("?target", name)
            if qMinCount == 0:
                clause = f"OPTIONAL {{ {clause} }}"
            clauses += clause
            project.update({p.replace("?target", name) for p in node_project})

        pvalue = graph.value(pshape, SH.hasValue)
        if pvalue:
            clauses += f"?target {path.n3()} {pvalue.n3()} .\n"

    return clauses, list(project)
```
</details>

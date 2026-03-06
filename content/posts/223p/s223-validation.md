---
title: "Validating ASHRAE 223P models"
date: 2026-03-05
categories: ['223P', 'SHACL', 'ontoenv', 'shifty']
type: post
---

*Note: I'll be using my [ontoenv](https://ontoenv.gtf.fyi/) tool to build this post*

The ASHRAE 223P standard defines a set of SHACL shapes for validating building models.
This post explains how to use those shapes to validate a building model, and also how to handle the ontology dependencies that the 223P shapes have.

### Ontology Dependencies

A shapes graph contains a set of SHACL shapes that define the validation rules for a particular domain.
Ontologies like ASHRAE 223P contain shapes which govern the structure and semantics of models; I'll use "shapes graph" and "ontology" interchangeably here, but the important thing is that the graph contains SHACL shapes that we want to use for validation.

Shapes often reference classes and properties defined in other ontologies.
223P, Brick and other cyber-physical ontologies commonly import the QUDT (Quantifiable Units and Data Types) ontology, which defines units of measurement and data types that are used in the shapes.
Importing an ontology is helpful because it allows us to outsource definitions and validation rules, much in the same way that we download software libraries instead of writing all the code ourselves.
However, it also means that we need to have those ontologies available when we want to validate a model against the shapes.

Ontology graphs contain triples defining the name of the ontology and associated metadata, which can include any number of `owl:imports` statements that reference other ontologies. When we want to validate a model against the shapes in that graph, we need to make sure that we also have access to all the ontologies that are imported by the shapes graph, and any ontologies that those ontologies import, and so on (i.e. the entire dependency tree).

Here's an example from the 223P ontology:

```turtle
<http://data.ashrae.org/standard223/1.0/model/all> a owl:Ontology ;
    # omitting other metadata for brevity...
    owl:imports <http://qudt.org/3.1.8/shacl/qudt-all>,
                <http://www.w3.org/ns/shacl> .
```

`http://data.ashrae.org/standard223/1.0/model/all` is the name 223P shapes graph, and it imports two ontologies: `http://qudt.org/3.1.8/shacl/qudt-all` (the QUDT shapes) and `http://www.w3.org/ns/shacl` (the SHACL specification shapes).
If you visit the QUDT link (http://qudt.org/3.1.8/shacl/qudt-all), you'll be directed to a Turtle file (another shapes graph!) that itself has `owl:imports` statements:

```turtle
<http://qudt.org/3.1.8/shacl/qudt-all> a owl:Ontology ;
  # omitting other metadata for brevity...
  owl:imports <http://www.linkedmodel.org/schema/vaem> ;
  owl:imports <http://www.w3.org/2004/02/skos/core> ;
  owl:imports <http://www.w3.org/ns/shacl> .
```

*those* ontologies may have their own dependencies, and so on.

Here's the graph of dependencies for the 223P ontology as of 2026-03-05 :

{{< figure width="75%" src="../223pdeps.png" alt="223p dependency graph as of 2026-03-05">}}

<details>
<summary>Generating this figure with `ontoenv`</summary>

From the `223standard` git repo, I first ran this command to create the environment

```
ontoenv init --offline -- data models extensions imports inference models validation vocab collections
```

then this command to generate a PDF of the dependency graph, rooted at the 223P ontology:

```
ontoenv dep-graph http://data.ashrae.org/standard223/1.0/model/all
```
</details>

To validate a model against 223P, we first need to find (a) the 223P graph (containing the shapes defining the validation task), and (b) any ontology dependencies that the 223P graph has.
These dependencies are important because the shapes in the 223P graph may reference classes and properties defined in those ontologies, and if we don't have those ontologies available, the validation may fail (due to missing classes/properties) or may give incorrect results (if the shapes are not evaluated correctly due to missing dependencies).

Here's a quick example.
The `s223:EnumerationKind-Numerical` shape mandates that instances of that enumeration kind must have a unit of measure (instance of `qudt:Unit`) associated via the `qudt:hasUnit` relationship.

```turtle
# simplified version of the actual shape, which is more complex and includes some additional rules and constraints
s223:EnumerationKind-Numerical a s223:Class, sh:NodeShape ;
        sh:property [ rdfs:comment "An `EnumerationKind-Numerical` shall be associated with exactly one Unit using the relation `qudt:hasUnit`."^^xsd:string ;
            sh:class qudt:Unit ;
            sh:maxCount 1 ;
            sh:minCount 1 ;
            sh:path qudt:hasUnit ] .
```

Imagine I have the following model that I want to validate against the 223P shapes:

```turtle
ex:myEnum a s223:EnumerationKind-Numerical ;
    qudt:hasUnit unit:Volt .
```

Without including the QUDT graph in the validation, there is no statement to assert that `unit:Volt` is an instance of `qudt:Unit`, so the validation would fail (because the shape requires that the value of `qudt:hasUnit` must be an instance of `qudt:Unit`).

### Assembling the 223P graph with its dependencies

The short answer here is to use the [Open223](https://open223.info/) site, which has a link to a recent version of the 223P shapes graph.
You can use this graph directly in your validation script, or you can download it and use it as a local file.
You can download the `223p.ttl` file from https://open223.info/223p.ttl --- however, this won't have all the dependencies included, so you would need to also download the QUDT shapes and any other dependencies that the 223P graph has.

`ontoenv` can make this much easier to manage.
Here are two ways to assemble the 223P graph with its dependencies using `ontoenv`:

First, on the command line, which is helpful for GitHub actions or other non-Python environments:

```bash
# initializes an empty environment
ontoenv init

# adds the 223P graph and all its dependencies to the environment; this will
# also cache the graphs locally so that they can be used in future validations
# without needing to re-download
ontoenv add https://open223.info/223p.ttl 

# prints out the ontologies that were added to the environment, including the
# 223P graph and its dependencies
ontoenv list ontologies
# should print out:
# http://data.ashrae.org/standard223/1.0/model/all
# http://qudt.org/3.1.8/shacl/qudt-all
# http://www.linkedmodel.org/schema/vaem
# http://www.w3.org/2004/02/skos/core
# http://www.w3.org/ns/shacl#

# create the imports "closure" and save it to a local file; this file will
# contain the 223P graph and all its dependencies in one file, which can be used
# for validation # IMPORTANT: use the *name* of the 223P ontology
# (http://data.ashrae.org/standard223/1.0/model/all) and not the URL of the file
# (https://open223.info/223p.ttl), because the imports are defined in terms of
# the ontology name, not the file URL
ontoenv closure http://data.ashrae.org/standard223/1.0/model/all 223p_with_deps.ttl
```

Second, in Python, which is helpful for more complex validation scripts or when you want to run inference as part of validation:

```python
from ontoenv import OntoEnv

# doesn't scan local directories, won't save anything to disk
env = OntoEnv(temporary=True)
env.add("https://open223.info/223p.ttl")

shapes, imported = env.get_closure("http://data.ashrae.org/standard223/1.0/model/all")
print(f"Imported the following ontologies: {imported}\ntotal triples: {len(shapes)}")
# should give output like:
# Imported the following ontologies: ['http://data.ashrae.org/standard223/1.0/model/all', 'http://qudt.org/3.1.8/shacl/qudt-all', 'http://www.w3.org/ns/shacl#', 'http://www.w3.org/2004/02/skos/core', 'http://www.linkedmodel.org/schema/vaem']
# total triples: 142605
```
and now you've got an rdflib graph (`shapes`) that contains the 223P shapes and all their dependencies.

{{< announce >}}
2026-03-05: it is on my TODO list to integrate ontoenv with BuildingMOTIF. I hope to report this integration soon!
{{< /announce >}}

If you want to use another tool for managing dependencies (like BuildingMOTIF), you
can also use `ontoenv` to explicitly list the dependencies of the 223P graph, and then add those dependencies to your tool of choice.

```python
from ontoenv import OntoEnv
from buildingmotif import BuildingMOTIF
from buildingmotif.dataclasses import Library

bm = BuildingMOTIF("sqlite://")

# doesn't scan local directories, won't save anything to disk
env = OntoEnv(temporary=True)
env.add("https://open223.info/223p.ttl")
for dep in env.list_closure("http://data.ashrae.org/standard223/1.0/model/all"):
    print(dep) # should print out the same list of ontologies as before
    graph = env.get_graph(dep)
    # add 'graph' to your tool of choice here, like BuildingMOTIF
    Library.load(ontology_graph=graph)
```

### Validating a model against the 223P shapes

Now that you've got the shapes graph assembled with all the dependencies, you can use it to validate your model.
Below is an example of how to do this using `pySHACL`.

I'm showing a slightly different use of `ontoenv` here, which scans the local directory for ontologies, which allows us to use local files for validation instead of needing to re-download from the web every time.
For example, if we have a local copy of the 223P graph and its dependencies, we can just put those in the current directory and they will be found by the environment.
This is usually how I use `ontoenv` in my own scripts.

```python
from ontoenv import OntoEnv
import pyshacl
from rdflib import Graph

# scans the current directory for local ontology files
env = OntoEnv(search_directories=["."])
env.add("https://open223.info/223p.ttl")
shapes, imported = env.get_closure("http://data.ashrae.org/standard223/1.0/model/all")

model = Graph().parse("mymodel.ttl", format="turtle")
valid, report_graph, report_human = pyshacl.validate(
    data_graph=model,
    shacl_graph=shapes,
    ont_graph=shapes,
    advanced=True,
    inplace=True, # this will add inferred triples to 'model'
    js=True,
    allow_warnings=True,
)
```


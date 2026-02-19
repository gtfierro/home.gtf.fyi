---
title: "My shortest Brick validation+inference script yet"
date: 2026-02-19
categories: ['Brick', 'SHACL', 'ontoenv', 'shifty']
type: post
---

My evenings these past few weeks have been spent working on [ontoenv](https://ontoenv.gtf.fyi/) (a dev environment manager for ontologies) and [shifty](https://github.com/gtfierro/shifty) (a vibe-coded SHACL implementation).
They are finally at the stage where I can get a short script working that does both inference and validation of a building model against the 223P SHACL shapes, and I'm pretty happy with how it looks!

<details>
<summary>The example model needs an `owl:imports` statement:</summary>

```turtle
@prefix owl: <http://www.w3.org/2002/07/owl#> .

<http://example.com/ontoenv-example/> a owl:Ontology ;
    owl:imports <https://brickschema.org/schema/1.4/Brick> .

# etc... rest of your model
```
</details>

Here's the short version of the script:

```python
# /// script
# dependencies = [
#     "ontoenv==0.5.0a8",
#     "pyshifty",
#     "rdflib",
# ]
# ///
from rdflib import Graph
import shifty

model_graph = Graph().parse("mymodel.ttl", format="turtle")
print("Model triples:", len(model_graph))

validates, results_graph, results_text = shifty.validate(
    model_graph, run_inference=True, skip_invalid_rules=True
)
print(results_text)
print("Conforms?", validates)
```

This script automatically fetches the shapes required for validation, runs inference as part of validation, and skips any rules that are invalid (e.g. due to missing dependencies or unsupported features). This *return* signature is the same as [pySHACL](https://github.com/RDFLib/pySHACL).

Here's the longer, more verbose script that shows off several of the features

```python
# /// script
# dependencies = [
#     "ontoenv==0.5.0a8",
#     "pyshifty",
#     "rdflib",
# ]
# ///
from rdflib import Graph
from ontoenv import OntoEnv
import shifty

# https://ontoenv.gtf.fyi/ for ontology dependencies
# ontoenv>=0.5 removed `no_search`; pass an empty search list to disable scanning.
env = OntoEnv(temporary=True, search_directories=[])

# force use of the nightly Brick release (1.4.nightly); mymodel.ttl imports Brick 1.4
# so importing our preferred version of Brick into the environment *first* ensures
# that we are using the latest version of Brick, which has the latest SHACL shapes and bug fixes.

env.add("https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl")

# load the model to be validated; it should have an owl:imports statement for
# Brick (or whatever shapes it needs)
model_graph = Graph().parse("mymodel.ttl", format="turtle")
print("Model triples:", len(model_graph))

# download all dependencies for the model. This follows owl:imports statements
# in the model graph to find the shapes and any dependencies of those shapes
# (e.g. QUDT).
shape_graph, imported = env.get_dependencies_graph(model_graph, fetch_missing=True, recursion_depth=1)
print(f"Imported {imported} dependencies.")
print(imported)
print("Shape triples:", len(shape_graph))

# how to calculate the inferred triples directly, e.g. to prepare for querying:
# skip imports during inference to avoid re-fetching dependencies
#compiled = shifty.infer(model_graph, shape_graph, do_imports=False, skip_invalid_rules=True)
#print("Inferred triples:", len(compiled))

# runs validation. Can perform inference as part of this (run_inference=True)
# We pre-computed the shape graph (get_dependencies_graph) so we use
# do_imports=False to avoid re-doing that work. In practice, no reason to do
# this. Just call shifty.validate(model_graph, shape_graph) and it should handle
# everything!
validates, results_graph, results_text = shifty.validate(
    model_graph,
    shape_graph,
    run_inference=True,
    do_imports=False,
    skip_invalid_rules=True,
)
print(results_text)
print("Conforms?", validates)
```


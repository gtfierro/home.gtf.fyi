---
title: "Using Ontoenv and Shifty to validate ASHRAE 223 models"
date: 2026-06-07
categories: ['shifty','ontoenv','223']
type: post
maturity: seedling
updates:
    - date: "2026-06-07"
      note: "Working script with ontoenv==0.5 and shifty==0.2.4"
---

My [`ontoenv`](https://ontoenv.gtf.fyi) and [`shifty`](`https://pyshifty.gtf.fyi`) projects
are far enough along that I can provide some simple scripts for validating ASHRAE 223 models.

Here's the simple version of the script that requires you to provide all of the ontologies you want to validate against:

```python
# /// script
# dependencies = [
#    "rdflib",
#    "pyshifty>=0.2.5"
#   ]
#  python = ">=3.10"
# ///
import rdflib
import shifty
import sys


print("Loading model file into rdflib graph...")
model_file = sys.argv[1] if len(sys.argv) > 1 else "https://models.open223.info/NIST-IBAL.ttl"
model = rdflib.Graph().parse(model_file)

# If you know the ontologies you want to use for validation,
# you can load the graphs manually
s223 = rdflib.Graph().parse("https://open223.info/223p.ttl")
qudt = rdflib.Graph().parse("http://qudt.org/3.2.1/shacl/qudt-all")
# provide both shape graphs to the validator
conforms, report_graph, results_text = shifty.validate(model, [s223, qudt], minimum_severity="Violation")
print("Validation results:")
print(results_text)
print(f"Conforms: {conforms}")
```

Here's the slightly more complex version that uses `ontoenv` for automatic
resolution of the ontology dependencies.

```python
# /// script
# dependencies = [
#    "rdflib",
#    "ontoenv>=0.5",
#    "pyshifty>=0.2.5"
#   ]
#  python = ">=3.10"
# ///
import rdflib
import ontoenv
import shifty
import sys

model_file = sys.argv[1] if len(sys.argv) > 1 else "https://models.open223.info/NIST-IBAL.ttl"

env = ontoenv.OntoEnv(temporary=True)

model_id = env.add(model_file)
model = env.get_graph(model_id)

# you can use ontoenv to load the ontologies and their dependencies automatically

# we have to tell ontoenv where 223P is, because the ontology's URL is not
# "live" yet. However, the ontologies mentioned in the imports of 223P *are*
# available at their URLs, so we can use the OntoEnv to get the closure graph
# for validation
print("Loading S223 and dependencies into OntoEnv...")
env.add("https://open223.info/223p.ttl") # this will download all dependencies into OntoEnv

print("Gathering closure graph for validation...")
# here we ask the model for what its owl:imports are. OntoEnv
# returns a single graph containing the full imports closure
closure, imported = env.get_closure(model_id)
print(f"Closure graph imported {len(imported)} ontologies.")

print("Validating model against S223...")
conforms, report_graph, results_text = shifty.validate(model, closure, minimum_severity="Violation")
print("Validation results:")
print(results_text)
print(f"Conforms: {conforms}")
```

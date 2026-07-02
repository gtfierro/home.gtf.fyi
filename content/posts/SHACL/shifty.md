---
title: "Shifty SHACL Engine"
date: 2026-06-30
categories: ['shifty','shacl','rdf']
type: post
maturity: seedling
lastmod: 2026-07-01
updates:
  - date: "2026-06-30"
    note: "Initial draft"
  - date: "2026-07-01"
    note: "Add links to benchmarking scripts"
  - date: "2026-07-01"
    note: "Add bigger benchmark results (best of 5)"
---

I vibe-coded a new SHACL validation and inference engine called [shifty](https://shifty.gtf.fyi) to address the speed and reporting issues I have run into with existing SHACL implementations.

> Want to use pyshifty? Check out the [web playground](https://shifty.gtf.fyi/playground) or the [Python API](https://pypi.org/project/pyshifty/).
> Links and docs available at [shifty.gtf.fyi](https://shifty.gtf.fyi).

SHACL (Shapes Constraint Language) is a language for validating RDF graphs against sets of conditions called shapes.
A SHACL extension called SHACL-AF additionally allows for forward-chaining inference rules to be defined in the shape graph, which can be used to infer new triples in the data graph.

I use SHACL extensively in my work on the [Brick](https://brickschema.org) and [ASHRAE 223(P)](https://open223.info) ontologies for smart buildings.
We use SHACL shapes to normalize knowledge graphs (e.g., add missing or implied edges), ensure correct usage of the ontologies, and to ensure the building KGs are ["semantically sufficient"](https://gtf.fyi/papers/fierro2022application.pdf) to run/configure applications.
There are a few characteristics of our use of SHACL that are worth highlighting:
- we distribute our ontologies (Brick, 223P) separately from individual building KGs. We imagine that buildings develop their own knowledge graphs that make reference to these ontologies. 
- SHACL validation and inference are run frequently as part of iterative development of the building KGs, suggesting that the *speed* of validation and inference is important to the quality of the development process
- when validation fails, we want to know *why* it failed, so that we can fix the problem. I'll dig more into this problem below.

## Issues with Existing SHACL Implementations

I want to start this section by saying I have tremendous respect for existing SHACL implementations.
In particular, [pySHACL](https://github.com/RDFLib/pySHACL) and [TopQuadrant's implementation](https://github.com/TopQuadrant/shacl) have both been critical resources to developing Brick and 223P, and I have learned a lot from both of these projects.
I am still using both of these implementations in my work, and I will continue to do so.

That said, there are some issues with existing SHACL implementations that I have run into in my work, which motivated me to develop my own SHACL implementation.

### Issue 1: Speed

A deeper dive into the performance of existing SHACL implementations is beyond the scope of this post, but in my experience I have noticed a couple sources of slowness in existing implementations. These performance issues are also mostly due to design choices we have made within Brick and ASHRAE 223(P), but they happen to demonstrate some pathological cases that existing SHACL implementations struggle with.

**Fixed-point inference:** ASHRAE 223(P) has a number of inference rules that are defined in the shape graph, and these rules are applied to the data graph until a fixed point is reached. The most significant use of this is in the ASHRAE 223(P) connection model:

{{< figure width="100%" src="/posts/SHACL/img/s223-connection.pdf" alt="ASHRAE 223(P) connection model">}}

One only needs to provide the `s223:cnx` relationships; through successive applications of SHACL inference, each of the other layers of the connection model are inferred. This is a very useful feature, but it can be slow to compute, especially when the shape graph is large and complex.

**Blank nodes and skolemization:** Related to the above issue, many rules in Brick and ASHRAE 223(P) require reasoning about the class hierarchy of the ontologies.
{{< sn >}}You can see evidence that this is a problem in the new [SHACL 1.2 specification](https://www.w3.org/TR/shacl12-core/#subClassOfInShapesGraph): "rdfs:subClassOf triples are often stored as part of the class and/or shape definitions and not the instance data"{{< /sn >}}
This presents a problem for traditional SHACL/SHACL-AF, which *technically* require the class/subclass definitions to be present within the data graph. However, in our use cases, we provide the class definitions in our ontology --- not the data graph!
This means we need to compute the union of the shapes and data graphs; normally this would not be a problem except for the fact that we use blank nodes extensively throughout our ontology definitions.{{< sn >}}Use of blank nodes is actually *required* in certain SHACL constructs like property paths and node expressions, so this is unavoidable.{{< /sn >}}
Blank nodes do not have a stable identity, which makes them difficult to de-duplicate.
If any of our inference rules create new blank nodes, we need to ensure that these blank nodes are skolemized (i.e., given a stable identity) so that they can be recognized as the same nodes in subsequent iterations of the fixed-point inference process.
Skolemization is slow, and we often need to apply it to our graphs before providing them to existing SHACL implementations, which adds to the overall slowness of the process.

**Empty targets:** Brick defines over a thousand classes, each of which is a SHACL NodeShape that targets instances of that class.
If there are no instances of a class in the data graph, then the corresponding NodeShape will have an empty target.
Existing SHACL implementations still attempt to evaluate these shapes, which is unnecessary and adds to the overall slowness of the process.

### Issue 2: The W3C SHACL Report is Unsatisfying

This is also an issue I can write much more about in future posts, but the W3C SHACL report is unsatisfying for a couple reasons.

**Terminates at aggregate components:** The W3C SHACL report terminates at aggregate components (e.g., `sh:and`, `sh:or`, `sh:xone`, `sh:not`), which hides the real reason for a validation failure. For example, if an `sh:or` fails, the report will only indicate that the `sh:or` failed, without providing any information about which branch failed or why.
Some implementations (e.g., pySHACL) provide a "detail" option that will provide more information about which branch failed, but this is often still not enough information to understand the root cause of the failure.

Here's a concrete example from Brick. Temperature sensors must have a unit, and the unit must be either degrees Fahrenheit or degrees Celsius (using the QUDT ontology):

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix sh:    <http://www.w3.org/ns/shacl#> .
@prefix unit:  <http://qudt.org/vocab/unit/> .

brick:TemperatureSensorShape a sh:NodeShape ;
    sh:targetClass brick:Temperature_Sensor ;
    sh:or (
        [ sh:property [ sh:path brick:hasUnit ; sh:hasValue unit:DEG_F ] ]
        [ sh:property [ sh:path brick:hasUnit ; sh:hasValue unit:DEG_C ] ]
    ) .
```

A W3C-conformant SHACL report for a sensor with no unit looks like:

```turtle
[ a sh:ValidationResult ;
  sh:resultSeverity sh:Violation ;
  sh:focusNode ex:TemperatureSensor1 ;
  sh:sourceShape brick:TemperatureSensorShape ;
  sh:sourceConstraintComponent sh:OrConstraintComponent ;
  sh:resultMessage "sh:or failed (or something similar to this)" ] .
```

Which branch? Which property was missing? The report doesn't say. In practice this means going back to the shape definition, checking both branches manually, and figuring out which one applies.

**No validation witnesses:** The W3C SHACL report does not provide any information about why a node *passed* validation. This is a problem for downstream applications that want to generate human-readable explanations of a model, not just validate it.
We need this feature for using SHACL validation results for application configuration, which is a key feature of [BuildingMOTIF](https://github.com/NatLabRockies/BuildingMOTIF); working around this required developing a SHACL/SPARQL translation feature.
Finally, I recognize this is a niche use, but we did find it necessary to develop this feature for our [current work on graph repair](https://gtf.fyi/papers/lin2025systematic.pdf) where we use passing subgraphs as part of the context to an LLM-based repair agent.

## Introducing Shifty

[Shifty](https://shifty.gtf.fyi) is a new (**100% vibe coded**{{< sn >}}I call the project "shifty" because you would be right to be skeptical over using an AI-generated project for something as critical as knowledge graph validation!{{< /sn >}}), SHACL validation and inference engine.
The core is implemented in Rust ([crates.io](https://crates.io/crates/shifty)), but you can interact with shifty over the [command line](https://shifty.gtf.fyi/docs/cli), a [Python API](https://pypi.org/project/pyshifty/) ([docs](https://shifty.gtf.fyi/python-api/index.html)), a [C++ API](https://github.com/gtfierro/shifty/tree/main/cpp), our [web-based workbench](https://shifty.gtf.fyi/playground), or a [WebAssembly package](https://github.com/gtfierro/shifty/tree/main/crates/shifty-wasm).
In my latest benchmarks, shifty performs validation and inference on brick and 223 graphs in less than 10 seconds. It is roughly X times faster than TopQuadrant's SHACL implementation, and Y times faster than pySHACL.

Shifty has the following features, available in each of the distributions/packages above:
- full support for SHACL and SHACL-AF (except for Javascript extensions)
    - includes SPARQL constraints, custom constraint components, node expressions, SHACL functions, SPARQL targets
    - no SHACL 1.2 yet
- fixed-point SHACL-AF forward chaining inference
- supports stratified recursion during validation and inference
- an efficient "algebra-based" engine that doesn't produce the W3C SHACL report, but instead reports a complete explanation of why each node passed or failed validation, including the specific constraints that were violated and the values that caused the violation. I'm the most excited about this feature, which I'll briefly describe below
- profiling output, allowing you to see how long each rule/shape took to validate or infer, and how many nodes were processed.


### Example Usage

```python
import shifty

# Run inference and retrieve the extended graph:
result = shifty.infer(data, rules)
g = result.graph()           # rdflib.Graph with original + inferred triples

# both 'validate' and 'validate_algebra' run inference first, so you can 
# just provide the original data graph and the rules graph

# validate with a pyshacl-compatible API
conforms, report_graph, results_text = shifty.validate(data, shapes)

# validate and get the algebraic (structural) report
result = shifty.validate_algebra(data, shapes)
for violation in result.violations():
    print(violation.focus_node, violation.shape)
    print(violation.explanation())   # structured tree, not just a string
```

### How Fast is Shifty?

Shifty *roughly* an order of magnitude faster than TopQuadrant's SHACL implementation, and two orders of magnitude faster than pySHACL on the Brick and 223P benchmarks.

The results below are from a simple benchmark that runs inference and then validation on a number of Brick and 223P graphs, and compares the time taken by shifty, TopQuadrant's SHACL implementation, and pySHACL.
The engines were each given the full "imports closure" of the Brick and 223P ontologies, and the time taken to load the ontologies is included in the benchmark results.
I gave all engines a 10 minute timeout (500 seconds), and any engine that took longer than 5 minutes was terminated and marked as "—" in the results below.
The times recorded are the best of 5 runs.

| Ontology | Model | Triples | pyshifty (s) | TopQuadrant (s) | pySHACL (s) | pyshifty vs TQ | pyshifty vs pySHACL |
|---|---:|---:|---:|---:|---:|---:|---:|
| brick | bldg24.ttl | 16 | 4.54 | 43.49 | 130.05 | 9.6x | 28.7x |
| brick | bldg31.ttl | 31 | 4.58 | 52.67 | 131.57 | 11.5x | 28.7x |
| brick | bldg16.ttl | 90 | 4.59 | 44.83 | 132.73 | 9.8x | 28.9x |
| brick | bldg25.ttl | 113 | 4.68 | 44.93 | 132.88 | 9.6x | 28.4x |
| brick | bldg19.ttl | 304 | 4.73 | 45.05 | 135.21 | 9.5x | 28.6x |
| brick | bldg4.ttl | 928 | 5.41 | 56.64 | 145.60 | 10.5x | 26.9x |
| brick | bldg8.ttl | 1000 | 5.40 | 46.55 | 147.12 | 8.6x | 27.2x |
| brick | bldg30.ttl | 2924 | 5.22 | 53.17 | 180.57 | 10.2x | 34.6x |
| brick | bldg11.ttl | 8608 | 21.77 | 90.29 | 292.64 | 4.1x | 13.4x |
| brick | bldg37.ttl | 10962 | 27.81 | 85.48 | 342.91 | 3.1x | 12.3x |
| s223 | guideline36-2021-A-1.ttl | 102 | 1.38 | 35.51 | 100.36 | 25.6x | 72.5x |
| s223 | guideline36-2021-A-4.ttl | 257 | 1.41 | 35.91 | — | 25.5x | — |
| s223 | NIST-HPL.ttl | 829 | 1.45 | 36.76 | 120.99 | 25.3x | 83.4x |
| s223 | guideline36-2021-A-9.ttl | 1060 | 1.55 | 36.90 | — | 23.7x | — |
| s223 | lbnl-example-radiant.ttl | 1709 | 1.47 | 22.84 | 162.64 | 15.5x | 110.5x |
| s223 | nrel-example.ttl | 8130 | 2.54 | 42.29 | — | 16.7x | — |
| s223 | lbnl-bdg4-1.ttl | 10568 | 2.42 | 45.23 | — | 18.7x | — |
| s223 | lbnl-bdg3-1.ttl | 26571 | 2.94 | 24.76 | — | 8.4x | — |
| s223 | pnnl-bdg2-1.ttl | 34810 | 4.55 | 99.47 | — | 21.9x | — |

{{< figure width="100%" src="/posts/SHACL/img/inference_plus_validation.png" alt="Inference + Validation Time">}}

<details>
<summary>Benchmarking scripts and setup</summary>

All the benchmarking scripts are [here](https://github.com/gtfierro/shifty/tree/main/benchmark/performance_comparison)

With a file called `selected-models.csv`:
```
suite,model,triples
brick,bldg24.ttl,16
brick,bldg31.ttl,31
brick,bldg16.ttl,90
brick,bldg25.ttl,113
brick,bldg19.ttl,304
brick,bldg4.ttl,928
brick,bldg8.ttl,1000
brick,bldg30.ttl,2924
brick,bldg11.ttl,8608
brick,bldg37.ttl,10962
s223,guideline36-2021-A-1.ttl,102
s223,guideline36-2021-A-4.ttl,257
s223,NIST-HPL.ttl,829
s223,guideline36-2021-A-9.ttl,1060
s223,lbnl-example-radiant.ttl,1709
s223,nrel-example.ttl,8130
s223,lbnl-bdg4-1.ttl,10568
s223,lbnl-bdg3-1.ttl,26571
s223,pnnl-bdg2-1.ttl,34810
s223,lazlo_sdh_223p_anon.ttl,144226
```

You can run the benchmark with:

```bash
uv run benchmark/performance_comparison/compare_engines.py --model-manifest selected_models.csv --runs 1 --keep-going --run-timeout-seconds 300
```

This will output the plot above, as well as a CSV file with the raw results.
</details>

### Why is Shifty Fast?

This is also a much longer question which I hope to write up in a paper soon, but the short answer is that shifty uses an algebraic representation of SHACL shapes and paths, which allows for a number of optimizations to be applied before any data is read.
The algebraic representation is based on the **extremely helpful** work of Ahmetaj et al. (2026){{< sn >}}Ahmetaj, S., Boneva, I., Hidders, J., Jakubowski, M., Labra-Gayo, J. E., Martens, W., Mogavero, F., Murlak, F., Okulmus, C., Savković, O., Šimkus, M., & Tomaszuk, D. (2026). Common Foundations for Recursive Shape Languages. *arXiv preprint arXiv:2604.20946*. [https://arxiv.org/abs/2604.20946](https://arxiv.org/abs/2604.20946){{< /sn >}}, which provides a formal semantics for SHACL.

Paths are a Kleene algebra with converse:
```
π ::= id | q | π⁻ | π · π′ | π ∪ π′ | π*
```
`id` is the focus node itself, `q` is a single predicate step, `⁻` is inverse traversal, `·` is sequential composition, `∪` is alternation, and `*` is transitive closure. `sh:sequencePath`, `sh:alternativePath`, and `sh:zeroOrMorePath` map directly to these operators. `sh:oneOrMorePath` and `sh:zeroOrOnePath` are just notation.
`sh:oneOrMorePath` is `π⁺ = π · π*` and `sh:zeroOrOnePath` is `π? = π ∪ id`; both are normalized away at parse time.

Shapes are constraints over focus nodes:
```
φ ::= ⊤ | test(τ) | ¬φ | φ ∧ φ′ | φ ∨ φ′ | ∃≥ⁿ π.φ | ∃≤ⁿ π.φ
```

**The key insight is how many SHACL vocabulary terms reduce to a single operator here**.
As an example, these constraint operators all involve counting: `sh:minCount`, `sh:maxCount`, `sh:qualifiedValueShape`, `sh:qualifiedMinCount`, `sh:qualifiedMaxCount`, `sh:node`, `sh:property`.
This means we can express them as `∃≥ⁿ` or `∃≤ⁿ` applied to some path and some (optional) qualifying shape.

Because everything is a term in this algebra, the normalizer can apply algebraic laws before touching any data.
Here are a few of the features that are enabled by this algebraic representation:
- **Count merging**: Two bounds on the same path in a conjunction merge into one range. `∃≥3 ex:knows.⊤ ∧ ∃≤10 ex:knows.⊤` becomes `∃[3..10] ex:knows.⊤`; this uses one path traversal instead of two. Contradictory bounds like `sh:minCount 5` combined with `sh:maxCount 2` reduce to ⊥ (FALSE), meaning every targeted node statically fails without reading any data.
- **Boolean simplification**: `¬¬φ = φ`, `φ ∧ ⊤ = φ`, `φ ∧ ⊥ = ⊥`, `φ ∧ ¬φ = ⊥`, and so on. Double-negation removal comes up more than you'd expect because of nested shapes.
- **Value-type intersection**: `sh:datatype xsd:string` combined with `sh:minInclusive 0` reduces statically to ⊥ (FALSE) because a string can never satisfy a numeric range constraint. This is only detectable because datatypes and range bounds are both represented as intersectable `test(τ)` terms.
- **Hash-consing / common subexpression elimination (CSE)**: Structurally identical sub-shapes across the whole schema get deduplicated to a single node in the shape arena. If ten shapes all require `∃≥1 rdf:type.⊤` (and in Brick and 223P, essentially all of them do) that constraint gets evaluated once per focus node with the result shared everywhere.

The `shifty inspect` CLI exposes each stage:
```sh
$ shifty inspect --stage algebra shapes.ttl    # post-parse IR
$ shifty inspect --stage normalized shapes.ttl # after simplification
```

### Improved Validation Reporting

Recall that the W3C SHACL report terminates at aggregate components: if an `sh:or` fails, you get a result that says the `sh:or` failed at this node, and no information about which branch failed or why.
This is annoying, but it's a real limitation when you want to use validation results downstream: explaining failures to a building operator, driving a repair process, generating a human-readable summary of what needs to be fixed, etc.

Because shifty evaluates by structural recursion over the shape algebra, it produces a report that mirrors the grammar. Here's our example from before:

```turtle
brick:TemperatureSensorShape a sh:NodeShape ;
    sh:targetClass brick:Temperature_Sensor ;
    sh:or (
        [ sh:property [ sh:path brick:hasUnit ; sh:hasValue unit:DEG_F ] ]
        [ sh:property [ sh:path brick:hasUnit ; sh:hasValue unit:DEG_C ] ]
    ) .
```

A sensor with no `brick:hasUnit`:
```
ex:TemperatureSensor1  fails  brick:TemperatureSensorShape
  or: both branches failed
    branch 0 (∃≥1 brick:hasUnit.test(unit:DEG_F)): 0 values found
    branch 1 (∃≥1 brick:hasUnit.test(unit:DEG_C)): 0 values found
```

There's a lot more to say about shifty, which I won't cover in this post:
- **Recursion and stratification**: SHACL shapes can reference each other cyclically, and the W3C spec is silent on what that means. Shifty pins specific semantics (greatest fixpoint for validation, least fixpoint for inference) based on work by Corman et al.{{< sn >}}Corman, J., Reutter, J. L., & Savković, O. (2018). Semantics and Validation of Recursive SHACL. In *The Semantic Web – ISWC 2018*. [https://doi.org/10.1007/978-3-030-00671-6_19](https://doi.org/10.1007/978-3-030-00671-6_19){{< /sn >}} and Andresel et al.{{< sn >}}Andresel, M., Corman, J., Ortiz, M., Reutter, J. L., Savković, O., & Simkus, M. (2020). Stable Model Semantics for Recursive SHACL. In *Proceedings of The Web Conference 2020* (pp. 1570–1580). [https://doi.org/10.1145/3366423.3380229](https://doi.org/10.1145/3366423.3380229){{< /sn >}}, with explicit error diagnostics for schemas those semantics can't handle.
- **SPARQL lowering**: SHACL's `sh:sparql` constraints can be compiled to a native plan over an immutable, multiply-indexed dataset, with Oxigraph as a fallback for full SPARQL 1.1. This gives **significant** speedups over existing SHACL implementations, which typically use a SPARQL engine to evaluate each `sh:sparql` constraint in isolation.
- **Profiling**: Per-shape and per-query telemetry, accessible via the Python API or the CLI. On the 223P/NIST benchmark, profiling is what revealed where time was actually going, and eventually motivated the native SPARQL work.
- **Symbolic repair**: A library API that computes the full space of possible repairs for a validation failure.

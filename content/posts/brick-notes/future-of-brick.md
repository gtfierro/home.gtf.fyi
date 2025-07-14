---
title: "The Future of Brick is SHACL"
date: 2021-07-27T00:00:00Z
categories: ['Brick', 'SHACL', 'Ontology Design']
type: post
draft: true
---


# The Future of Brick is SHACL

[Brick](https://brickschema.org) is an open-source, permissively-licensed ontology which describes physical, logical and virtual assets in buildings, the data about them, and the relationships between them.
Brick enables the discovery, extraction and analysis of data in buildings in a *standard manner* across vendor silos and building subsystems.
This kind of *semantic interoperability* is essential for many existing and future uses of data in the built environment.{{< sn >}}Bergmann, H., Mosiman, C., Saha, A., Haile, S., Livingood, W., Bushby, S., Fierro, G., Bender, J., Poplawski, M., Granderson, J. and Pritoni, M., 2020. **Semantic Interoperability to Enable Smart, Grid-Interactive Efficient Buildings**. Lawrence Berkeley National Lab.(LBNL), Berkeley, CA (United States).{{< /sn >}}

This post critically examines the current implementation of Brick, which is based on the OWL 2 RL ontology language, and discusses how this implementation has succeeded and --- importantly --- failed.
These failures can be summarized as follows:

1. The *open world assumption* is inappropriate for the characteristics of cyberphysical systems
3. Emerging use cases for Brick are focused more around constraints than they are around inferring information
2. OWL 2 RL can only express and detect a limited variety of validation conditions
4. OWL 2 RL is limited in what kinds of information it can generate or infer

Before digging into the above issues, it is important to refresh our understanding of the RDF data model and the OWL 2 family of ontology languages.

## RDF Data Model

The RDF data model is a specification of a directed, labeled graph that represents entities, resources, their properties and the relationships between them.
This is an extraordinarily flexible data model that is capable of expressing many different representations of information.
An RDF graph is expressed as a set of *triples*.{{< sn >}}<img src="/img/triple.png"></img>An RDF triple represents a relationship (or predicate) between two resources.This is a fundamental structure whose components are referred to as *subject*, *predicate* and *object*.{{< /sn >}}

One distinct advantage of the RDF data model is that the semantics of the expressed data can be encoded in an *ontology*.
An *ontology* is a set of rules and axioms which capture what kinds of information can be represented and derived from a set of statements.
It is essentially a programmatic specification of the semantics, or *meaning*, of data.

Below is an example of an RDF graph.
The "instance" nodes represent entities that are being described by the model; they may correspond to physical assets or data sources.
There are two edges between the instance nodes, each labeled `brick:feeds`{{< sn >}}Borrowed from Brick; definition [here](https://brickschema.org/ontology/1.2/relationships/feeds){{< /sn >}}; the exact meaning of this relationship is unimportant for this discussion.
The "ontology" nodes represent concepts (*classes*) that have a formal definition in the ontology.
The `rdfs:subClassOf` relationships between the concept nodes specifies which concepts are more general or specific than others{{< sn >}}We will formalize the notion of "class" and "subclass" below.{{< /sn >}}.

{{< figure width="70%" src="/img/pre-reason.png" alt="Model pre-reasoning">}}

The distinction between the "instance" and "ontology" portions of the graph are referred to, in the context of OWL, as the *terminological box* (*TBox*) and *assertional box* (*ABox*) respectively.
The TBox

Ontologies are expressed in *ontology languages*.
An ontology language permits the formal definition of meaning.
The choice of an ontology language determines what information can be captured in a graph and what can be *computationally inferred* from the contents of a graph and the axioms and rules contained within an ontology.

Below, we will delve into the OWL 2 family of ontology languages, cover the

## OWL 2 RL Semantics

OWL 2 is a family of ontology languages{{< sn >}}https://www.w3.org/TR/owl2-primer/ contains a much more complete description of OWL 2{{< /sn >}} defined by the W3C.

- ontology language based on a description logic
- flexible tradeoffs between expressiveness and decidability
- focus on OWL 2 RL (datalog-based)

The OWL 2 RL ontology language is formalized as a set of rules which define (a) what information can be inferred about a graph, given the statements within the graph, and (b) what information can be validated or checked.
In OWL 2 RL, these rules can be expressed as Datalog rules.
The set of rules is larger than I have time to discuss here {{< sn >}}https://www.w3.org/TR/owl2-profiles/#Reasoning_in_OWL_2_RL_and_RDF_Graphs_using_Rules{{< /sn >}}, but there are a few that are illustrative.
The following rule defines the set-based formalism of subclasses and types:

```prolog

T(?x, "rdf:type", ?c2) :- T(?c1, "rdfs:subClassOf", ?c2), T(?x, "rdf:type", ?c1) .
```

The rule is of the traditional Datalog form.
One detail relevant to the Datalog formalization of OWL 2 RL is there is only one relation, `T`{{< sn >}}My [dissertation](https://gtf.fyi/papers/fierro-dissertation.pdf) discusses more efficient transformations of OWL 2 RL rules. See Chapter 7.{{< /sn >}}, which contains all triples in an RDF graph.
It is important to reiterate that the RDF graph must contain the "instance" triples (for example, the Brick model of a building) as well as the "ontology" triples (for example, the Brick ontology).

The *body* of the rule --- to the right of the `:-` --- is true if there are triples that fulfill the conjunctive predicate given.
in the example above, the body is true if there is an entity `?c1` which has an `rdfs:subClassOf` relationship to an entity `?c2`, and there is an entity `?x` which has an `rdf:type` relationship to the `?c1` entity.{{< sn >}}I'm borrowing the SPARQL variable style here with the `?` prefix; usually, variables in Datalog are written with a capital letter.{{< /sn >}}

The *head* of the rule --- to the left of the `:-` --- is true if the body of the rule is true.
When a head is true, it can be considered part of the graph.
This means that head produces a triple for each binding of variables given by the body of the rule.
These "inferred" triples are often materialized into the graph to facilitate query answering, but there are ways around this.

Consider the graph from above, with new edges added according to the rule we have just discussed

{{< figure width="75%" src="/img/post-type-reason.png" alt="Model post-reasoning for subclass rule">}}

The graph now explicitly associates each of the "instance" nodes with its immediate types (as in the original graph) *as well as* all of the types which are supertypes of its immediate types, and the supertypes of *those* types, and so on.

While there are many OWL 2 inference rules, there are serveral critical rules that Brick uses in its implementation{{< sn >}}Fierro, G., Koh, J., Agarwal, Y., Gupta, R. K., & Culler, D. E. (2019, November). **Beyond a house of sticks: Formalizing metadata tags with brick**. In Proceedings of the 6th ACM International Conference on Systems for Energy-Efficient Buildings, Cities, and Transportation (pp. 125-134).{{< /sn >}}.
I'll discuss each of the salient semantic features of Brick and how they are enabled by OWL 2 RL.
Later, we'll investigate how many of these features are actually needed (not that they are useless --- they aren't! But they don't always do exactly what we'd like them to).

#### Classes and Subclasses

```prolog

% cax-sco
T(?x, "rdf:type", ?c2) :- T(?c1, "rdfs:subClassOf", ?c2), T(?x, "rdf:type", ?c1) .
```

The Datalog rule from above makes the implied types of all entities in the Brick model explicit.
Given a class hierarchy such as the Brick `Point` hierarchy{{< sn >}}<img src="/img/point-hierarchy.png"></img>{{< /sn >}}, this means that all instances of `brick:Air_Temperature_Sensor` will also be instances of `brick:Temperature_Sensor`, `brick:Sensor` and `brick:Point`.

This type information can be explicitly queried as well when it is materialized as part of the RDF graph.
Consider the following Turtle-encoded RDF model:

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <urn:ex#> .

brick:Point a owl:Class .
brick:Sensor a owl:Class ;
    rdfs:subClassOf brick:Point .
brick:Temperature_Sensor a owl:Class ;
    rdfs:subClassOf brick:Sensor .
brick:Air_Temperature_Sensor a owl:Class ;
    rdfs:subClassOf brick:Temperature_Sensor .
:x a brick:Air_Temperature_Sensor .
```

After applying the rule above, the model now looks like:

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <urn:ex#> .

brick:Point a owl:Class .
brick:Sensor a owl:Class ;
    rdfs:subClassOf brick:Point .
brick:Temperature_Sensor a owl:Class ;
    rdfs:subClassOf brick:Sensor .
brick:Air_Temperature_Sensor a owl:Class ;
    rdfs:subClassOf brick:Temperature_Sensor .

:x a brick:Air_Temperature_Sensor, brick:Temperature_Sensor,
    brick:Sensor, brick:Point .
```

A query for the type of the `urn:ex#x` entity on the post-reasoning model will return all of the indicated types.
As we will see later, returning *all* of the inferred types can present a challenge for some software, which must sift through the collection of types in order to determine the most "specific" type associated with a given entity.

#### Domains and Ranges

```prolog

% prp-dom
T(?x, "rdf:type", ?c) :- T(?p, "rdfs:domain", ?c), T(?x, ?p, ?y) .

% prp-rng
T(?y, "rdf:type", ?c) :- T(?p, "rdfs:range", ?c), T(?x, ?p, ?y) .
```

These two rules infer the type of an entity based on its inclusion as the subject or object of a property.
An `rdfs:domain` annotation on a property implies that any subject entity of that property is of the given type; the `rdfs:range` annotation implies the same but for the object of a property.
It is important to note that `rdfs:domain` and `rdfs:range` are *not* constraints; they generate new information rather than validating existing information.
Validating the type of an entity must be done through other means.

For an example, consider the following RDF graph

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <urn:ex#> .

brick:isPointOf a owl:ObjectProperty ;
    rdfs:domain brick:Point .
brick:hasPoint a owl:ObjectProperty ;
    rdfs:range brick:Point .

:x brick:hasPoint :y .
:a brick:isPointOf :b .
```

Per the two rules above, the types of `urn:ex#y` and `urn:ex#a` can be inferred.

* `prp-dom`: because `urn:ex#a` is the subject of `brick:isPointOf`, it must be a `brick:Point`
* `prp-rng`: because `urn:ex#y` is the object of `brick:hasPoint`, it must be a `brick:Point`

#### Value / Class Inference

```prolog

% cls-hv1
T(?u, ?p, ?y) :- T(?x, "owl:hasValue", ?y), T(?x, "owl:onProperty", ?p), T(?u, "rdf:type", ?x) .

% cls-hv2
T(?u, "rdf:type", ?x) :- T(?x, "owl:hasValue", ?y), T(?x, "owl:onProperty", ?p), T(?u, ?p, ?y) .
```

The two Datalog rules above perform complimentary operations.
The first, `cls-hv1`, encodes "inheritance" of a property and value associated with a class to all instances of that class.
The second, `cls-hv2`, infers the type of an entity if it has a specific value for a specific property.

Consider the following RDF graph as an example:

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <urn:ex#> .

brick:Point a owl:Class ;
    owl:hasValue "point" ;
    owl:onProperty brick:hasTag .

:x a brick:Point .
:y brick:hasTag "point" .
```

After applying the `cls-hv2` rule, `urn:ex#x` will "inherit" the `"point"` tag because it is an instance of `brick:Point`.
`urn:ex#y` will be inferred to be an instance of `brick:Point` *because* it has the `"point"` tag associated with it.

Although useful, a significant limitation of these rules is that they can only associate a single property name and value with each class.
In a scenario with more than one `owl:hasValue`/`owl:onProperty` pairing for a class, there is no way for OWL to tell which value is associated with which property.
Using only the rules above, all combinations of properties and values will be inferred for instances of the class.
See the example below:

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <urn:ex#> .

# the WRONG way to talk about conjunctions of properties and values
brick:Sensor a owl:Class ;
    owl:hasValue "point" ;
    owl:onProperty brick:hasTag ;
    owl:hasValue  "true"^^xsd:boolean ;
    owl:onProperty brick:measuresThings ;

:x a brick:Sensor .
# inferred...
:x brick:hasTag "true"^^xsd:boolean, "point" ;
   brick:measuresThings "true"^^xsd:boolean, "point" .
```

Obviously, this is not what we want.
The upshot of this is that another mechanism must be used to encode that (a) a class can be inferred from the *conjunction* of several properties and values and (b) a class can inherit multiple properties and values.

Luckily, OWL 2 RL provides one such mechanism: *intersections*.
The relevant semantics of intersections are given by the Datalog rule below.{{< sn >}}This rule uses some odd syntax. The `LIST[...]` construction is an [RDF list](https://www.w3.org/TR/rdf-schema/#ch_list) of classes that is named `?x`.{{< /sn >}}

```prolog

% cls-int1
T(?y, "rdf:type", ?c) :- T(?c, "owl:intersectionOf", ?x), LIST[?x, ?c1, ..., ?cn],
                   T(?y, "rdf:type", ?c1), T(?y, "rdf:type", ?c2), ..., T(?y, "rdf:type", ?cn) .

% cls-int2
T(?y, "rdf:type", ?c1), ... T(?y, "rdf:type", ?cn) :- T(?c, "owl:intersectionOf", ?x),
        LIST[?x, ?c1, ..., ?cn], T(?y, "rdf:type", ?c) .
```

The `cls-int1` rule asserts that if an entity `?y` is an instance of all *n* classes (`?c1` through `?cn`), then it is also an instance of class `?c`.
These semantics allow us to encode the inference of a class from a conjunction of properties:

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <urn:ex#> .

brick:Sensor a owl:Class ;
    owl:intersectionOf ( # everything in the parentheses is a member of the list
        [ # these square brackets denote an "anonymous" class with the hasValue/onProperty annotations
            owl:hasValue "point" ;
            owl:onProperty brick:hasTag
        ],
        [
            owl:hasValue "true"^^xsd:boolean ;
            owl:onProperty brick:measuresThings
        ]
    ) .

:x a brick:Sensor .
:y brick:hasTag "point" ;
   brick:measuresThings "true"^^xsd:boolean .
```

Per `cls-int1`, `urn:ex#y` is inferred to be an instance of `brick:Sensor` because it has both required properties.
Per `cls-int2`{{< sn >}}This rule performs the complement of `cls-int1`: if an entity is an instance of the main class `?c`, then it will also be an instance of all classes whose intersection is equivalent to that class.{{< /sn >}}, `urn:ex#x` is inferred to be an instance of each of the classes which compose the intersection annotation; then, via `cls-hv2` above, `urn:ex#x` inherits the properties associated with each of those classes.
The end result is this model:

```turtle
:x a brick:Sensor ;
   brick:hasTag "point" ;
   brick:measuresThings "true"^^xsd:boolean .

:y a brick:Sensor ;
   brick:hasTag "point" ;
   brick:measuresThings "true"^^xsd:boolean .
```

Brick uses these features to encode an equivalence between a class and a set of properties or tags.
However, there is still a major hole: negation!
It is impossible, within these sets of rules, to encode a condition that an entity must *not* have a certain property, or even a certain value on a certain property.
This is intrinsically linked to the *open-world assumption*; we will review this assumption in the context of other OWL 2 issues below.

## Issue with OWL (2 RL): The Open World Assumption

The first major issue with OWL 2 RL is how it handles missing information.
OWL, and most semantic web and linked data technologies, are based on what is called the *open world assumption* (OWA).
It is helpful to understand OWA by first understanding the *closed world assumption* (CWA).
Both are philosophies for how to treat the absence of information in a database.{{< sn >}}In this context, the RDF graph is our database{{< /sn >}}

CWA is the default interpretation of missing information for traditional databases: it treats missing information as false.
This is intuitive for many business use cases, where the database is considered to be a comprehensive source of information.
Consider a database of products being sold by a vendor and a query for a particular product which returns no results on the database.
Under CWA, the interpretation of the lack of results is that there is no available product by that name.
Another way to put this is *if a statement is true, then the truthfulness of the statement is captured in the database*.

The compliment to CWA is OWA.
OWA asserts that the truthfulness of statements that are *not* in the database cannot be known.
Under OWA, the only interpretation of null results for our product query above is that the database only knows that it does not know whether that product is available.
CWA makes sense for scenarios in which the database is the point of truth; however, linked data technologies were designed for the web, where there is no single point of truth or authoritative source of all information.
If data is not found in the web, it is not necessarily false --- it simply may not have been written down or linked to.{{< sn >}}Intuitively, this can make sense in our daily experience. When performing a web search for information, we typically interpret a lack of relevant results as an indication that we must refine our query or we are using the wrong terms, not that our query is invalid or false.{{< /sn >}}
This also conveniently allows OWL 2 RL to sidestep the complexities of negation in the rule-based context by requiring that all inference is dependent upon information that is present in the RDF graph, rather than information that is not.

Is the open world assumption appropriate for cyberphysical use cases?
I argue that it is not.
In cyberphysical settings, there is no "web of knowledge" that is waiting to be referenced or linked to; instead, the digital records produced and maintained about cyberphysical systems are designed and intended to be comprehensive references.
In fact, the value of these digital records is dependent on some notion of completeness: asset management software tracks all assets that have been installed or commissioned for a system; building information models contain architectural information for all constructed elements of a building; timeseries databases contain the metadata and telemetry for all sensors and data streams in a deployment.
Software for cyberphysical systems must be able to make use of what is known to exist as well as what is known to not exist within a particular environment.
OWA makes it difficult to effectively reason about the latter.

## CPS Design Patterns and OWA

There are several ontology design patterns useful for modeling CPS that are impeded by OWA.
Each of these fundamentally depends on being able to express some sort of negation over the contents of the RDF graph.

### Mutually Exclusive Information

It can be helpful to model certain attributes or properties as being mutually exclusive:
- a sensor may not measure both air and water at the same time
- entities may not be an instance of both an Equipment and a Location class
- etc.

We can approximate those semantics in OWL 2 RL in one of two ways, using OWL classes to define groups of entities which have the desired properties.

1. We can use the `owl:disjointWith` property to define two classes as being disjoint. If an entity is a member of two disjoing classes, then OWL inference will complain.
2. We can use `owl:complementOf` to define one class as the complement of another; any entity which is a member of both classes will cause OWL inference to complain.

These two rules are semantically different, but their implementation in OWL 2 RL's rules is limited to noticing logical inconsistencies rather than actually inferring information.

```prolog

% cax-dw
T(?x "rdf:type", "owl:Nothing") :- T(?c1, "owl:disjointWith", ?c2), T(?x, "rdf:type", ?c1), T(?x, "rdf:type", ?c2) .

% cls-com
T(?x "rdf:type", "owl:Nothing") :- T(?c1, "owl:complementOf", ?c2), T(?x, "rdf:type", ?c1), T(?x, "rdf:type", ?c2) .
```

As a short example, here is an example of how one might model that Sensor instances can measure either water or air, but not both

```ttl
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <urn:ex#> .

brick:Point a owl:Class .

brick:Sensor a owl:Class ;
    rdfs:subClassOf brick:Point .
    
brick:SensorMeasuresAir a owl:Restriction ;
    owl:hasValue "air" ;
    owl:onProperty brick:hasSubstance ;
    owl:disjointWith brick:SensorMeasuresWater ;
    rdfs:subClassOf brick:Sensor .
.

brick:SensorMeasuresWater a owl:Restriction ;
    owl:hasValue "water" ;
    owl:onProperty brick:hasSubstance ;
    owl:disjointWith brick:SensorMeasuresAir ;
    rdfs:subClassOf brick:Sensor .
.

:sen1 a brick:Sensor ;
      brick:hasSubstance "water", "air" .
# this will be tagged as an instance of owl:Nothing by the inference process,
# indicating that it is involved in a logical inconsistency
```

OWL 2 RL's implementation of mutually exclusive information leaves something to be desired.
We would like to be able to more directly express what properties are mutually exclusive, and to have more detailed and explicit feedback if those constraints are violated.

```ttl
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <urn:ex#> .

brick:Point a owl:Class .

brick:Sensor a owl:Class, sh:NodeShape ;
    rdfs:subClassOf brick:Point ;
    sh:property [
        sh:path brick:hasSubstance ;
        etc..
    ] ;
.
    
brick:SensorMeasuresAir a owl:Restriction ;
    owl:hasValue "air" ;
    owl:onProperty brick:hasSubstance ;
    owl:disjointWith brick:SensorMeasuresWater ;
    rdfs:subClassOf brick:Sensor .
.

brick:SensorMeasuresWater a owl:Restriction ;
    owl:hasValue "water" ;
    owl:onProperty brick:hasSubstance ;
    owl:disjointWith brick:SensorMeasuresAir ;
    rdfs:subClassOf brick:Sensor .
.

:sen1 a brick:Sensor ;
      brick:hasSubstance "water", "air" .
# this will be tagged as an instance of owl:Nothing by the inference process,
# indicating that it is involved in a logical inconsistency
```

### Tag / Class Inference



- OWA:
    - hard to say "when X does *not* have property Y..."
    - tag issue (max air setpoint...)
- class types -- get most specific:
    - rdfs:subClassOf*
- what kind of validation errors can be detected:
    - failure cases in OWL 2 RL rules
- multiple domain/ranges:
    - owl gives intersection, but we really want union or something more specific

## SHACL

### Overview

### Advantages

### Causes for hesitation

#### OWL 2 Features

- How to replicate OWL 2 features
- standard OWL shapes?

#### SHACL-AF Support

## The Future

### Application Shapes

- from analytics providers
- standard shapes for different standards
- have examples

### Equipment Shapes

- from manufacturers
- have examples

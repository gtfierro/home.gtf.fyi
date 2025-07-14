---
title: "Getting Started with Brick Research"
date: 2023-05-17T00:00:00Z
categories: ['Brick','Research']
type: post
---


*This whole document is in-progress -- be sure to check back!*

---

# Brick Research Reading List

So you want to do research on or with Brick -- great!
One common question I get or find myself answering is "what background do I need to get myself up to speed with using Brick at a level where I can do research?"
This post attempts to answer that question.

For high-level background, please read through [Chapter 2 of my PhD thesis](https://gtf.fyi/papers/fierro-dissertation.pdf) -- this is a decent overview of the information detailed below.

## Vision Papers

These are some high-level vision papers that can provide additional background and context into this work:

- [Semantic Interoperability to Enable Smart, Grid-Interactive Efficient Buildings](https://gtf.fyi/papers/semantic_interop.pdf) from Harry Bergmann at US DOE
- [Towards Digital and Performance-Based Supervisory HVAC Control Delivery](https://escholarship.org/uc/item/59z6d46m) from Dr. Amir Roth at US DOE

## RDF Background and Related Technologies

I would recommend reading through the W3C's "Primer" documents on the core linked-data technologies.
These are a little more technical than I would like for someone's introduction to the subject, but they are excellent references.

The best way to approach these is to read the first couple sections in full, and reserve the latter parts for future reference.

- [RDF Primer](https://www.w3.org/TR/rdf11-primer/): explains the RDF data model and its components
- [Turtle](https://www.w3.org/TR/turtle/) is a common serialization format for RDF graphs (the Brick ontology is [distributed as Turtle files](https://github.com/BrickSchema/Brick/releases); this document can provide some clarity to reading these files as a human, but most tools will parse them without any issues
- [SPARQL Primer](https://www.w3.org/TR/sparql11-overview/): explains the SPARQL query language, the predominant and standard language for querying and manipulating RDF graphs
- [SPARQL Query Primer](https://www.w3.org/TR/sparql11-query/): focuses on explaining *reading* RDF graphs; this is the most common flavor of SPARQL query used with Brick
- [SHACL](https://www.w3.org/TR/shacl/): this is the constraint language which describes constraints, requirements, conditions and other schematic and semantic constructs for an ontology. Brick is implemented in SHACL rather than older traditional ontology languages like OWL. Brick also makes use of [SHACL-AF](https://www.w3.org/TR/shacl-af/), which includes advanced features like rules.

### Shapes Constraint Language Resources

As SHACL becomes a more integral part of semantic metadata solutions for Buildings, it will become increasingly important to develop expertise in this language. Here are some additional
resources for getting up-to-date on SHACL:

- [Validation RDF book](http://book.validatingrdf.com)
- [Comparison of SHACL and OWL](https://spinrdf.org/shacl-and-owl.html)
- [Data Shapes website](https://datashapes.org)
- of course, do not forget the [SHACL specification](https://www.w3.org/TR/shacl/) and the [SHACL Advanced specification](https://www.w3.org/TR/shacl-af/)

## Buildings Background

I am still struggling to find a good resource for bootstrapping an understanding of building subsystems.
Some resources to check out:

- ASHRAE Guideline 36{{< sn >}}Technically you need to buy a copy of this from ASHRAE, but you can find some online copies with some careful Googling{{< /sn >}}: contains helpful figures and descriptions of typical forced air HVAC systems, control sequences, and fault detection rules
- [APAR Rules](https://doi.org/10.1016/j.enbuild.2006.04.014): data-driven fault detection rules for air handler units

## Ontology Design and Implementation

These are papers about Brick, extensions to Brick, or related ontologies:

- [Original Brick paper](https://gtf.fyi/papers/brick2016balaji.pdf) (BuildSys 2016): describes the original vision and implementation; many of the property names have changed since
- [Brick and Tag-based metadata](https://gtf.fyi/papers/house2020fierro.pdf) (FrontiersIn 2020): describes how Brick metadata is compatible with tag-based metadata schemes
- [Occupancy Datasets and Brick](https://gtf.fyi/papers/extending2022luo.pdf) (Automation in Construction 2022): extends Brick with concepts for occupancy modeling and describing occupancy datasets

## Brick Applications

These are papers about applying Brick to data-driven analytics, and other applications

- [Mortar](https://gtf.fyi/papers/mortar2020fierro.pdf) (ACM Transactions on Sensor Networks 2019): large dataset of buildings and Brick models, enabling portable analytics
- [Thermal comfort application](https://gtf.fyi/papers/enabling2022sun.pdf) (ASHRAE 2022): example of Brick being used to perform thermal comfort analysis
- [Simulated Digital Twins](https://gtf.fyi/papers/fierro2022simulated.pdf) (BuildSys 22): using Brick with BOPtest, Modelica and BACnet to present a physically realistic simulation abstracted behind a Brick model and a virtual BACnet network

## Constructing Semantic Metadata Models

- [BuildingMOTIF and Semantic Sufficiency](https://gtf.fyi/papers/fierro2022application.pdf): defines the important *semantic sufficiency* concept and defines some methods for automated construction and verification of RDF models
- [Dr. Bhattacharya's work](https://cseweb.ucsd.edu/~dehong/pdf/buildsys15-paper2.pdf) on active learning applied to BMS label parsing predates Brick, but still outlines many of the challenges involved
- [Dr. Koh's work](https://dl.acm.org/doi/abs/10.1145/3276774.3276795) explores application of classic NLP techniques to tokenizing BMS labels and closes the loop by producing Brick metadata as a result
- [This Brick docs page](https://docs.brickschema.org/lifecycle/creation.html)  lists a few techniques and provides a link to a helpful video demonstrating the use of [OpenRefine](https://openrefine.org) for parsing BMS labels

## Data Systems and Programming

- [Mortar](https://gtf.fyi/papers/mortar2020fierro.pdf) (ACM Transactions on Sensor Networks 2019): large dataset of buildings and Brick models, enabling portable analytics
- [HodDB](https://gtf.fyi/papers/hoddb2017fierro.pdf): (BuildSys 17) SPARQL database specialized for Brick workloads
- [Chapter 5](https://gtf.fyi/papers/fierro-dissertation.pdf) of my PhD thesis covers how self-adapting software might be expressed
- [Chapter 7](https://gtf.fyi/papers/fierro-dissertation.pdf) of my PhD thesis covers the design and implementation of data systems supporting inference/storage for Brick models

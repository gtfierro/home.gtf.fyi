---
title: "Projects"
date: 2021-06-12T12:13:19-07:00
---

## BuildingMOTIF

{{< figure width="60%" src="/buildingmotif.png" alt="BuildingMOTIF Workflow">}}

BuildingMOTIF is an open-source SDK for (1) verifying the compliance and validity of RDF models using ontologies like Brick, RealEstateCore, and ASHRAE 223; and (2) automating the creation of RDF models through incorporating application requirements into the authoring process.

* [GitHub](https://github.com/NREL/BuildingMOTIF)

<u>Papers</u>: [BuildSys 2022](/papers/fierro2022application.pdf)

## Brick

{{< figure width="60%" src="/brick-model-example.png" alt="Brick Model">}}

Brick is an open-source ontology which describes, defines and contextualizes data sources in and around buildings. Brick standardizes semantic description of **physical, virtual and logical** entities and assets and the **relationships between them**. Brick facilitates the implementation of *self-adapting* data-driven software --- software which can configure itself to operate in a particular setting --- by enabling that software to query its environment and discover relevant data sources.

* [Brick Website](https://brickschema.org)
* [GitHub](https://github.com/BrickSchema/Brick)

<u>Papers</u>: [BuildSys 2016](/papers/brick2016balaji.pdf) | [Applied Energy 2018](/papers/brick2018balaji.pdf) | [BuildSys 2019](/papers/house2019fierro.pdf) | [Frontiers 2020](/papers/house2020fierro.pdf)

---

## Mortar

{{< figure width="80%" src="/mortar.png"  alt="Mortar Platform" >}}

**Note: the Mortar dataset is now available on HuggingFace under two datasets:**
* [Building graphs](https://huggingface.co/datasets/gtfierro/mortargraphs)
* [Building timeseries](https://huggingface.co/datasets/gtfierro/mortar)

Mortar is an open platform for developing robust, reproducible building analytics against an open testbed of over 100 real buildings, each described with a Brick model. Mortar implements a declarative API enabling *self-adapting analytics* which can be written once and deployed over 10s or 100s of sites without changing a line of code or configuration. Mortar supports a library of [open analytics implementations](https://github.com/SoftwareDefinedBuildings/mortar-analytics) which demonstrate how Brick metadata can be used to author building analytics.

* [Mortar Website](https://mortardata.org)
* [GitHub](https://github.com/gtfierro/mortar)
* [Analytics Library](https://github.com/SoftwareDefinedBuildings/mortar-analytics)

<u>Papers</u>:  [BuildSys 2018](/papers/mortar2018fierro.pdf) | [TOSN 2020](/papers/mortar2020fierro.pdf)

---

## RDF and Semantic Web Tooling

I maintain a variety of semantic web tooling that strives to make ontology development and management easier, faster and more intuitive. These tools include:

- [ontoenv](https://github.com/gtfierro/ontoenv): a command-line utility and Python library for managing `owl:imports` statements and `owl:Ontology` definitions
- [reasonable](https://github.com/gtfierro/reasonable): a decently fast OWL2 RL reasoner, written in Rust, with Python bindings; the design of `reasonable` is described in Chapter 7 of my dissertation
- [brickschema](https://github.com/BrickSchema/py-brickschema): a Python library, built on RDFlib, which facilitates querying, management, inference of Brick models
- [WebSPARQL](https://github.com/gtfierro/rdf-ui): an online SPARQL query processor and result visualizer ([Online Demo](https://sparql.gtf.fyi/))


---

## eXtensible Building Operating System

{{< figure width="60%" src="/xbos.png" alt="XBOS Platform" >}}

XBOS (eXtensible Building Operating System) is an open-source large-scale distributed operating system for smart buildings. XBOS provides secure real-time monitoring and control capabilities over diverse hardware (including BMS, smart meters, EV chargers and IoT devices). XBOS utilizes Brick to enable the development of portable control applications

* [Github](https://github.com/gtfierro/xboswave)

<u>Papers</u>: [Tech Report 2015](/papers/EECS-2015-197.pdf) | [TOSN 2018](/papers/democratizing2018anderson.pdf) | [USENIX Security 2019](/papers/wave2019andersen.pdf) | [SmartGridComm 2020](https://ieeexplore.ieee.org/abstract/document/9303006/) 

---
title: "Deriving Views over RDF Graphs"
date: 2025-02-23T00:00:00Z
categories: ['223p','rdf']
type: post
---

*(the model is in the eye of the beholder)*

{{< announce >}}
[Part 2](/posts/223p/loops/eye-of-the-beholder-2) of this post explores how we can define loops in a knowledge graph and how we can derive different views of the same loop for different applications.
{{< /announce >}}

Ontologies are a formal representation of a *perspective* on a domain.
They are specific in what details they care about, and which details they don't.
This means that some ontologies are more appropriate for certain applications than others.
Correspondingly, knowledge graphs using such an ontology may be better suited to answer certain questions over others.
Some applications may require us to derive a *new perspective* on a particular knowledge graph.
It is convenient to think of this derivation as a "view" or "projection" of the underlying knowledge graph which abstracts away the unnecessary detail for a particular application.

Let's make this concrete.

### Example: 223P and Brick

The ontologies that I work with -- [Brick](https://brickschema.org) and [223P](https://open223.info) -- are both oriented towards modeling building assets, systems, and data during their operation.
223P models the pipes, wires, connections, composition of building assets (equipment, sensors) and their relationship to architectural space. This includes rigorous modeling of substances, flows (with direction!), and quantities within the building. The plan is for a 223P model to be created from the architectural documents as part of the building commissioning process, where this information is known and still up-to-date.

Here is a partial 223P model focusing on a supply air temperature sensor:
```ttl
@prefix bldg: <urn:ex/> .
@prefix s223: <http://data.ashrae.org/standard223#> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix qudtqk: <http://qudt.org/vocab/quantitykind/> .
@prefix unit: <http://qudt.org/vocab/unit/> .

bldg:damper a s223:Damper ;
    s223:cnx bldg:damper-out .

bldg:sensor a s223:Sensor ;
    s223:hasObservationLocation bldg:damper-out ;
    s223:hasPhysicalLocation bldg:damper ;
    s223:observes bldg:air-temp .

bldg:damper-out a s223:OutletConnectionPoint ;
    s223:cnx bldg:out-connection ;
    s223:hasMedium s223:Medium-Air ;
    s223:hasProperty bldg:air-temp .

bldg:air-temp a s223:QuantifiableObservableProperty,
    qudt:hasQuantityKind qudtqk:Temperature ;
    s223:hasAspect s223:Role-Supply ;
    qudt:hasUnit unit:DEG_C .
```

`bldg:air-temp` is a supply air temperature sensor, which observes the temperature of the air flowing out of a damper (`bldg:damper-out`).
However, it is not explicitly labeled as a "supply air temperature sensor" in the model -- this is an application-specific interpretation of the model.

Brick captures the I/O "points" in a building and how they relate to the major architectural, mechanical, electrical components. This involves some modeling of upstream/downstream relationships between components. A Brick model (a specific knowledge graph of a building) is a simplification of the corresponding 223P model:
A Brick model:
   - *includes* major equipment with significant components, *excluding* connection points and pipes and other details
   - *abstracts* explicit models of physical sensors and properties into *simple* I/O points that directly relate to data sources

Following our example, here is a partial Brick model focusing on the same supply air temperature sensor:

```ttl
@prefix bldg: <urn:ex/> .
@prefix s223: <http://data.ashrae.org/standard223#> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix qudtqk: <http://qudt.org/vocab/quantitykind/> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix brick: <https://brickschema.org/schema/Brick#> .

bldg:damper a s223:Damper ;
    brick:hasPoint bldg:air-temp .

bldg:air-temp a s223:QuantifiableObservableProperty,
                brick:Supply_Air_Temperature_Sensor ;
    qudt:hasQuantityKind qudtqk:Temperature ;
    s223:hasAspect s223:Role-Supply ;
    qudt:hasUnit unit:DEG_C .
```

The relationship between the damper and the sensor (the *digital* I/O point "sensor") is now a direct link (`brick:hasPoint`) and the sensor has an application-friendly type of "Supply_Air_Temperature_Sensor".
An illustration of this abstraction is below{{< sn >}}I am experimenting with using Claude to generate SVGs instead of me putting them together by hand{{< /sn >}}.


{{< figure width="70%" src="/img/2025-02-23-brick-223p-view.svg" alt="abstracting 223P models with Brick">}}

### Modeling Loops

Loops are a common pattern in building systems.
*Air loops* are a common example in HVAC systems: air is conditioned by a unit, distributed to various zones, and then returned to the unit where it can be mixed with fresh air and conditioned again.
Several types of *water loops* are also common in buildings: hot water loops circulate water between a boiler and various heating coils, chilled water loops circulate water between a chiller and various cooling coils, etc.

**How should we model these loops in a knowledge graph?**
We would like to define the loop using some process so that the loop information can be queried and analyzed.
We will approach this using the same "view" concept discussed above.

Starting with a 223P model gives us detailed information on all the components that make up a loop:
- equipment (e.g., boilers, chillers, air handlers)
- connections (e.g., pipes, ducts)
- connection points (e.g., inlets, outlets)
- junctions

Substances flow from an equipment outlet to a connection point, though a connection, and into an equipment inlet.
An equipment may have multiple inlets and outlets, and a connection point may have multiple connections.
Connection points within an equipment may be paired with one another to illustrate how substances flow through the equipment (this can be helpful for modeling the two sides of a heat exchanger, for example).

It seems like we have enough detail here to model loops, but how do we actually define the loop?
The nature of this definition depends on the application, but it also impacts the method we can use to define the loop.
Here are a few possible definitions of "loops" for different use cases:
- [this paper](https://www.sciencedirect.com/science/article/abs/pii/S0098135419313687) from Villez, Vanrolleghem and Corominas provides a method for computing Pareto-optimal placement of sensors for applications like mass balance. The method works on an directed graph where the nodes are unit processes and the edges are connections (e.g., pipes) between them. The method also introduces a global "Environment" node which captures the flow of substances into and out of the system.
- gbXML's [AirLoop](https://www.gbxml.org/schema_doc/7.03/GreenBuildingXML_Ver7.03.html#LinkF) only contains the list of equipment in the loop (e.g. AHU and VAV for an air loop, or VAV and Boiler for a hydronic heating loop). The upstream/downstream relationships between equipment are not explicitly modeled as they are not required for the gbXML use case. This is similar to the [`brick:Air_Loop`](https://ontology.brickschema.org/brick/Air_Loop.html) class in Brick.
- Stepping back, we must also decide what specific components go into the loop definition. Is it just the equipment? Or do we include affected architectural spaces? The pipes and ducts and connections between these components? Any sensors or actuators along the way? What about the connection points on equipment?

Here's a specific example of a simple HVAC system in 223P:

{{< figure width="100%" src="/img/2025-02-23-hvac-diagram.svg" alt="simple HVAC loop in 223P">}}

<details>
<summary>Expand for Turtle definition of the 223P model</summary>

{{< importcode "loops/2025-02-23-hvac223p.ttl" "turtle" >}}
</details>

---

[Part 2](/posts/223p/loops/eye-of-the-beholder-2) will explore how we can define loops in a knowledge graph and how we can derive different views of the same loop for different applications.


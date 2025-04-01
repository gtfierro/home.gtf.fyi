---
title: "Defining HVAC Loops"
date: 2025-03-23T00:00:00Z
categories: ['223p','rdf']
type: post
---

{{< announce >}}
This is an in-progress post and may contain some errors or incomplete information.
{{< /announce >}}

Here's a specific example of a simple HVAC system in 223P:

{{< figure width="100%" src="/img/hvac223p.ttl.svg" alt="simple HVAC loop in 223P">}}

<details>
<summary>Expand for Turtle definition of the 223P model</summary>

{{< importcode "2025-02-23-hvac223p.ttl" "turtle" >}}
</details>

---

We are using an RDF representation of the 223P model, meaning we have decomposed the graph into triples of
<code>subject predicate object</code> statements.
This is significant, because it affects the kinds of traversals and queries we can perform on the model.

I'm going to break the "loop definition" problem into two orthogonal components:

- What is the "topology" of the loop? Does it contain a single path through the graph, all elements in the transitive closure of a node, or a strongly connected component?
- What components are in the loop? Do I want equipment, connections, connection points, any properties we find along the way, ...?
    - this decision also affects the edge types we need to query to define the loop. Different types of components are connected by different types of edges.

Our goal is to fill out this table with the access methods required to define each kind of loop.

| | Simple Cycle | Transitive Closure | Strongly Connected Component |
|---|---|---|---|
| Single component type | ??? | ??? | ??? |
| Multiple component types | ??? | ??? | ??? |

Quick refresher on the difference between a cycle and a strongly connected component.
A cycle is a path through a graph that starts and ends at the same node; other than that node, no other node is visited more than once.
In the context of our HVAC system, this corresponds to the air loop through one of the VAVs (but not both!).
Below is an illustration of the cycle through VAV 1. There is a second cycle in this graph through VAV 2.

A strongly connected component (SCC) is a set of nodes where there is a path from every node to every other node in the set.
In the context of our HVAC system, this corresponds to the entire system, as there is a path from every component to every other component through the AHU.

{{< announce >}}
A **key limitation** of the work here is we are assuming that:
- all connection points are of the same substance (`s223:Fluid-Air`, etc)
- there is only one input and one output connection point per equipment

These assumptions are not true in general, especially with heat exchangers. These can have multiple input/output pairs which might even be of different substances (think of a hot water coil in an air loop). Handling these requires following the [`s223:pairedConnectionPoint`](https://explore.open223.info/s223/pairedConnectionPoint.html) relationship to follow within the equipment.
{{< /announce >}}

### Simple Cycle, Single Component Type

Let's start with what is probably the conceptually simplest case: a simple cycle definition using only a single component type.
This can look 2 ways.
The first is just the big equipment without any of their equipment components (containing only <code>AHU</code> and <code>VAV1</code>).

{{< figure width="100%" src="/img/2025-03-23-hvac-cycle-equipment.svg" alt="highlighting a cycle through VAV 1 without subcomponents">}}

The second is the big equipment with all of their equipment components: (<code>AHU, VAV1, Damper, Coil</code>).

{{< figure width="100%" src="/img/2025-03-23-hvac-cycle-equipment-components.svg" alt="highlighting a cycle through VAV 1 with subcomponents">}}

**Both of these loops are difficult to define programmatically** for 3 reasons:

1. Not all of the components are directly connected! The <code>VAV1</code> is connected to <code>AHU</code> *through* the <code>Room 1</code> node.
Any traversal algorithm would need to be able to follow the path through <code>Room 1</code> to find the connection between <code>VAV1</code> and <code>AHU</code>.
2. Even the directly connected components are connected through different types of edges. This is particularly relevant for the second loop where we include the equipment components.<code>AHU</code> has a direct link to <code>VAV1</code> through a <code>s223:connectedTo</code> edge, but <code>VAV1</code> is connected to its subcomponents through <code>s223:contains</code> edges.
3. When the algorithm reaches <code>AHU</code> it needs to not include anything in the <code>VAV2</code> branch of the graph. The only "repeat" node allowed in the loop definition is the starting node (<code>VAV1</code>).


We'll do this by first using a script to "compile" our model to include all of the [implied edges](https://docs.open223.info/explanation/223_overview.html) between the components.
This should make it easier to write the queries to define the loops.
{{< sn >}}Run with <code>uv run compile.py</code>{{< /sn >}}

{{< importcode "compile.py" "python" >}}

Now, we can use a Python script to convert this to a NetworkX representation and use an existing implementation to find cycles in the graph.
We are using the `networkx.simple_cycles` method here, which is a wrapper around a depth-first traversal of the graph.
{{< sn >}}Run with <code>uv run dfs.py</code>{{< /sn >}}

{{< importcode "dfs.py" "python" >}}

This gives the following output

{{< importcode "dfs-output.txt" "txt" >}}

There are 34 cycles in the graph! Many of these are trivially short loops that don't contain any interesting information but exist because of the additional edges added by the 223P ontology.
Edges like `s223:isConnectionPointOf` (can be inferred) and `s223:mapsTo` (added by the modeler) will point "backwards" from the flow of air through
the HVAC system, creating these loops.

To get our desired loop we need to filter out all non-equipment components from each `VAV1` cycle

{{< importcode "dfs-filter.py" "python" >}}

This gives the following output

{{< importcode "dfs-filter-output.txt" "txt" >}}

In here, we can see our desired loops from above, in addition to a few others.

This method of defining loops has a few steps, but you can express most things you want to find in the graph with a combination of compiling the model and using a graph traversal algorithm with some custom filtering and transformations.

| | Simple Cycle | Transitive Closure | Strongly Connected Component |
|---|---|---|---|
| Single component type | `nx.simple_cycles` + filtering  | ??? | ??? |
| Multiple component types | ??? | ??? | ??? |

Keep in mind that `nx.simple_cycles` is a brute-force algorithm that will find all cycles in the graph, so it can be slow for large graphs.

### Simple Cycle, Multiple Component Types

This is pretty similar to the single component type case, but we just change the filtering step to include only the type of components we care about.
For example, if we want to include domain spaces in addition to equipment in the loop, just change the SPARQL query to include the space types.
This is implemented in the `keep` function below:
{{< sn >}}Run with <code>uv run dfs-filter-multiple.py</code>{{< /sn >}}

{{< importcode "dfs-filter-multiple.py" "python" >}}

The `keep` function also contains the line `FILTER NOT EXISTS { ?something s223:contains ?node }`, which will filter out all components contained by another component; this will remove the damper and heating coil from any loops we define.
Obviously this is an optional feature: removing this line will include loop definitions with the VAV's components.

Running the script gives the following output, which contains the loop we want: `Room1HVAC -> VAV1 -> AHU`

{{< importcode "dfs-filter-multiple-output.txt" "txt" >}}

We can also do this without having to touch any SPARQL at all!

{{< importcode "cycles-root-types.py" "python" >}}

This uses the compiled graph (with the 223P ontology embedded within it) to find the cycles in the graph that contain only the types of components we care about. It does this by using a shortest path algorithm to determine which is the most appropriate "root" class of each node in the cycle, and using that information to filter out the cycles that don't contain the desired components.
We can also use this to keep cycles that contain at least one of each desired component type.

{{< importcode "cycles-root-types-output.txt" "txt" >}}

| | Simple Cycle | Transitive Closure | Strongly Connected Component |
|---|---|---|---|
| Single component type | `nx.simple_cycles` + filtering  | ??? | ??? |
| Multiple component types | `nx.simple_cycles` + filtering | ??? | ??? |

### Transitive Closure, Single Component Type

Now let's examine how to do a transitive closure definition using only a single component type.
A *transitive closure* is the set of all nodes reachable from a given node by following a specific edge type (or specific set of edge types).
The physical analog to the transitive closure of a VAV is all equipment in the building that might receive (recycled) air that was previously conditioned by the VAV.
For a chiller's supply water, the physical analog is every coil that would receive water from the chiller.

In its most basic form, the transitive closure definition needs an edge pattern to follow.
We can also constraint the closure to only include certain types of nodes, or contain certain nodes.

We have 3 types of components in our example: Equipment (AHU, VAV), Connection Points (Inlet, Outlet), and Connections (Ducts).

Let's start with the <code>s223:Equipment</code> type.
Instances of equipment are connected to each other by <code>s223:connectedTo</code> edges.
We can define the transitive closure of equipment as the set of all equipment that are connected to each other using this edge.

```sparql
PREFIX s223: <http://data.ashrae.org/standard223#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?equipment ?connectedEquipment
WHERE {
    BIND(<http://example.com/hvac/VAV1> as ?equipment)
    ?equipment rdf:type/rdfs:subClassOf* s223:Equipment .
    ?equipment s223:connectedTo ?connectedEquipment .
    ?connectedEquipment rdf:type/rdfs:subClassOf* s223:Equipment .
}
```

This query needs to be run on the *compiled model with the embedded ontology*; this model contains all of the inferred edges as well as the type definitions (and hierarchy) required to support the `rdfs:subClassOf` edges.
The `BIND` statement at the top of the query sets the starting node for the transitive closure to `VAV1`.

The result of this query can be found [here](https://query.open223.info/?query=PREFIX+unit%3A+%3Chttp%3A%2F%2Fqudt.org%2Fvocab%2Funit%2F%3E%0APREFIX+quantitykind%3A+%3Chttp%3A%2F%2Fqudt.org%2Fvocab%2Fquantitykind%2F%3E%0APREFIX+qudt%3A+%3Chttp%3A%2F%2Fqudt.org%2Fschema%2Fqudt%2F%3E%0APREFIX+sh%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Fshacl%23%3E%0APREFIX+owl%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2002%2F07%2Fowl%23%3E%0APREFIX+s223%3A+%3Chttp%3A%2F%2Fdata.ashrae.org%2Fstandard223%23%3E%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0APREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0ASELECT+%3Fequipment+%3FconnectedEquipment%0AWHERE+%7B%0A++BIND%28%3Chttp%3A%2F%2Fexample.com%2Fhvac%2FVAV1%3E+as+%3Fequipment%29%0A++++%3Fequipment+rdf%3Atype%2Frdfs%3AsubClassOf*+s223%3AEquipment+.%0A++++%3Fequipment+s223%3AconnectsTo*+%3FconnectedEquipment+.%0A++++%3FconnectedEquipment+rdf%3Atype%2Frdfs%3AsubClassOf*+s223%3AEquipment+.%0A%7D%0A&url=https%3A%2F%2Fgtf.fyi%2Fposts%2F223p%2Fhvac223p-compiled-all.ttl)

**This is not currently working due to limitations in the SHACL inference engine which doesn't run enough times to add the edges we need**

The most basic transitive closure we can define uses the `s223:cnx` relationship, which is a catch-all for all connections between components.
However, there is no requirement that `s223:cnx` exists between all components (it is a convenience for building models), so this will not always give us the full transitive closure.

| | Simple Cycle | Transitive Closure | Strongly Connected Component |
|---|---|---|---|
| Single component type | `nx.simple_cycles` + filtering  | SPARQL Query | ??? |
| Multiple component types | `nx.simple_cycles` + filtering | ??? | ??? |

### Transitive Closure, Multiple Component Types

Handling multiple component types in the transitive closure is mostly straightforward as an extension to the single component type case.
What changes is the definition of the transitive closure: it now needs to handle multiple types of edges.
In simpler ontologies like Brick, the single topological relationship `brick:feeds` is easy to follow between all sorts of entities.
223P has different types of edges between different types of components, so the transitive closure query needs to be more complex.

For example, to find the transitive closure of all equipment and connection points connected to a VAV, we need to follow:

- `s223:connectedTo` edges between equipment
- `s223:hasConnectionPoint` edges between equipment and connection points

```sparql
PREFIX s223: <http://data.ashrae.org/standard223#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?start ?rest
WHERE {
    BIND(<http://example.com/hvac/VAV1> as ?start)
    ?start (s223:connectedTo|s223:hasConnectionPoint)* ?rest .
}
```

Note that this query returns everything reachable from the VAV using these edges; any filtering based on the type of the node will need to be done in post-processing similar to the cycle case.

| | Simple Cycle | Transitive Closure | Strongly Connected Component |
|---|---|---|---|
| Single component type | `nx.simple_cycles` + filtering  | SPARQL Query | ??? |
| Multiple component types | `nx.simple_cycles` + filtering | SPARQL Query + filtering | ??? |

---

I will talk about strongly connected components in a future post.

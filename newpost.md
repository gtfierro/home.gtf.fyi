### Table of Contents
1. [Introduction](#introduction)
2. [Simple Cycle, Single Component Type](#simple-cycle-single-component-type)
3. [Simple Cycle, Multiple Component Types](#simple-cycle-multiple-component-types)
4. [Transitive Closure, Single Component Type](#transitive-closure-single-component-type)
5. [Transitive Closure, Multiple Component Types](#transitive-closure-multiple-component-types)
6. [Conclusion](#conclusion)

### Introduction {#introduction}
This document explores different methods for defining HVAC loops using an RDF representation of the 223P model. Specifically, it addresses the topology of loops and the components involved. We'll discuss simple cycles, transitive closures, and touch on strongly connected components.

### Simple Cycle, Single Component Type {#simple-cycle-single-component-type}
We begin with defining simple cycles using a single component type within an HVAC system. By utilizing a Python script and NetworkX's `simple_cycles` method, we can identify and filter desired cycles.

### Simple Cycle, Multiple Component Types {#simple-cycle-multiple-component-types}
This section extends to cycles involving multiple component types. Adjusting the filtering criteria in the Python scripts allows us to capture cycles with various component types, such as spaces alongside equipment.

### Transitive Closure, Single Component Type {#transitive-closure-single-component-type}
A transitive closure is employed to identify all reachable nodes from a starting component within the graph. We utilize SPARQL queries to delineate transitive closures, focusing on single component types connected by specific edge patterns.

### Transitive Closure, Multiple Component Types {#transitive-closure-multiple-component-types}
Complexity increases when managing transitive closures involving multiple component types due to varied edge relationships. SPARQL queries are adjusted to manage this complexity by considering several edge patterns.

### Conclusion {#conclusion}
The document closes by summarizing the methods and frameworks discussed for defining HVAC loops in 223P models. It highlights the current limitations and potential areas for further exploration, especially regarding strongly connected components.

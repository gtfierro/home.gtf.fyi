---
title: "Agentic Knowledge Graph Creation"
date: 2026-07-30
categories: ['rdf','agent','llm']
type: post
maturity: seedling
lastmod: 2026-07-30
updates:
  - date: "2026-07-30"
    note: "Initial draft"
---

I created an [LLM agent skill](https://agentskills.io/home) for BuildingMOTIF.
The skill teaches agents how to use BuildingMOTIF to create knowledge graphs for the Brick, ASHRAE 223P, or WaTr ontologies.
The documentation for the skill is available at [here](https://github.com/NatLabRockies/BuildingMOTIF/blob/gtf-buildingmotif/docs/guides/agent-skill.md); it has a clunky
installation method currently for two reasons:
(a) the BuildingMOTIF branch is not yet merged into the main branch, and (b) the skill is not yet published to the Agent Skills Registry.
So, you'll have to download the skill [yourself](https://github.com/NatLabRockies/BuildingMOTIF/blob/gtf-buildingmotif/docs/guides/agent-skill.md#getting-the-skill-files)

Obviously more evaluation and other work is coming soon, but I wanted to share the skill and some examples of its use now.

Examples:
- Using GLM 5.2 to create a WaTr knowledge graph
    - [Session trace](/posts/agents/glm5.2-watr.html)
    - [Script](/posts/agents/build_watr_model.py)
    - [Knowledge graph](/posts/agents/watr_model.ttl)
- Using GLM 5.2 to create a ASHRAE 223P knowledge graph
    - [Session trace](/posts/agents/glm5.2-223p.html)
    - [Script](/posts/agents/build_vav3110.py)
    - [Knowledge graph](/posts/agents/vav3110.ttl)

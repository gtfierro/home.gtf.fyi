---
title: "Getting all template bodies from BuildingMOTIF"
date: 2023-06-12T17:15:14-07:00
categories: ['BuildingMOTIF','scratch']
type: post
---

Here's a quick how-to on load libraries into a BuildingMOTIF installation and then list all of the templates in those libraries as well as the *bodies* (RDF graph component) of those templates.

At this time (2023-06-13), BuildingMOTIF is still under active development so you'll want to install it directly from GitHub{{< sn >}}You can also clone the [repository](https://github.com/NREL/BuildingMOTIF) directly and do this all within that environment {{< /sn >}}:

```bash
pip install -e git+https://github.com/NREL/BuildingMOTIF#egg=buildingmotif
```

Now, create a file called `libraries.yml` which contains the following lines:

```yml
- ontology: https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl
- git:
    repo: https://github.com/NREL/BuildingMOTIF
    branch: develop
    path: libraries/chiller-plant
- git:
    repo: https://github.com/NREL/BuildingMOTIF
    branch: develop
    path: libraries/ashrae/guideline36
```

You can then load these libraries into a local BuildingMOTIF installation using this command:

```bash
DB_URI=sqlite:///my_libraries.db buildingmotif load -l libraries.yml
```

Now, all of our libraries are loaded into a local install! All of the state associated with BuildingMOTIF is now in a local SQLite database called `my_libraries.db`.

To list the templates, you will need to boot up a Python interpreter or paste the following code into a text editor
and then execute it *in the same directory as `my_libraries.db`*:

```python
from buildingmotif import BuildingMOTIF
from buildingmotif.dataclasses import Library

bm = BuildingMOTIF("sqlite:///my_libraries.db")

for lib in bm.table_connection.get_all_db_libraries():
    library = Library.load(db_id=lib.id)
    for template in library.get_templates():
        print(template)
# outputs:
# Template(_id=1345, _name='cold-deck-with-damper', body=<Graph identifier=3a8e57ad-2e76-456e-97f9-ce97af8284ff (<class 'rdflib.graph.Graph'>)>, optional_args=[], _bm=<buildingmotif.building_motif.building_motif.BuildingMOTIF object at 0x1023c7ee0>)
# Template(_id=1346, _name='vav-cooling-only', body=<Graph identifier=cfe59bc4-1aeb-4f33-834a-731af90a0e4d (<class 'rdflib.graph.Graph'>)>, optional_args=['occ', 'co2'], _bm=<buildingmotif.building_motif.building_motif.BuildingMOTIF object at 0x1023c7ee0>)
# Template(_id=1347, _name='multiple-zone-ahu', body=<Graph identifier=ee9e2628-c1b4-4e43-b0ef-5cd623265282 (<class 'rdflib.graph.Graph'>)>, optional_args=['ma_temp', 'ra_temp', 'filter_pd'], _bm=<buildingmotif.building_motif.building_motif.BuildingMOTIF object at 0x1023c7ee0>)
# Template(_id=1348, _name='with-relief-damper', body=<Graph identifier=f3e33ee3-6e4b-4b28-a8ae-e4d7ebd890ab (<class 'rdflib.graph.Graph'>)>, optional_args=['sp-sensor'], _bm=<buildingmotif.building_motif.building_motif.BuildingMOTIF object at 0x1023c7ee0>)
# Template(_id=1349, _name='with-return-fan', body=<Graph identifier=59596d76-14dd-4595-9e04-ceef558311bc (<class 'rdflib.graph.Graph'>)>, optional_args=['supply-air-flow', 'return-air-flow', 'sp-sensor'], _bm=<buildingmotif.building_motif.building_motif.BuildingMOTIF object at 0x1023c7ee0>)
```

To get the RDF graph part of these templates, you can access the `body` attribute of each Template object. This will retrieve the RDF graph object associated with the template:

```python
from buildingmotif import BuildingMOTIF
from buildingmotif.dataclasses import Library

bm = BuildingMOTIF("sqlite:///my_libraries.db")

for lib in bm.table_connection.get_all_db_libraries():
    library = Library.load(db_id=lib.id)
    for template in library.get_templates():
        print(template.body.serialize())
```

This will output things like:

```ttl
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix ns3: <urn:___param___#> .

ns3:name brick:hasPart ns3:return-fan ;
    brick:hasPoint ns3:return-air-flow,
        ns3:sp-sensor,
        ns3:supply-air-flow .

ns3:relief-damper a brick:Exhaust_Damper .
```

You may also want to "inline" the template dependencies which will give you larger graphs with additional types and constraints.


```python
from buildingmotif import BuildingMOTIF
from buildingmotif.dataclasses import Library

bm = BuildingMOTIF("sqlite:///my_libraries.db")

for lib in bm.table_connection.get_all_db_libraries():
    library = Library.load(db_id=lib.id)
    for template in library.get_templates():
        print(template.inline_dependencies().body.serialize())
```

This outputs larger graphs like:

```ttl
@prefix brick: <https://brickschema.org/schema/Brick#> .

<urn:___param___#name> brick:hasPart <urn:___param___#return-fan> ;
    brick:hasPoint <urn:___param___#return-air-flow>,
        <urn:___param___#sp-sensor>,
        <urn:___param___#supply-air-flow> .

<urn:___param___#relief-damper> a brick:Damper,
        brick:Exhaust_Damper ;
    brick:hasPoint <urn:___param___#relief-damper-dmppos> .

<urn:___param___#relief-damper-dmppos> a brick:Damper_Position_Command .

<urn:___param___#return-air-flow> a brick:Return_Air_Flow_Sensor .

<urn:___param___#return-fan> a brick:Fan,
        brick:Return_Fan ;
    brick:hasPoint <urn:___param___#return-fan-name-speed>,
        <urn:___param___#return-fan-name-start_stop>,
        <urn:___param___#return-fan-name-status> .

<urn:___param___#return-fan-name-speed> a brick:Frequency_Command .

<urn:___param___#return-fan-name-start_stop> a brick:Start_Stop_Command .

<urn:___param___#return-fan-name-status> a brick:Fan_Status .

<urn:___param___#sp-sensor> a brick:Static_Pressure_Sensor .

<urn:___param___#supply-air-flow> a brick:Supply_Air_Flow_Sensor .
```

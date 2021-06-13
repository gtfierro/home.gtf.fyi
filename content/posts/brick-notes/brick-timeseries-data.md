---
title: "Brick Timeseries Data"
date: 2020-02-02T17:15:14-07:00
categories: ['Brick']
type: post
---

# Brick Timeseries Access 

Here is a "completely" modeled zone air temperature sensor modeled in Brick

```turtle
@prefix brick: <https://brickschema.org/schema/1.2/Brick#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix tag: <https://brickschema.org/schema/1.2/BrickTag#> .
@prefix : <urn:bldg#> .

:x    a     brick:Zone_Air_Temperature_Sensor ;
    brick:hasUnit   unit:DEG_C ;
    rdfs:label  "SODA1R410_ARS" ;
    # below, we will ignore the following properties as they
    # are orthogonal to the timeseries modeling discussion
    brick:isPointOf :hvac_zone_1 ;
    # automatically added
    brick:hasTag    tag:Zone, tag:Air, tag:Temperature, tag:Sensor ;
.
```

How do we connect the temperature sensor `x` to a timeseries database? And what are the concerns we will need to handle?

I'll start with the simplest model, and gradually motivate and add complexity. Some of the design decisions are orthogonal, and some are not.

Note that [SSN/SOSA](https://www.w3.org/TR/vocab-ssn) do not deal with any aspects of timeseries storage.

---

## Simple Model

In the simplest model, we use the point\'s URI (`urn:bldg#x` above) as the foreign key into the timeseries database. This requires no extra, implementation-specific metadata to be added to the Brick model above.

```turtle
@prefix brick: <https://brickschema.org/schema/1.2/Brick#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix tag: <https://brickschema.org/schema/1.2/BrickTag#> .
@prefix : <urn:bldg#> .

:x    a     brick:Zone_Air_Temperature_Sensor ;
    brick:hasUnit   unit:DEG_C ;
.
```

Here is a strawman SQL table implementation. We can optimize this by using smaller unique identifiers to factor out the overhead of the potentially long URI in our data table. This would result in the entity URIs being placed in another table

```sql
CREATE TABLE data(
    time        TIMESTAMPTZ,
    entity_uri  TEXT NOT NULL,
    value       FLOAT NOT NULL
);
```

See the Mortar Postgres schema for an example of a real-world schema: <https://github.com/gtfierro/mortar/blob/master/docker/pg/setup.sql>

The advantages of this approach are that Brick models can be maximally agnostic to how they are stored; all the complexity of how to store, address, index and identify the timeseries data is factored out to an external system.

---

## Adding Timeseries Identifier

A common alternative design --- used by Mortar v1, Brick Server and some ad-hoc data libraries --- is to embed timeseries identifiers in the Brick model. This can be done with a `brick:hasTimeseriesId` DataType property:

```turtle
@prefix brick: <https://brickschema.org/schema/1.2/Brick#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix : <urn:bldg#> .

:x    a     brick:Zone_Air_Temperature_Sensor ;
    brick:hasUnit   unit:DEG_C ;
    brick:hasTimeseriesId "4905ecbd-78d0-455f-b02c-23576d1f2493" ;
.
```

The advantages of this approach are that it is now clear which entities have timeseries data associated with them. This also can factor the "mapping" issues out from your timeseries database: rather than storing the entity URI for each identifier in your timeseries database, or forcing your timeseries database to store URIs instead of a more space-efficient and consistently-sized identifier, the Brick model can simply store the identifier that is used by the database.

In the example above, this is a UUID, but it could just as easily be an integer or byte hash.

---

## Adding Storage

But what if we want to store metadata about where to find the timeseries data? We can augment the above model with properties of the timeseries database: the network location, access credentials, valid range of data, and so on.

```turtle
@prefix brick: <https://brickschema.org/schema/1.2/Brick#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix : <urn:bldg#> .

:db   a     brick:InfluxDatabase ;
    brick:address "1.2.3.4:8888" ;
    brick:protocol "http" ;
    brick:influxCollection "mydata" ;
    brick:username "Rosencrantz" ;
    brick:password "Guildenstern" ;
.

:x    a     brick:Zone_Air_Temperature_Sensor ;
    brick:hasUnit   unit:DEG_C ;
    brick:hasTimeseriesId "4905ecbd-78d0-455f-b02c-23576d1f2493" ;
    brick:storedAt  :db ;
.
```

Now, applications can retrieve the relevant properties to access the timeseries data from the Brick model. The "type" of the storage location tells the application which protocol and/or API to speak. This model permits data to be stored in different databases (multiple `brick:storedAt` properties), but assumes that these database use the same timeseries identifier. This is not necessarily an issue if we consider the entity timeseries ID to come from the Brick model, rather than come from the timeseries database.

If we do need to store timeseries in each database, then we can adopt something like the following model:

```turtle
@prefix brick: <https://brickschema.org/schema/1.2/Brick#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix : <urn:bldg#> .

:db1   a     brick:InfluxDatabase ;
    brick:address "1.2.3.4:8888" ;
    brick:protocol "http" ;
    brick:influxCollection "mydata" ;
    brick:username "Rosencrantz" ;
    brick:password "Guildenstern" ;
.

:db2   a     brick:TimescaleDatabase ;
    brick:connString "postgresql://myuser:mypass@1.2.3.4:5432/mydata" ;
.

:x    a     brick:Zone_Air_Temperature_Sensor ;
    brick:hasUnit   unit:DEG_C ;
    brick:timeseries [
        brick:hasTimeseriesId "4905ecbd-78d0-455f-b02c-23576d1f2493" ;
        brick:storedAt  :db1 ;
    ] ;
    brick:timeseries [
        brick:hasTimeseriesId "da13ecf5ad4e18a9" ;
        brick:storedAt  :db2 ;
    ],
.
```

It is not too hard imagine how we could add additional properties to capture the temporal range of timeseries data that is stored in each database (for example if 2012-2014 data was stored in `:db1` and all subsequent data was stored in `:db2`). The ontology-minded among us may even point to the PROV-O ontology as one existing data model that can help: https://www.w3.org/TR/prov-o

An alternative model could substitute the numerous properties as seen on the `InfluxDatabase` instance, and instead standardize on some database URI. I\'m not aware of any standard that actually defines this, but the postgres connstring is fairly ubiquitous:

```
protocol://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]
```

The advantages of this approach are that it gives more information to the application, and permits a great deal of flexibility in where and how timeseries data is stored. The other side of this is, of course, increased complexity of the Brick model and how it must be queried.

---

## With Current Value

Another aspect to the representation of timeseries data is how we might capture the **current** value of a point in a Brick model. This information can be represented in the RDF model, but it is important to point out that this would likely be part of a "virtual" Brick model, rather than the "on disk" Brick model.

The "on disk" Brick model is what we consider to be a Brick model today: essentially the turtle file loaded into RDFlib or some database. In conjunction with any of the above methods for connecting a point entity to its timeseries data, the Brick database can "patch" the Brick model with properties that pull in the current value of a point (or past 15 minutes of points, or whatever is desired). This can be done at query time, if the query asks for it.

If the Brick model, enhanced with these "virtual" and "added-at-query-time" properties, were to be rendered as turtle, it might look like the following:

```turtle
@prefix brick: <https://brickschema.org/schema/1.2/Brick#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix : <urn:bldg#> .

:x    a     brick:Zone_Air_Temperature_Sensor ;
    brick:hasUnit   unit:DEG_C ;
    brick:hasTimeseriesId "4905ecbd-78d0-455f-b02c-23576d1f2493" ;
    brick:currentValue 20.1 ;
.
```

It is worth noting that 223P has several ways of representing current values, which account for cases where a single value is represented in two different measurement systems. The `qudt:QuantityValue` instances follow QUDT best practices for representing a value with a unit.

```turtle
:Fan20OutletPressureValue
  a c223:Value ;
  c223:hasSimpleValue "101300" ;
  qudt:quantityValue b20:SIValue ;
  qudt:quantityValue b20:USValue ;
.

:SIValue
  a qudt:QuantityValue ;
  qudt:unit <http://qudt.org/vocab/unit/PA> ;
  qudt:value "19123"^^qudt:valueUnion ;
.
:USValue
  a qudt:QuantityValue ;
  qudt:unit <http://qudt.org/vocab/unit/LB_F-PER-IN2> ;
  qudt:value "2.7"^^qudt:valueUnion ;
.
```

In Brick, we make the simplification that units apply to the whole timeseries, though it is not too hard to see how that could be relaxed/generalized:

```turtle
:x    a     brick:Zone_Air_Temperature_Sensor ;
    brick:timeseries [
        brick:hasTimeseriesId "4905ecbd-78d0-455f-b02c-23576d1f2493" ;
        brick:hasUnit   unit:DEG_C ;
        brick:storedAt  :db1 ;
    ] ;
    brick:timeseries [
        brick:hasTimeseriesId "da13ecf5ad4e18a9" ;
        brick:hasUnit   unit:DEG_F ;
        brick:storedAt  :db2 ;
    ] ;
.
```

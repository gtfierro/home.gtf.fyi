---
title: "Binding to 231"
date: 2026-02-22T15:00:00-07:00
categories: ['Brick','223P','231']
type: post
maturity: sprout
lastmod: 2026-02-22
updates:
  - date: "2026-02-22"
    note: "Initial draft"
---

## Background

Control Description Language (CDL) is a subset of Modelica which portably specifies control sequences for building systems.
It has recently been standardized and published as ASHRAE Standard 231.
CDL represents control sequences as a directed graph of control blocks, which have inputs and outputs, and may be composed of other control blocks.

Here's an example block:

```ttl
@prefix S231P: <https://data.ashrae.org/S231P#> .
@prefix cdl: <http://example.org#cdl_models.Controls.> .
@prefix quantitykind: <http://qudt.org/vocab/quantitykind#> .
@prefix qudt: <http://qudt.org/schema/qudt#> .
@prefix unit: <http://qudt.org/vocab/unit#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

cdl:Controller a S231P:Block ;
    S231P:containsBlock cdl:Controller.loaShe,
        cdl:Controller.single_zone_ratchet_base ;
    S231P:hasInput cdl:Controller.TZon,
        cdl:Controller.TZonCooSetCur,
        cdl:Controller.TZonHeaSetCur ;
    S231P:hasOutput cdl:Controller.TZonCooSetCom,
        cdl:Controller.TZonHeaSetCom ;
    S231P:hasParameter cdl:Controller.loadShedHourEnd,
        cdl:Controller.loadShedHourStart,
        cdl:Controller.occStaHourEnd,
        cdl:Controller.occStaHourStart,
        cdl:Controller.reboundDuration,
        cdl:Controller.samplePeriodRatchet,
        cdl:Controller.samplePeriodRebound ;
    S231P:label "Controller" .
```

The `s231P:hasInput` and `s231P:hasOutput` relationships point to the names of the inputs and outputs of the block, which
are commonly things like setpoints, sensors, alarms, commands.
The block above has inputs for the current zone temperature (`TZon`), the current cooling setpoint (`TZonCooSetCur`), and the current heating setpoint (`TZonHeaSetCur`); it has outputs for the cooling setpoint command (`TZonCooSetCom`) and the heating setpoint command (`TZonHeaSetCom`).
To be able to use CDL to specify control sequences for a particular building, we need to be able to connect the inputs and outputs of the control blocks to the actual points in the building that they refer to.
This tells any CDL execution engine which points to read from and write to when executing the control sequence.

Our question is: **what does this binding look like, and how can we represent it in Brick?**

Here's the Brick model we'll be using:

```ttl
@prefix bldg: <https://BESTESTAir.urn#> .
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix quantitykind: <http://qudt.org/vocab/quantitykind/> .
@prefix qudt: <http://qudt.org/schema/qudt/> .

bldg:hvac_wes a brick:VAV ;
    brick:feeds bldg:flo_Wes ;
    brick:hasPoint bldg:hvac_oveZonActWes_yDam,
        bldg:hvac_oveZonActWes_yReaHea,
        bldg:hvac_reaZonWes_TSup,
        bldg:hvac_reaZonWes_V_flow .

bldg:flo_Wes a brick:Zone ;
    brick:hasPoint bldg:hvac_oveZonSupWes_TZonCooSet,
        bldg:hvac_oveZonSupWes_TZonHeaSet,
        bldg:hvac_reaZonWes_TZon .

bldg:hvac_oveZonActWes_yDam a brick:Damper_Position_Setpoint ;
    qudt:hasUnit qudt:UNITLESS .

bldg:hvac_oveZonActWes_yReaHea a brick:Reheat_Command ;
    qudt:hasUnit qudt:UNITLESS .

bldg:hvac_oveZonSupWes_TZonCooSet a brick:Zone_Air_Cooling_Temperature_Setpoint ;
    qudt:hasQuantityKind quantitykind:Temperature ;
    qudt:hasUnit qudt:K .

bldg:hvac_oveZonSupWes_TZonHeaSet a brick:Zone_Air_Heating_Temperature_Setpoint ;
    qudt:hasQuantityKind quantitykind:Temperature ;
    qudt:hasUnit qudt:K .

bldg:hvac_reaZonWes_TSup a brick:Supply_Air_Temperature_Sensor ;
    qudt:hasQuantityKind quantitykind:Temperature ;
    qudt:hasUnit qudt:K .

bldg:hvac_reaZonWes_TZon a brick:Zone_Air_Temperature_Sensor ;
    qudt:hasQuantityKind quantitykind:Temperature ;
    qudt:hasUnit qudt:K .

bldg:hvac_reaZonWes_V_flow a brick:Supply_Air_Flow_Sensor ;
    qudt:hasQuantityKind quantitykind:VolumeFlowRate ;
    qudt:hasUnit qudt:M3-PER-SEC .
```

## The wrong way: indirection through another predicate

I was reading through [this paper](https://www.sciencedirect.com/science/article/pii/S0926580526000907) on
integrating Brick and the newly-released Control Description Language (ASHRAE Standard 231)
and noticed that the paper introduced a new relationship:

> To connect inputs and outputs from control sequences to points in equipment, without violating the Brick schema or CDL, we introduce a new relationship, `ex:connectedTo`.

This means that the resulting "binding" would look like this:

```ttl
cdl:Controller.TZon ex:connectedTo bldg:hvac_reaZonWes_TZon .
cdl:Controller.TZonCooSetCur ex:connectedTo bldg:hvac_oveZonSupWes_TZonCooSet .
cdl:Controller.TZonHeaSetCur ex:connectedTo bldg:hvac_oveZonSupWes_TZonHeaSet .
cdl:Controller.TZonCooSetCom ex:connectedTo bldg:hvac_oveZonActWes_yDam .
cdl:Controller.TZonHeaSetCom ex:connectedTo bldg:hvac_oveZonActWes_yReaHea .
```

This works, but it introduces an extra layer of indirection that is unnecessary.

Now, I want to be clear that I think this is a great practical paper demonstrating use of Brick, CDL, and IFC, and I think the authors did a great job of navigating the challenges of integrating these standards.
But I do think this new relationship is a design mistake, and I want to explain why.
To be fair, ASHRAE 231 does not do a great job of specifying the intended pattern below, and I hope this can be addressed with further public examples and documentation.

## The right way: the inputs and outputs are the predicates

The controller definition tells us that `cdl:Controller.TZon` is an input, and `cdl:Controller.TZonCooSetCom` is an output.
This means that we can directly use these as predicates to connect to the points in the building, without introducing an extra relationship:

```ttl
cdl:Controller
    cdl:Controller.TZon bldg:hvac_reaZonWes_TZon ;
    cdl:Controller.TZonCooSetCur bldg:hvac_oveZonSupWes_TZonCooSet ;
    cdl:Controller.TZonHeaSetCur bldg:hvac_oveZonSupWes_TZonHeaSet ;
    cdl:Controller.TZonCooSetCom bldg:hvac_oveZonActWes_yDam ;
    cdl:Controller.TZonHeaSetCom bldg:hvac_oveZonActWes_yReaHea .
```

## Ambiguity in the presence of multiple instances

Everything above uses a single instance of the `Controller` block, so the distinction between the block *type* and a particular *instance* of it never really surfaces.
But CDL sequences aren't singletons!
The same `Controller` block could be instantiated once per zone, once per AHU, or however many times the sequence needs to repeat.
Each instance gets its own identity, but every instance of the same block would share the same input, output, and parameter names because those names come from the block definition and not from the instance.

The `ex:connectedTo` model creates an ambiguous situation:
consider two zones, west and east, each with its own instance of `Controller`.
We need to say "west's `TZon` is bound to this point" and "east's `TZon` is bound to that point".
With `ex:connectedTo`, we must bind to the block-level name itself, since that's the only name we have:

```ttl
cdl:Controller.TZon ex:connectedTo bldg:hvac_reaZonWes_TZon .
cdl:Controller.TZon ex:connectedTo bldg:hvac_reaZonEas_TZon .
```

Both triples have the same subject.
There is nothing here that says which instance of `Controller` each binding belongs to: `cdl:Controller.TZon` isn't "west's `TZon`" or "east's `TZon`," it's just *the* `TZon` input of the block.
To fix this you'd have to mint a fresh URI per instance per input (`cdl:Controller_Wes.TZon`, `cdl:Controller_Eas.TZon`, ...), which defeats the purpose of having block-level names at all and pushes the type/instance distinction into your URI-naming convention instead of your data model.

The predicate pattern doesn't have this problem, because the instance is the subject and the block-level name is the predicate.

```ttl
bldg:hvac_wes_ctrl
    cdl:Controller.TZon bldg:hvac_reaZonWes_TZon ;
    ... .

bldg:hvac_eas_ctrl
    cdl:Controller.TZon bldg:hvac_reaZonEas_TZon ;
    ... .
```

`cdl:Controller.TZon` means the same thing in both triples --- "the `TZon` input of the `Controller` block" --- but each triple is unambiguously about a different instance, because the subject carries that information instead of the predicate.

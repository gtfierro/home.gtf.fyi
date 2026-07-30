"""
Build a 223P model of BACnet device 3110 (a series fan-powered VAV terminal unit
with hot-water reheat) from discover-3110.ttl.

Every 223P class / role / medium / QUDT term used below was verified against the
loaded 223p.ttl ontology in discover.py.  No term is guessed.

Scope (confirmed with the user): physical + control points only; full air-side
topology (connection points wired through ducts via s223:cnx) plus the hydronic
reheat branch.  Trend logs, schedules, calendars, notification classes, files,
internal PID loop variables, and opaque m#### multistates are intentionally
excluded.
"""
import os
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, OWL
from buildingmotif import BuildingMOTIF
from buildingmotif.dataclasses import Library, Model
from buildingmotif.namespaces import S223, SH, bind_prefixes

HERE = os.path.dirname(os.path.abspath(__file__))
S223_TTL = os.path.join(HERE, "223p.ttl")
BACNET_DUMP = os.path.join(HERE, "..", "buildingmotif-skill-src", "discover-3110.ttl")
OUT_TTL = os.path.join(HERE, "vav3110.ttl")

# --- namespaces ---
BLDG = Namespace("urn:bldg/")
BACNET = Namespace("http://data.ashrae.org/bacnet/2016#")
UNIT = Namespace("http://qudt.org/vocab/unit/")
QK = Namespace("http://qudt.org/vocab/quantitykind/")

g = Graph()
g.bind("s223", S223)
g.bind("bldg", BLDG)
g.bind("qudt", Namespace("http://qudt.org/schema/qudt/"))
g.bind("unit", UNIT)
g.bind("quantitykind", QK)
g.bind("bacnet", BACNET)


def R(local):
    return BLDG[local]


def add(s, p, o):
    g.add((s, p, o))


def prop(node, label, klass, qk=None, unit=None, desc=None, owner=None, see=None, enum_kind=None):
    """Create a typed 223P Property node with QUDT quantity kind/unit and optional enum kind."""
    add(node, RDF.type, klass)
    add(node, RDFS.label, Literal(label))
    if qk is not None:
        add(node, URIRef("http://qudt.org/schema/qudt/hasQuantityKind"), qk)
    if unit is not None:
        add(node, URIRef("http://qudt.org/schema/qudt/hasUnit"), unit)
    if enum_kind is not None:
        add(node, S223.hasEnumerationKind, enum_kind)
    if desc:
        add(node, RDFS.comment, Literal(desc))
    if owner is not None:
        add(owner, S223.hasProperty, node)
    if see is not None:
        add(node, RDFS.seeAlso, see)
    return node


def sensor(node, observes, location, label):
    add(node, RDF.type, S223.Sensor)
    add(node, RDFS.label, Literal(label))
    add(node, S223.observes, observes)
    add(node, S223.hasObservationLocation, location)
    return node


def cp(node, klass, medium, role=None):
    add(node, RDF.type, klass)
    add(node, S223.hasMedium, medium)
    if role is not None:
        add(node, S223.hasRole, role)
    return node


# ---------------------------------------------------------------------------
# Equipment
# ---------------------------------------------------------------------------
vav = R("vav3110")
damper = R("vav3110_damper")
fan = R("vav3110_fan")
coil = R("vav3110_reheat_coil")
hwvalve = R("vav3110_hw_valve")
zone = R("zone")
zone_ds = R("zone_hvac_domain_space")
zone_space = R("zone_physical_space")

add(vav, RDF.type, S223.FanPoweredTerminal)
add(vav, RDFS.label, Literal("VAV-3110 (series fan-powered terminal unit)"))
add(vav, S223.contains, damper)
add(vav, S223.contains, fan)
add(vav, S223.contains, coil)
add(vav, S223.contains, hwvalve)

add(damper, RDF.type, S223.Damper)
add(damper, RDFS.label, Literal("VAV-3110 primary air damper"))
add(fan, RDF.type, S223.Fan)
add(fan, RDFS.label, Literal("VAV-3110 series fan"))
add(coil, RDF.type, S223.HeatingCoil)
add(coil, RDFS.label, Literal("VAV-3110 hot-water reheat coil"))
add(coil, S223.hasRole, S223["Role-Heating"])
add(hwvalve, RDF.type, S223.TwoWayValve)
add(hwvalve, RDFS.label, Literal("VAV-3110 hot-water valve"))

# Zone / space
add(zone, RDF.type, S223.Zone)
add(zone, RDFS.label, Literal("Zone served by VAV-3110"))
add(zone, S223.hasDomain, S223["Domain-HVAC"])
add(zone, S223.hasDomainSpace, zone_ds)
add(zone_ds, RDF.type, S223.DomainSpace)
add(zone_ds, S223.hasDomain, S223["Domain-HVAC"])
add(zone_space, RDF.type, S223.PhysicalSpace)
add(zone_space, RDFS.label, Literal("Physical space of VAV-3110 zone"))
add(zone_space, S223.encloses, zone_ds)

# ---------------------------------------------------------------------------
# Connection points
# ---------------------------------------------------------------------------
# Air side (Fluid-Air)
cp_vav_in = cp(R("cp_vav_primary_in"), S223.InletConnectionPoint, S223["Fluid-Air"], S223["Role-Primary"])
cp_vav_out = cp(R("cp_vav_discharge"), S223.OutletConnectionPoint, S223["Fluid-Air"], S223["Role-Discharge"])
cp_damper_in = cp(R("cp_damper_in"), S223.InletConnectionPoint, S223["Fluid-Air"])
cp_damper_out = cp(R("cp_damper_out"), S223.OutletConnectionPoint, S223["Fluid-Air"])
cp_fan_in = cp(R("cp_fan_in"), S223.InletConnectionPoint, S223["Fluid-Air"])
cp_fan_out = cp(R("cp_fan_out"), S223.OutletConnectionPoint, S223["Fluid-Air"])
cp_coil_in = cp(R("cp_coil_air_in"), S223.InletConnectionPoint, S223["Fluid-Air"])
cp_coil_out = cp(R("cp_coil_air_out"), S223.OutletConnectionPoint, S223["Fluid-Air"])
cp_zone_in = cp(R("cp_zone_in"), S223.InletConnectionPoint, S223["Fluid-Air"])

# Water side (Water-HotWater)
cp_valve_hw_in = cp(R("cp_valve_hw_in"), S223.InletConnectionPoint, S223["Water-HotWater"])
cp_valve_hw_out = cp(R("cp_valve_hw_out"), S223.OutletConnectionPoint, S223["Water-HotWater"])
cp_coil_hw_in = cp(R("cp_coil_hw_in"), S223.InletConnectionPoint, S223["Water-HotWater"])
cp_coil_hw_out = cp(R("cp_coil_hw_out"), S223.OutletConnectionPoint, S223["Water-HotWater"])

# Own the connection points
for equip, cps in [
    (vav, [cp_vav_in, cp_vav_out]),
    (damper, [cp_damper_in, cp_damper_out]),
    (fan, [cp_fan_in, cp_fan_out]),
    (coil, [cp_coil_in, cp_coil_out, cp_coil_hw_in, cp_coil_hw_out]),
    (hwvalve, [cp_valve_hw_in, cp_valve_hw_out]),
    (zone_ds, [cp_zone_in]),
]:
    for c in cps:
        add(equip, S223.hasConnectionPoint, c)

# mapsTo goes from the contained equipment's CP to the container's CP it exposes
# (validated: the mapsTo subject's owner must be contained by the mapsTo object's owner)
add(cp_damper_in, S223.mapsTo, cp_vav_in)
add(cp_coil_out, S223.mapsTo, cp_vav_out)

# ---------------------------------------------------------------------------
# Connections (ducts / pipe) wiring CPs via s223:cnx
# ---------------------------------------------------------------------------
duct_damper_fan = R("duct_damper_to_fan")
duct_fan_coil = R("duct_fan_to_coil")
duct_vav_zone = R("duct_vav_to_zone")
pipe_valve_coil = R("pipe_valve_to_coil")

for d in [duct_damper_fan, duct_fan_coil, duct_vav_zone]:
    add(d, RDF.type, S223.Duct)
    add(d, S223.hasMedium, S223["Fluid-Air"])
add(duct_damper_fan, S223.cnx, cp_damper_out); add(duct_damper_fan, S223.cnx, cp_fan_in)
add(duct_fan_coil, S223.cnx, cp_fan_out); add(duct_fan_coil, S223.cnx, cp_coil_in)
add(duct_vav_zone, S223.cnx, cp_vav_out); add(duct_vav_zone, S223.cnx, cp_zone_in)

add(pipe_valve_coil, RDF.type, S223.Pipe)
add(pipe_valve_coil, S223.hasMedium, S223["Water-HotWater"])
add(pipe_valve_coil, S223.cnx, cp_valve_hw_out); add(pipe_valve_coil, S223.cnx, cp_coil_hw_in)

# ---------------------------------------------------------------------------
# Properties + sensors/commands, anchored to BACnet objects (rdfs:seeAlso)
# ---------------------------------------------------------------------------
BN = lambda oid: URIRef(f"bacnet://3110/{oid}")

# --- Zone temperature (AI,4 zone_temp) ---
p = prop(R("zone_temp"), "Zone Temperature", S223.QuantifiableObservableProperty,
         QK.Temperature, UNIT.DEG_F, "Zone Air Temperature", zone_ds, BN("analog-input,4"))
sensor(R("zone_temp_sensor"), p, zone_ds, "Zone temperature sensor")

# --- Discharge air temperature (AI,2 da_temp) ---
p = prop(R("discharge_air_temp"), "Discharge Air Temperature", S223.QuantifiableObservableProperty,
         QK.Temperature, UNIT.DEG_F, "Discharge Air Temperature", coil, BN("analog-input,2"))
sensor(R("discharge_air_temp_sensor"), p, coil, "Discharge air temperature sensor")

# --- Primary airflow (AI,1 flow_input) ---
p = prop(R("primary_airflow"), "Actual Flow", S223.QuantifiableObservableProperty,
         QK.VolumeFlowRate, UNIT["FT3-PER-MIN"], "Primary airflow", damper, BN("analog-input,1"))
sensor(R("primary_airflow_sensor"), p, damper, "Primary airflow sensor")

# --- Fan airflow (AV,60 fan_airflow) ---
p = prop(R("fan_airflow"), "Fan Airflow", S223.QuantifiableObservableProperty,
         QK.VolumeFlowRate, UNIT["FT3-PER-MIN"], "Series fan airflow", fan, BN("analog-value,60"))
sensor(R("fan_airflow_sensor"), p, fan, "Fan airflow sensor")

# --- Fan status (BI,3 fan_stat) ---
p = prop(R("fan_status"), "Fan Status", S223.EnumeratedObservableProperty,
         desc="Fan run status", owner=fan, see=BN("binary-input,3"),
         enum_kind=S223["Binary-OnOff"])
sensor(R("fan_status_sensor"), p, fan, "Fan status sensor")

# --- Occupancy status (BV,3 occ_status) ---
p = prop(R("occupancy_status"), "Occupancy Status", S223.EnumeratedObservableProperty,
         desc="Zone occupancy status", owner=zone_ds, see=BN("binary-value,3"),
         enum_kind=S223["EnumerationKind-Occupancy"])
sensor(R("occupancy_status_sensor"), p, zone_ds, "Occupancy status sensor")

# --- Fan start/stop command (BO,1 fan) ---
prop(R("fan_start_stop_command"), "Fan Start/Stop", S223.EnumeratedActuatableProperty,
     desc="Fan start/stop command", owner=fan, see=BN("binary-output,1"),
     enum_kind=S223["Binary-OnOff"])

# --- Fan speed command (AO,2 fan_speed) ---
prop(R("fan_speed_command"), "Fan Speed", S223.QuantifiableActuatableProperty,
     QK.DimensionlessRatio, UNIT.PERCENT, "Series fan speed command", fan, BN("analog-output,2"))

# --- Damper position command (AV,24 dmpr_pos) ---
prop(R("damper_position_command"), "Damper Position", S223.QuantifiableActuatableProperty,
     QK.DimensionlessRatio, UNIT.PERCENT, "Damper position command", damper, BN("analog-value,24"))

# --- Hot-water valve command (AO,1 hw_valve) ---
prop(R("hw_valve_command"), "Hot Water Valve", S223.QuantifiableActuatableProperty,
     QK.DimensionlessRatio, UNIT.PERCENT, "Hot-water valve position command", hwvalve, BN("analog-output,1"))

# --- Temperature setpoints (zone) ---
sp = [
    ("occ_cooling_setpoint", "Occupied Cooling Setpoint", "analog-value,1"),
    ("occ_heating_setpoint", "Occupied Heating Setpoint", "analog-value,2"),
    ("unocc_cooling_setpoint", "Unoccupied Cooling Setpoint", "analog-value,3"),
    ("unocc_heating_setpoint", "Unoccupied Heating Setpoint", "analog-value,4"),
    ("effective_cooling_setpoint", "Effective Cool Setpoint", "analog-value,7"),
    ("effective_heating_setpoint", "Effective Heat Setpoint", "analog-value,8"),
]
for local, label, oid in sp:
    prop(R(local), label, S223.QuantifiableActuatableProperty,
         QK.Temperature, UNIT.DEG_F, owner=zone_ds, see=BN(oid))

# --- Airflow setpoint (AV,29 flow_sp) ---
prop(R("airflow_setpoint"), "Airflow Setpoint", S223.QuantifiableActuatableProperty,
     QK.VolumeFlowRate, UNIT["FT3-PER-MIN"], "Discharge airflow setpoint", damper, BN("analog-value,29"))

# ---------------------------------------------------------------------------
# Build the BuildingMOTIF model and validate against 223P shapes
# ---------------------------------------------------------------------------
bm = BuildingMOTIF("sqlite://")
s223_lib = Library.from_ontology(S223_TTL, run_shacl_inference=False)
shapes = s223_lib.get_shape_collection()

model = Model.create(BLDG, description="223P model of BACnet device 3110 (series fan-powered VAV w/ HW reheat)")
model.add_graph(g)
g.serialize(destination=OUT_TTL, format="turtle")
print(f"wrote {OUT_TTL}  ({len(g)} triples)")

ctx = model.validate([shapes], error_on_missing_imports=False)
print("\n== validation ==")
print("valid:", ctx.valid)
violations = ctx.get_reasons_with_severity(SH.Violation)
print(f"violations: {sum(len(v) for v in violations.values())} across {len(violations)} foci")
for focus, fails in violations.items():
    who = str(focus).replace("urn:bldg/", "bldg:") if focus is not None else "(model-level)"
    for f in fails[:6]:
        print(f"  {who}: {f.reason()}")

missing = bm.ontology_environment.missing_imports(model.graph)
if missing:
    print("\nWARNING unresolved imports:", list(missing)[:10])

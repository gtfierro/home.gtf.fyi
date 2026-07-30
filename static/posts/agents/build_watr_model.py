#!/usr/bin/env python3
"""
Build a WaTr (NAWI water-ontology) model of the NAWI advanced-treatment pilot from the
SCADA tags in streams.csv.

Treatment train (order INFERRED from the tag set, flagged for user confirmation):
    Influent(break tank) -> BAF(C1..C4) -> GAC(C1..C4) -> UF -> O3 -> UV/H2O2 -> Chlorination -> Effluent
plus backwash (BW) and chemical-dosing (DP1..4) support subsystems.

Approach (per the buildingmotif skill): map every source tag to verified WaTr/s223
classes + QUDT units, build the graph with direct triples (a point-list build), wire the
train with s223:Pipe topology, then validate against the WaTr+223P shape collections and
iterate.
"""
import csv
import re
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL
from buildingmotif import BuildingMOTIF
from buildingmotif.dataclasses import Library, Model
from buildingmotif.namespaces import S223, QUDT, bind_prefixes

# ---- Namespaces ---------------------------------------------------------
WATR = Namespace("urn:nawi-water-ontology#")
QK = Namespace("http://qudt.org/vocab/quantitykind/")
UNIT = Namespace("http://qudt.org/vocab/unit/")
BLDG = Namespace("urn:nawi-water/")

# ---- Equipment nodes ----------------------------------------------------
EQ = {
    "Influent":          BLDG["Influent"],            # watr:Tank (break tank)
    "BAF":               BLDG["BAF"],                 # watr:UnitProcess (train), contains BAF_C1..4
    "BAF_C1":            BLDG["BAF_C1"], "BAF_C2": BLDG["BAF_C2"],
    "BAF_C3":            BLDG["BAF_C3"], "BAF_C4": BLDG["BAF_C4"],
    "GAC":               BLDG["GAC"],
    "GAC_C1":            BLDG["GAC_C1"], "GAC_C2": BLDG["GAC_C2"],
    "GAC_C3":            BLDG["GAC_C3"], "GAC_C4": BLDG["GAC_C4"],
    "UF":                BLDG["UF"],
    "Ozone":             BLDG["Ozone"],
    "UV_AOP":            BLDG["UV_AOP"],              # composite UV train
    "UV1":               BLDG["UV1"], "UV2": BLDG["UV2"], "UV3": BLDG["UV3"],
    "Chlorination":      BLDG["Chlorination"],
    "Effluent":          BLDG["Effluent"],            # watr:Tank
    "DFO":               BLDG["DFO"],                 # s223:Equipment (sample/monitoring pt; process unconfirmed)
    "DP1": BLDG["DP1"], "DP2": BLDG["DP2"], "DP3": BLDG["DP3"], "DP4": BLDG["DP4"],
    "BW_BackwashPump":   BLDG["BW_BackwashPump"],
    "BW_BackwashTank":  BLDG["BW_BackwashTank"],      # watr:Tank
    "BW_FlowValve":      BLDG["BW_FlowValve"],
    "UF_BackwashPump":   BLDG["UF_BackwashPump"],
    "Influent_FeedPump": BLDG["Influent_FeedPump"],
    "GAC_FeedPump":      BLDG["GAC_FeedPump"],
    "EFF_WastingPump":   BLDG["EFF_WastingPump"],
    "UV_H2O2_Pump":      BLDG["UV_H2O2_Pump"],
    "Effluent_Compressor": BLDG["Effluent_Compressor"],
    "MULT_TOC":          BLDG["MULT_TOC_Analyzer"],
    "RealTech_1":        BLDG["RealTech_1"], "RealTech_2": BLDG["RealTech_2"],
    "ParticleCounter":   BLDG["ParticleCounter"],
    "TOC_Selector":      BLDG["TOC_StreamSelector"],
    "SCADA":             BLDG["SCADA_System"],
}

# ---- Tag -> equipment routing ------------------------------------------
def equip_for(tag):
    t = tag
    if t.startswith("Set_"):
        body = t[4:]
        if body.startswith("UF_"):  return EQ["UF"]
        if body.startswith("BAF_") or body.startswith("Total_BAF_"): return EQ["BAF"]
        if body.startswith("GAC_") or body.startswith("Total_GAC_"): return EQ["GAC"]
        return EQ["SCADA"]
    if t.startswith("INF-"): return EQ["Influent"]
    if t == "External_Influent_Pumps_State": return EQ["Influent_FeedPump"]
    if t.startswith("EFF-"):
        if t.endswith("Wasting_Pump_State"): return EQ["EFF_WastingPump"]
        if t == "EFF-Compressor_Pressure_psi": return EQ["Effluent_Compressor"]
        return EQ["Effluent"]
    if t.startswith("CL2-"): return EQ["Chlorination"]
    if t.startswith("DFO-") or t.startswith("DFW-"): return EQ["DFO"]
    if t.startswith("O3") or t.startswith("Ozone_Dose") or t.startswith("O3:"): return EQ["Ozone"]
    if t == "UV-H2O2_Dosing_Pump_State": return EQ["UV_H2O2_Pump"]
    if t.startswith("UV-"): return EQ["UV_AOP"]
    if re.fullmatch(r"UV[123]_State", t): return EQ["UV" + t[2]]
    if t.startswith("UF-") or t.startswith("UF_"):
        if t == "UF-Backwash_Pump_State": return EQ["UF_BackwashPump"]
        return EQ["UF"]
    if t.startswith("BAF-"):
        m = re.match(r"BAF-C([1-4])", t)
        if m: return EQ["BAF_C" + m.group(1)]
        return EQ["BAF"]
    if re.fullmatch(r"BAF_C([1-4])_State", t):
        return EQ["BAF_C" + re.fullmatch(r"BAF_C([1-4])_State", t).group(1)]
    if t.startswith("GAC-"):
        if t == "GAC-Feed_Pump_State": return EQ["GAC_FeedPump"]
        m = re.match(r"GAC-C([1-4])", t)
        if m: return EQ["GAC_C" + m.group(1)]
        return EQ["GAC"]
    if re.fullmatch(r"GAC_C([1-4])_State", t):
        return EQ["GAC_C" + re.fullmatch(r"GAC_C([1-4])_State", t).group(1)]
    if re.match(r"DP([1-4])(-|_)", t):
        return EQ["DP" + re.match(r"DP([1-4])", t).group(1)]
    if t.startswith("BW-") or t.startswith("BW_"):
        if "Backwash_Pump_State" in t: return EQ["BW_BackwashPump"]
        if "Backwash_Tank_Volume" in t: return EQ["BW_BackwashTank"]
        return EQ["BW_FlowValve"]
    if t.startswith("MULT-"): return EQ["MULT_TOC"]
    if t == "TOC_Remote_Start_State": return EQ["MULT_TOC"]
    if t == "TOTAL_POTABLE_WATER_PRODUCED_gal": return EQ["Effluent"]
    if t.startswith("TOC_Stream_"): return EQ["TOC_Selector"]
    if t.startswith("RealTech_1"): return EQ["RealTech_1"]
    if t.startswith("RealTech_2"): return EQ["RealTech_2"]
    if t.startswith("Particle_Count_"): return EQ["ParticleCounter"]
    if t.startswith("LJ"): return EQ["SCADA"]
    if t in ("SYSTEM_POWER", "HARDWARE_STATE", "Main_24VDC_Power_State",
             "SCADA_Enclosure_Door", "Runtime_hr", "Iteration",
             "net_bytes_recv", "net_bytes_sent", "cpu_percent", "disk_percent",
             "memory_percent", "memory_used_bytes"):
        return EQ["SCADA"]
    return EQ["SCADA"]  # safe default; reported

# ---- QUDT suffix -> (quantitykind, unit) ------------------------------
SUFFIX_MAP = [
    ("count/mL", (QK.NumberDensity, UNIT["NUM-PER-MilliL"])),
    ("mW/cm^2",  (QK.PowerPerArea, UNIT["MilliW-PER-M2"])),   # exact cm^-2 unit absent; flagged
    ("mg/L",    (QK.MassConcentration, UNIT["MilliGM-PER-L"])),
    ("ppmv",    (QK.VolumeFraction, UNIT["PPM"])),
    ("ppb",     (QK.VolumeFraction, UNIT["PPB"])),
    ("ppm",     (QK.MassConcentration, UNIT["MilliGM-PER-L"])),  # aqueous ppm ~ mg/L
    ("GPM",     (QK.VolumeFlowRate, UNIT["GAL_US-PER-MIN"])),
    ("mL/min",  (QK.VolumeFlowRate, UNIT["MilliL-PER-MIN"])),
    ("psi",     (QK.Pressure, UNIT["PSI"])),
    ("NTU",     (QK.Turbidity, UNIT["NTU"])),
    ("_C",      (QK.Temperature, UNIT["DEG_C"])),
    ("_%",      (QK.DimensionlessRatio, UNIT["PERCENT"])),
    ("_gal",    (QK.Volume, UNIT["GAL_US"])),
    ("_ft",     (QK.Length, UNIT["FT"])),
    ("_s",      (QK.Time, UNIT["SEC"])),
    ("min",     (QK.Time, UNIT["MIN"])),
    ("hr",      (QK.Time, UNIT["HR"])),
    ("_V",      (QK.Voltage, UNIT["V"])),
    ("_A",      (QK.ElectricCurrent, UNIT["A"])),
]

def qudt_for(tag):
    for suf, (qk, u) in SUFFIX_MAP:
        if tag.endswith(suf):
            return qk, u
    return None, None

# ---- constituent / sensor selection (content-driven) ------------------
def substance_sensor_for(tag):
    low = tag.lower()
    if "toc" in low and "no2" not in low: return WATR["Constituent-OrganicCarbon"], WATR.TotalOrganicCompoundConcentrationSensor
    if "tic" in low: return WATR["Constituent-InorganicCarbon"], WATR.ConcentrationSensor
    if "nitrite" in low: return WATR["Constituent-Nitrite"], WATR.ConcentrationSensor
    if "nitrate" in low: return WATR["Constituent-Nitrate"], WATR.ConcentrationSensor
    if "ammonia" in low: return WATR["Constituent-Ammonia"], WATR.ConcentrationSensor
    if "nox" in low: return WATR["Constituent-NitrogenOxides"], WATR.ConcentrationSensor
    if "dissolved_oxygen" in low: return WATR["Constituent-DissolvedOxygen"], WATR.OxygenMeter
    if "chlorine" in low: return WATR["Disinfectant-Chlorine"], WATR.ConcentrationSensor
    if low.startswith("o3") or "ozone" in low or "offgas" in low:
        return WATR["Disinfectant-Ozone"], WATR.ConcentrationSensor
    if "particle_count" in low: return WATR["Constituent-Particles"], WATR.ConcentrationSensor
    if "turbidity" in low: return WATR["Constituent-SuspendedSolids"], WATR.TurbidityMeter
    if "flow" in low or "flowrate" in low: return None, WATR.FlowSensor
    if "pressure" in low: return None, WATR.PressureSensor
    if "temperature" in low: return None, WATR.TemperatureSensor
    if "level" in low: return None, WATR.LevelSensor
    if "volume" in low and not low.startswith("set_"): return None, WATR.VolumeSensor
    if "ph" in re.sub(r"[\W_]+", "", low): return None, WATR.pHSensor
    if "uvt" in low: return None, S223.Sensor
    if "ultraviolet" in low or "uv_" in low: return None, S223.Sensor
    if "current_draw" in low: return None, S223.Sensor
    if "current_draw" in low: return None, S223.Sensor
    if low.endswith("_v") or "dac" in low: return None, S223.Sensor
    if "runtime" in low or "iteration" in low or "bytes" in low or "percent" in low:
        return None, S223.Sensor
    return None, S223.Sensor

# ---- enumerated-pattern detection --------------------------------------
ENUM_OBS_PATTERNS = ("_state", "running", "fault", "door", "auto_override",
                     "system_power", "hardware_state", "reactor_state", "ozone_state")
ENUM_ACT_PATTERNS = ("start/stop", "on/off")

def is_enum_obs(tag):
    low = tag.lower()
    return any(p in low for p in ENUM_OBS_PATTERNS)
def is_enum_act(tag):
    low = tag.lower()
    return any(p in low for p in ENUM_ACT_PATTERNS)

# =======================================================================
# Build
# =======================================================================
def main():
    bm = BuildingMOTIF("sqlite://")
    print("loading 223p + watr ...")
    s223lib = Library.from_ontology("ontologies/223p.ttl", run_shacl_inference=False)
    watrlib = Library.from_ontology("ontologies/water.ttl", run_shacl_inference=False)
    scs = [s223lib.get_shape_collection(), watrlib.get_shape_collection()]

    model = Model.create(BLDG, description="NAWI advanced-treatment pilot WaTr model from SCADA tags")
    g = model.graph
    WATER = S223["Fluid-Water"]

    def nid(s): return re.sub(r"[^A-Za-z0-9_]", "_", s)

    # ---- 1. Equipment typing & process assignment ----------------------
    def proc(eq, p): g.add((eq, WATR.hasProcess, p))
    g.add((EQ["Influent"], RDF.type, WATR.Tank))
    g.add((EQ["Effluent"], RDF.type, WATR.Tank))
    g.add((EQ["BW_BackwashTank"], RDF.type, WATR.Tank))
    # BAF train + columns
    g.add((EQ["BAF"], RDF.type, WATR.UnitProcess)); proc(EQ["BAF"], WATR["Process-BiologicallyActiveFiltration"])
    for c in ("BAF_C1", "BAF_C2", "BAF_C3", "BAF_C4"):
        g.add((EQ[c], RDF.type, WATR.BiologicalAeratedFilter)); proc(EQ[c], WATR["Process-BiologicallyActiveFiltration"])
        g.add((EQ["BAF"], S223.contains, EQ[c]))
    # GAC train + columns
    g.add((EQ["GAC"], RDF.type, WATR.UnitProcess)); proc(EQ["GAC"], WATR["Process-GranularActivatedCarbon"])
    for c in ("GAC_C1", "GAC_C2", "GAC_C3", "GAC_C4"):
        g.add((EQ[c], RDF.type, WATR.GranularActivatedCarbonAdsorber)); proc(EQ[c], WATR["Process-GranularActivatedCarbon"])
        g.add((EQ["GAC"], S223.contains, EQ[c]))
    # UF
    g.add((EQ["UF"], RDF.type, WATR.UltrafiltrationUnit)); proc(EQ["UF"], WATR["Process-Ultrafiltration"])
    # Ozone
    g.add((EQ["Ozone"], RDF.type, WATR.OzonationUnit)); proc(EQ["Ozone"], WATR["Process-Ozonation"])
    # UV/H2O2 composite + 3 reactors
    g.add((EQ["UV_AOP"], RDF.type, WATR.UnitProcess)); proc(EQ["UV_AOP"], WATR["Process-AdvancedOxidation"])
    for u in ("UV1", "UV2", "UV3"):
        g.add((EQ[u], RDF.type, WATR.UVH2O2Reactor)); proc(EQ[u], WATR["Process-AdvancedOxidation"])
        g.add((EQ["UV_AOP"], S223.contains, EQ[u]))
    # Chlorination
    g.add((EQ["Chlorination"], RDF.type, WATR.ChlorinationUnit)); proc(EQ["Chlorination"], WATR["Process-Chlorination"])
    # DFO sample/monitoring point (process deliberately NOT asserted -- unconfirmed)
    g.add((EQ["DFO"], RDF.type, S223.Equipment))
    # Pumps
    for dp in ("DP1", "DP2", "DP3", "DP4"):
        g.add((EQ[dp], RDF.type, WATR.Pump)); proc(EQ[dp], WATR["Process-ChemicalAddition"])
    g.add((EQ["BW_BackwashPump"], RDF.type, WATR.Pump)); proc(EQ["BW_BackwashPump"], WATR["Process-Backwashing"])
    g.add((EQ["UF_BackwashPump"], RDF.type, WATR.Pump)); proc(EQ["UF_BackwashPump"], WATR["Process-Backwashing"])
    g.add((EQ["Influent_FeedPump"], RDF.type, WATR.Pump))
    g.add((EQ["GAC_FeedPump"], RDF.type, WATR.Pump))
    g.add((EQ["EFF_WastingPump"], RDF.type, WATR.Pump))
    g.add((EQ["UV_H2O2_Pump"], RDF.type, WATR.Pump)); proc(EQ["UV_H2O2_Pump"], WATR["Process-ChemicalAddition"])
    # plain s223 support equipment (no process required)
    for k in ("BW_FlowValve", "Effluent_Compressor", "MULT_TOC", "RealTech_1", "RealTech_2",
              "ParticleCounter", "TOC_Selector", "SCADA"):
        g.add((EQ[k], RDF.type, S223.Equipment))

    # ---- 2. Connected train topology -----------------------------------
    def cp(equip, name, direction):
        node = BLDG[nid(str(equip).split("/")[-1] + "_" + name)]
        g.add((node, RDF.type, S223.InletConnectionPoint if direction == "in" else S223.OutletConnectionPoint))
        g.add((node, S223.hasMedium, WATER))
        g.add((node, S223.isConnectionPointOf, equip))
        g.add((equip, S223.hasConnectionPoint, node))
        return node

    def sub_ports(sub_equip, comp_in, comp_out, label):
        """Required inlet+outlet CPs on a contained sub-equipment (parallel column).
        Each column carries its own ports; they are not manifolded to the composite's
        single train port (223 mapsTo is 1:1), so the composite holds the train flow
        while columns are represented as parallel contained equipment."""
        cp(sub_equip, label + "_in", "in")
        cp(sub_equip, label + "_out", "out")

    def pipe(a_cp, b_cp, label):
        p = BLDG["pipe_" + nid(label)]
        g.add((p, RDF.type, S223.Pipe))
        g.add((p, S223.hasMedium, WATER))
        g.add((p, S223.cnx, a_cp)); g.add((p, S223.cnx, b_cp))
        g.add((p, S223.connectsAt, a_cp)); g.add((p, S223.connectsAt, b_cp))
        return p

    def plug(cp_node, label):
        pl = BLDG["plug_" + nid(label)]
        g.add((pl, RDF.type, S223.Connectable))
        g.add((cp_node, S223.cnx, pl)); g.add((cp_node, S223.connectsAt, pl))

    infl_in = cp(EQ["Influent"], "in", "in"); infl_out = cp(EQ["Influent"], "out", "out")
    baf_in = cp(EQ["BAF"], "in", "in"); baf_out = cp(EQ["BAF"], "out", "out")
    gac_in = cp(EQ["GAC"], "in", "in"); gac_out = cp(EQ["GAC"], "out", "out")
    uf_in = cp(EQ["UF"], "feed", "in"); uf_perm = cp(EQ["UF"], "permeate", "out"); uf_rej = cp(EQ["UF"], "reject", "out")
    o3_in = cp(EQ["Ozone"], "in", "in"); o3_out = cp(EQ["Ozone"], "out", "out")
    uv_in = cp(EQ["UV_AOP"], "in", "in"); uv_out = cp(EQ["UV_AOP"], "out", "out")
    cl_in = cp(EQ["Chlorination"], "in", "in"); cl_out = cp(EQ["Chlorination"], "out", "out")
    eff_in = cp(EQ["Effluent"], "in", "in"); eff_out = cp(EQ["Effluent"], "out", "out")
    bwtk_in = cp(EQ["BW_BackwashTank"], "in", "in"); bwtk_out = cp(EQ["BW_BackwashTank"], "out", "out")

    # contained columns/reactors: required inlet+outlet CPs that map to the composite ports
    for i, c in enumerate(("BAF_C1", "BAF_C2", "BAF_C3", "BAF_C4"), 1):
        sub_ports(EQ[c], baf_in, baf_out, "c%d" % i)
    for i, c in enumerate(("GAC_C1", "GAC_C2", "GAC_C3", "GAC_C4"), 1):
        sub_ports(EQ[c], gac_in, gac_out, "c%d" % i)
    for u in ("UV1", "UV2", "UV3"):
        sub_ports(EQ[u], uv_in, uv_out, u.lower())
    # pumps: required inlet+outlet CPs (water medium; not wired into the train)
    for k in ("DP1", "DP2", "DP3", "DP4", "BW_BackwashPump", "UF_BackwashPump",
             "Influent_FeedPump", "GAC_FeedPump", "EFF_WastingPump", "UV_H2O2_Pump"):
        cp(EQ[k], "in", "in"); cp(EQ[k], "out", "out")

    pipe(infl_out, baf_in, "infl_to_baf")
    pipe(baf_out, gac_in, "baf_to_gac")
    pipe(gac_out, uf_in, "gac_to_uf")
    pipe(uf_perm, o3_in, "uf_to_o3")
    # uf_rej, infl_in, eff_out, bwtk_in/out are left deliberately unconnected (boundary
    # ports); validation does not require every connection point to be wired.
    pipe(o3_out, uv_in, "o3_to_uv")
    pipe(uv_out, cl_in, "uv_to_cl2")
    pipe(cl_out, eff_in, "cl2_to_eff")

    # ---- 3. Map tags to properties + sensors ---------------------------
    HW_TAGS = []
    mapped = 0
    unresolved = []
    counts = {}

    def add_sensor(prop, sensor_cls, equip):
        s = BLDG[nid(str(prop).split("/")[-1] + "_sensor")]
        g.add((s, RDF.type, sensor_cls))
        g.add((s, S223.observes, prop))
        g.add((s, S223.hasObservationLocation, equip))
        return s

    with open("streams.csv", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        tag = r["ref_name"]
        equip = equip_for(tag)
        counts[str(equip).split("/")[-1]] = counts.get(str(equip).split("/")[-1], 0) + 1
        if equip == EQ["SCADA"]:
            HW_TAGS.append(tag)
        pnode = BLDG[nid(tag)]
        g.add((pnode, RDFS.label, Literal(tag)))
        g.add((equip, S223.hasProperty, pnode))

        is_quant_act = (tag.startswith("Set_") and not tag.endswith("ON/OFF")) \
            or tag.endswith("-Speed_%") or tag.endswith("Flow_Valve_%")
        calculated = (tag == "O3:TOC+NO2_Ratio")

        enum_kind = None
        if "fault" in tag.lower():
            enum_kind = S223["Aspect-Fault"]
        elif is_enum_act(tag) or (tag.startswith("Set_") and tag.endswith("ON/OFF")) or is_enum_obs(tag):
            enum_kind = S223["Binary-OnOff"]

        if is_enum_act(tag) or (tag.startswith("Set_") and tag.endswith("ON/OFF")):
            g.add((pnode, RDF.type, S223.EnumeratedActuatableProperty))
            g.add((pnode, S223.hasEnumerationKind, enum_kind))
            g.add((equip, S223.actuatedByProperty, pnode))
            mapped += 1; continue
        if is_enum_obs(tag):
            g.add((pnode, RDF.type, S223.EnumeratedObservableProperty))
            g.add((pnode, S223.hasEnumerationKind, enum_kind))
            add_sensor(pnode, S223.Sensor, equip); mapped += 1; continue
        # quantifiable
        qk, u = qudt_for(tag)
        substance, sensor_cls = substance_sensor_for(tag)
        if calculated:
            g.add((pnode, RDF.type, S223.QuantifiableProperty))
        elif is_quant_act:
            g.add((pnode, RDF.type, S223.QuantifiableActuatableProperty))
            g.add((equip, S223.actuatedByProperty, pnode))
        else:
            g.add((pnode, RDF.type, S223.QuantifiableObservableProperty))
        if qk is None:
            qk = QK.DimensionlessRatio  # iteration counts, byte counts, ratios, UVT, etc.
        g.add((pnode, QUDT.hasQuantityKind, qk))
        if u is not None:
            g.add((pnode, QUDT.hasUnit, u))
        if substance is not None:
            g.add((pnode, S223.ofSubstance, substance))
            g.add((pnode, S223.ofMedium, WATER))
        if not is_quant_act and not calculated:
            add_sensor(pnode, sensor_cls, equip)
        mapped += 1

    # ---- 4. Validate ---------------------------------------------------
    print(f"\nmapped {mapped} tags; equipment nodes: {len(counts)}")
    print("SCADA/hardware tags routed to SCADA_System:", len(HW_TAGS))
    ctx = model.validate(scs, error_on_missing_imports=False)
    print("\nVALID:", ctx.valid)
    if not ctx.valid:
        n = 0
        for w in ctx.diffset:
            print("  FAIL:", w.reason() if hasattr(w, "reason") else w)
            n += 1
            if n >= 60:
                print("  ... (truncated)")
                break

    # ---- 5. Serialize ---------------------------------------------------
    g.bind("watr", WATR); g.bind("s223", S223); g.bind("qudt", QUDT)
    g.bind("quantitykind", QK); g.bind("unit", UNIT); g.bind("bldg", BLDG)
    model.graph.serialize(destination="watr_model.ttl", format="turtle")
    print("\nwrote watr_model.ttl  (", len(g), "triples )")
    print("\n== tags per equipment ==")
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {v:3d}  {k}")
    print("\n== SCADA/hardware tags (modeled as SCADA_System properties, reported separately) ==")
    for t in HW_TAGS:
        print("   ", t)
    print("\n== NOTE: treatment-train order is INFERRED from the tag set and needs confirmation. ==")
    print("== NOTE: DFO/DFW modeled as a plain s223:Equipment sample point (process unconfirmed). ==")
    print("== NOTE: UV intensity uses unit:MilliW-PER-M2 (exact MilliW-PER-CentiM2 absent in QUDT). ==")

if __name__ == "__main__":
    main()

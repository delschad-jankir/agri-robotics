"""Konstruktionsprüfung wie bei einer Design-Review:
1. Schweißbaugruppen = genau ein zusammenhängender Körper
2. Kollision aller Teilepaare in Ruhelage (Durchdringung > TOL_VOL mm^3)
3. Verbindungen: jede definierte Verbindung hat geometrischen Kontakt (Abstand <= TOL_CONTACT)
4. Freischwebende Teile: alle Teile über Verbindungen mit dem Rahmen verbunden
5. Bodenkontakt: alle vier Reifen stehen auf z=0, kein anderes Teil unter Bodenfreiheit
6. Kinematik: Kollisionsfreiheit über den gesamten Kippweg (Schrittweite STEP Grad)
7. Masse, Schwerpunkt, Standsicherheit (eben/Hang) und Zylinderkraft über den Kippweg
Ergebnis: out/check_report.json + Konsolenausgabe. Exit-Code 1 bei Fehlern."""
import json, math, sys, time, itertools
from collections import defaultdict
import numpy as np
from model import build_all, joints, build_payload, P
import kin

TOL_VOL = 1.0         # mm^3
TOL_CONTACT = 0.3     # mm
STEP = 2.5            # Grad
THETA_STOP = 55.0     # mechanischer Anschlag (Soll-Kippwinkel)
PAYLOAD_DENSITY = 750  # kg/m^3 (nasser Pferdemist mit Stroh, konservativ)
MIN_GROUND = 120      # mm Mindest-Bodenfreiheit (außer Reifen/Bumper)


def bb_overlap(a, b, m=0.5):
    A, B = a.bounding_box(), b.bounding_box()
    return not (A.max.X < B.min.X - m or B.max.X < A.min.X - m or A.max.Y < B.min.Y - m or
                B.max.Y < A.min.Y - m or A.max.Z < B.min.Z - m or B.max.Z < A.min.Z - m)


def inter_vol(a, b):
    try:
        c = a & b
        return c.volume if c is not None else 0.0
    except Exception as e:
        return -1.0


def main():
    t0 = time.time()
    rep = {"errors": [], "warnings": []}
    parts = build_all()
    byname = {p.name: p for p in parts}
    print(f"{len(parts)} Teile aufgebaut ({time.time()-t0:.1f}s)")

    # 1 Schweißbaugruppen
    for p in parts:
        n = len(p.shape.solids())
        if n != 1:
            rep["errors"].append(f"'{p.name}' besteht aus {n} getrennten Körpern (freischwebendes Element)")
    print("1 Einkörperprüfung fertig")

    # 2 Kollisionen in Ruhelage
    jset = {frozenset((a, b)) for a, b, _ in joints()}
    coll = []
    for a, b in itertools.combinations(parts, 2):
        if not bb_overlap(a.shape, b.shape):
            continue
        v = inter_vol(a.shape, b.shape)
        if v > TOL_VOL or v < 0:
            coll.append((a.name, b.name, round(v, 1)))
    for c in coll:
        rep["errors"].append(f"Kollision Ruhelage: {c[0]} <-> {c[1]}: {c[2]} mm³")
    rep["collisions_rest"] = coll
    print(f"2 Kollisionen Ruhelage: {len(coll)}")

    # 3 Verbindungen
    jres = []
    for a, b, kind in joints():
        d = byname[a].shape.distance_to(byname[b].shape)
        ok = d <= TOL_CONTACT
        jres.append({"a": a, "b": b, "art": kind, "abstand_mm": round(d, 3), "ok": ok})
        if not ok:
            rep["errors"].append(f"Verbindung ohne Kontakt: {a} <-> {b} ({kind}), Abstand {d:.2f} mm")
    rep["joints"] = jres
    print(f"3 Verbindungen: {sum(j['ok'] for j in jres)}/{len(jres)} mit Kontakt")

    # 4 Zusammenhang
    g = defaultdict(set)
    for j in jres:
        if j["ok"]:
            g[j["a"]].add(j["b"]); g[j["b"]].add(j["a"])
    seen, stack = set(), ["Rahmen (Schweißbaugruppe)"]
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n); stack += list(g[n])
    floating = [p.name for p in parts if p.name not in seen]
    for f in floating:
        rep["errors"].append(f"Freischwebendes Teil (keine Verbindung zum Rahmen): {f}")
    rep["floating"] = floating
    print(f"4 Freischwebende Teile: {len(floating)}")

    # 5 Boden
    gnd = {}
    for p in parts:
        zmin = p.shape.bounding_box().min.Z
        gnd[p.name] = zmin
        if p.name.startswith("Reifen") and abs(zmin) > 1.0:
            rep["errors"].append(f"{p.name} steht nicht auf dem Boden (z_min={zmin:.1f})")
        if not p.name.startswith(("Reifen", "Felge", "Bumper")) and zmin < MIN_GROUND:
            rep["warnings"].append(f"Bodenfreiheit {p.name}: {zmin:.0f} mm < {MIN_GROUND} mm")
    rep["ground_clearance_mm"] = round(min(v for k, v in gnd.items() if not k.startswith(("Reifen", "Felge", "Bumper"))), 1)
    print(f"5 Bodenfreiheit min (ohne Räder/Bumper): {rep['ground_clearance_mm']} mm")

    # 5b Teleskopzylinder: Führungsüberdeckung jeder Stufe bei vollem Hub (Soll >= 50 mm)
    Lr, n = P["cyl_retracted"], len(P["cyl_r"]) - 1
    tops = [Lr - 70 + 10 * i for i in range(n)]
    bottoms = [60 + 25 + 10 * i for i in range(1, n + 1)]
    ov = [tops[i - 1] - (bottoms[i - 1] + P["cyl_stage_stroke"]) for i in range(1, n + 1)]
    rep["cyl_overlap_mm"] = ov
    if min(ov) < 50:
        rep["errors"].append(f"Teleskopzylinder: Führungsüberdeckung nur {min(ov)} mm (< 50 mm)")
    print(f"5b Zylinder-Überdeckung min {min(ov)} mm")

    # 6 Kinematik
    th_geo = kin.theta_max_geom()
    th_end = min(th_geo, THETA_STOP)
    rep["theta_max_cylinder_deg"] = round(th_geo, 2)
    rep["theta_stop_deg"] = th_end
    if th_geo < THETA_STOP:
        rep["errors"].append(f"Zylinderhub reicht nur für {th_geo:.1f}° < Soll {THETA_STOP}°")
    moving = [p for p in parts if p.group in ("hopper", "gate") or p.group.startswith("cyl")]
    fixed = [p for p in parts if p not in moving]
    sweep = []
    thetas = list(np.arange(0, th_end + 1e-6, STEP))
    if thetas[-1] < th_end:
        thetas.append(th_end)
    for th in thetas:
        M = kin.poses(th)
        mv = {p.name: kin.posed(p.shape, M[p.group]) for p in moving}
        hits = []
        pairs = [(a, b) for a in moving for b in fixed] + list(itertools.combinations(moving, 2))
        for a, b in pairs:
            if a.group == b.group or frozenset((a.name, b.name)) in jset:
                continue
            sa = mv[a.name]
            sb = mv.get(b.name, b.shape)
            if not bb_overlap(sa, sb):
                continue
            v = inter_vol(sa, sb)
            if v > TOL_VOL or v < 0:
                hits.append((a.name, b.name, round(v, 1)))
        zmin = min(s.bounding_box().min.Z for s in mv.values())
        # Mindestabstände kritischer Paare
        clr = {
            "Mulde-Reifen": min(mv["Mulde (Schweißbaugruppe)"].distance_to(byname[f"Reifen {t}"].shape) for t in ("VL", "HL")),
            "Zylinder-Mulde": min(mv[f"Teleskopzylinder Stufe {i}"].distance_to(mv["Mulde (Schweißbaugruppe)"]) for i in range(4)),
            "Klappe-Rahmen": mv["Heckklappe (Pendelklappe)"].distance_to(byname["Rahmen (Schweißbaugruppe)"].shape),
            "Mulde-Technikbox": min(mv["Mulde (Schweißbaugruppe)"].distance_to(byname[n].shape) for n in
                                    ("Akkugehäuse (LiFePO4 48 V 100 Ah)", "Steuerungs-/Hydraulikgehäuse")),
        }
        sweep.append({"theta": round(float(th), 2), "collisions": hits, "zmin_moving": round(zmin, 1),
                      "clearance": {k: round(v, 1) for k, v in clr.items()}})
        for h in hits:
            rep["errors"].append(f"Kollision bei {th:.1f}°: {h[0]} <-> {h[1]}: {h[2]} mm³")
        if zmin < 0:
            rep["errors"].append(f"Bewegtes Teil unter Boden bei {th:.1f}° (z={zmin:.0f})")
        print(f"   θ={th:5.1f}°  Kollisionen={len(hits)}  zmin={zmin:6.0f}  " +
              "  ".join(f"{k}={v:.0f}" for k, v in clr.items()))
    rep["sweep"] = sweep
    print("6 Kinematik fertig")

    # 7 Massen / Schwerpunkt / Stabilität / Zylinderkraft
    def mass_cg(p, shape=None):
        s = shape or p.shape
        if p.mass_kg is not None:
            m = p.mass_kg
        else:
            m = s.volume * 1e-9 * p.density
        c = s.center()
        return m, np.array([c.X, c.Y, c.Z])
    masses = []
    for p in parts:
        m, c = mass_cg(p)
        masses.append({"teil": p.name, "gruppe": p.group, "masse_kg": round(m, 2), "sp_mm": [round(v, 1) for v in c]})
    rep["masses"] = masses
    m_veh = sum(x["masse_kg"] for x in masses)
    payload = build_payload()
    vol_m3 = payload.volume * 1e-9
    m_pay = vol_m3 * PAYLOAD_DENSITY
    pc = payload.center(); c_pay0 = np.array([pc.X, pc.Y, pc.Z])
    rep["vehicle_mass_kg"] = round(m_veh, 1)
    rep["payload"] = {"volumen_m3": round(vol_m3, 3), "dichte": PAYLOAD_DENSITY, "masse_kg": round(m_pay, 1),
                      "sp_mm": [round(v, 1) for v in c_pay0]}
    print(f"7 Fahrzeugmasse {m_veh:.0f} kg, Ladung {vol_m3*1000:.0f} l ≈ {m_pay:.0f} kg")

    xf, xr, yw = P["x_front"], P["x_rear"], P["wheel_y"]
    stab = []
    Lmax = P["cyl_retracted"] + P["cyl_stroke"]
    for th in thetas:
        M = kin.poses(th)
        tot_m, tot_mc = 0.0, np.zeros(3)
        mom = 0.0  # Moment um Kippachse (Nmm), positiv = senkt Mulde
        for x in masses:
            p = byname[x["teil"]]
            c = kin.apply(M[p.group], x["sp_mm"])
            tot_m += x["masse_kg"]; tot_mc += x["masse_kg"] * c
            if p.group in ("hopper", "gate"):
                mom += x["masse_kg"] * 9.81 * (c[0] - P["pivot_x"])
        cp = kin.apply(M["hopper"], c_pay0)
        mom_l = mom + m_pay * 9.81 * (cp[0] - P["pivot_x"])
        tot_ml, cg_l = tot_m + m_pay, (tot_mc + m_pay * cp) / (tot_m + m_pay)
        cg_e = tot_mc / tot_m
        # Zylinderkraft per virtueller Arbeit: F = M / (dL/dθ)
        d = 0.05
        dL = (kin.cyl_length(th + d) - kin.cyl_length(max(th - d, 0))) / math.radians(th + d - max(th - d, 0))
        F_l = mom_l / dL if dL > 0 else float("nan")
        F_e = mom / dL if dL > 0 else float("nan")
        def margins(cg):
            return {"vorn": xf - cg[0], "hinten": cg[0] - xr, "seite": yw - abs(cg[1]), "h": cg[2]}
        ml, me = margins(cg_l), margins(cg_e)
        stab.append({"theta": round(float(th), 2), "cg_beladen": [round(v, 1) for v in cg_l],
                     "cg_leer": [round(v, 1) for v in cg_e],
                     "kippgrenze_beladen_deg": {k: round(math.degrees(math.atan(ml[k] / ml["h"])), 1) for k in ("vorn", "hinten", "seite")},
                     "kippgrenze_leer_deg": {k: round(math.degrees(math.atan(me[k] / me["h"])), 1) for k in ("vorn", "hinten", "seite")},
                     "zylinderkraft_beladen_N": round(F_l, 0), "zylinderkraft_leer_N": round(F_e, 0),
                     "zylinderlaenge_mm": round(kin.cyl_length(th), 1)})
        if F_e <= 0:
            rep["warnings"].append(f"Leere Mulde senkt bei {th:.1f}° nicht selbständig ab (Rückstellmoment ≤ 0)")
    rep["stability"] = stab
    rep["mass_total_loaded_kg"] = round(m_veh + m_pay, 1)
    for s in stab:
        k = s["kippgrenze_beladen_deg"]
        if min(k.values()) < 8.5:
            rep["warnings"].append(f"θ={s['theta']}°: statische Kippgrenze beladen nur {min(k.values())}° (< 8,5° ≙ 15 %)")
    rep["runtime_s"] = round(time.time() - t0, 1)
    json.dump(rep, open("../out/check_report.json", "w"), indent=1, ensure_ascii=False)
    print("\n=== ERGEBNIS ===")
    print(f"Fehler: {len(rep['errors'])}   Warnungen: {len(rep['warnings'])}")
    for e in rep["errors"]:
        print("  FEHLER  ", e)
    for w in rep["warnings"]:
        print("  WARNUNG ", w)
    s0, s1 = stab[0], stab[-1]
    print(f"Kippgrenzen beladen θ=0: {s0['kippgrenze_beladen_deg']}, θ={s1['theta']}: {s1['kippgrenze_beladen_deg']}")
    print(f"Zylinderkraft beladen max {max(s['zylinderkraft_beladen_N'] for s in stab):.0f} N")
    return 1 if rep["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())

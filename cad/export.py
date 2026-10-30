"""Export: STEP-Baugruppe (für Fusion 360 / jedes CAD), STL je Teil + meta.json für den Renderer,
Posen-Tabellen für Animationen."""
import json, os, math
import numpy as np
from build123d import Compound, Color, export_step, export_stl
from model import build_all, build_payload, P, COL
import kin

OUT = "../out"
os.makedirs(f"{OUT}/stl", exist_ok=True)


def safe(n):
    return "".join(c if c.isalnum() else "_" for c in n.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss").replace("Ø", "D"))


def ascii_label(n):
    """STEP-Namen nur ASCII (Fusion zeigt Umlaute sonst falsch an)."""
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("Ä", "Ae"), ("Ö", "Oe"), ("Ü", "Ue"), ("ß", "ss"), ("Ø", "D"), ("°", "deg")):
        n = n.replace(a, b)
    return n.encode("ascii", "ignore").decode()


def main():
    parts = build_all()
    payload = build_payload()
    meta = []
    children = []
    for p in parts:
        fn = safe(p.name) + ".stl"
        export_stl(p.shape, f"{OUT}/stl/{fn}", tolerance=0.3, angular_tolerance=0.2)
        meta.append({"name": p.name, "file": fn, "group": p.group, "color": COL[p.color], "colorKey": p.color})
        s = p.shape
        s.label = ascii_label(p.name)
        s.color = Color(*COL[p.color])
        children.append(s)
    export_stl(payload, f"{OUT}/stl/payload.stl", tolerance=0.5, angular_tolerance=0.3)
    meta.append({"name": "Ladung (Mist)", "file": "payload.stl", "group": "hopper", "color": COL["payload"], "colorKey": "payload"})
    asm = Compound(children=children, label="Mist-Shuttle V1 (Konzept)")
    export_step(asm, f"{OUT}/mist_shuttle_v1.step")
    # Posen: Kippwinkel 0..55 in 0.5°-Schritten
    th = kin.theta_max_geom()
    stop = min(th, 55.0)
    table = {}
    for t in np.arange(0, stop + 1e-9, 0.5):
        M = kin.poses(float(t))
        table[f"{t:.1f}"] = {k: v.tolist() for k, v in M.items() if not k.startswith("wheel")}
    info = {"parts": meta, "theta_stop": stop, "pivot": [P["pivot_x"], P["pivot_z"]],
            "wheels": {k: [x, P["wheel_r"]] for k, x in (("VL", P["x_front"]), ("HL", P["x_rear"]), ("VR", P["x_front"]), ("HR", P["x_rear"]))},
            "poses": table}
    json.dump(info, open(f"{OUT}/meta.json", "w"))
    print("STEP + STL exportiert:", len(meta), "Teile, Kippwinkel bis", stop)


if __name__ == "__main__":
    main()

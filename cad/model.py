"""Parametrisches Konzeptmodell "Mist-Shuttle" (Kippmulde, Variante 1).

Koordinaten (mm): X = Fahrtrichtung vorn (Technikseite), Y = links, Z = oben, Boden z = 0.
Alle Teile werden in Ruhelage (Mulde abgesenkt) in Weltkoordinaten modelliert.
Schweißbaugruppen (Rahmen, Mulde, Heckklappe) sind je EIN Teil; check.py prüft, dass sie
aus genau einem zusammenhängenden Volumenkörper bestehen.
"""
import math
from dataclasses import dataclass, field
from build123d import (Box, Cylinder, Cone, Location, Rotation, Polygon, Plane, extrude,
                       fillet, Axis, Solid, Part, Sphere, Compound)

# ---------------------------------------------------------------- Parameter
P = dict(
    # Räder (Bereifung 4.00-8 / Ø400)
    wheel_r=200.0, wheel_w=90.0, wheel_y=350.0, x_front=400.0, x_rear=-400.0,
    rim_r=102.0,
    # Rahmen: Längsträger Rechteckrohr 60x40x3, Querträger 40x40x3
    rail_y_in=230.0, rail_y_out=270.0, rail_z0=170.0, rail_z1=230.0,
    frame_x0=-720.0, frame_x1=760.0, tube_t=3.0,
    # Kipplager (Drehpunkt Mulde)
    pivot_x=-690.0, pivot_z=260.0, pivot_d=25.0,
    # Mulde
    hop_x0=-700.0, hop_x1=350.0, hop_floor_z=280.0, hop_top_z=820.0, hop_front_top_x=470.0,
    hop_y_floor=260.0, hop_y_wall=305.0, hop_z_knee=430.0, sheet=3.0, floor_t=4.0,
    # Teleskopzylinder (4-stufig, Ø91/76/61/46)
    cyl_x=575.0, cyl_base_z=215.0, cyl_retracted=513.0, cyl_stage_stroke=285.0,
    cyl_r=(55.0, 45.5, 38.0, 30.5, 23.0),  # Gehäuse + 4 Stufen Ø91/76/61/46
    # Heckklappe
    gate_hinge_x=-712.0, gate_hinge_z=808.0,
)
P["cyl_top_z"] = P["cyl_base_z"] + P["cyl_retracted"]
P["cyl_stroke"] = 4 * P["cyl_stage_stroke"]  # 4 ausfahrende Stufen

# Werkstoffe: Dichte kg/m^3 (für Masse/Schwerpunkt)
MAT = {
    "steel": 7850, "rubber_tyre": 1150 * 0.45, "alu": 2700, "pom": 1400,
    "battery": None, "box": None, "motor": None, "sensor": None,
}

COL = {  # RGB 0..1 für Render/STEP
    "frame": (0.18, 0.19, 0.21), "hopper": (0.95, 0.45, 0.08), "gate": (0.95, 0.45, 0.08),
    "steel": (0.72, 0.73, 0.75), "chrome": (0.85, 0.86, 0.88), "tyre": (0.07, 0.07, 0.07),
    "rim": (0.93, 0.76, 0.10), "drive": (0.30, 0.33, 0.38), "box": (0.80, 0.82, 0.84),
    "sensor": (0.08, 0.09, 0.10), "red": (0.85, 0.08, 0.08), "yellow": (0.98, 0.82, 0.05),
    "rubber": (0.12, 0.12, 0.12), "beacon": (1.0, 0.55, 0.0), "payload": (0.36, 0.25, 0.14),
}


@dataclass
class PartDef:
    name: str
    shape: object
    group: str            # Bewegungsgruppe: fixed, hopper, gate, wheel_FL..., cyl0..cyl3
    color: str
    density: float = 7850  # kg/m^3, oder None + mass_kg
    mass_kg: float = None
    bom: str = ""          # Stücklistentext
    weldment: bool = False
    meta: dict = field(default_factory=dict)


# ---------------------------------------------------------------- Helfer
def box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0).moved(Location(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)))


def rect_tube_x(x0, x1, yc, zc, w, h, t):
    """Rechteckrohr entlang X, Breite w (Y), Höhe h (Z)."""
    return box(x0, x1, yc - w / 2, yc + w / 2, zc - h / 2, zc + h / 2) - \
        box(x0 - 1, x1 + 1, yc - w / 2 + t, yc + w / 2 - t, zc - h / 2 + t, zc + h / 2 - t)


def rect_tube_y(y0, y1, xc, zc, w, h, t):
    return box(xc - w / 2, xc + w / 2, y0, y1, zc - h / 2, zc + h / 2) - \
        box(xc - w / 2 + t, xc + w / 2 - t, y0 - 1, y1 + 1, zc - h / 2 + t, zc + h / 2 - t)


def cyl_y(xc, zc, r, y0, y1):
    """Zylinder mit Achse parallel Y."""
    return Cylinder(r, y1 - y0).moved(Location((xc, (y0 + y1) / 2, zc), (90, 0, 0)))


def cyl_x(yc, zc, r, x0, x1):
    return Cylinder(r, x1 - x0).moved(Location(((x0 + x1) / 2, yc, zc), (0, 90, 0)))


def cyl_z(xc, yc, r, z0, z1):
    return Cylinder(r, z1 - z0).moved(Location((xc, yc, (z0 + z1) / 2)))


def prism_xz(pts, y0, y1):
    """Prisma: Polygon in XZ-Ebene, extrudiert von y0 bis y1."""
    face = Polygon(*[(x, z) for x, z in pts], align=None)
    # Polygon liegt in XY -> auf XZ-Ebene drehen: (x,y)->(x,0,y), Extrusion entlang +Y
    sol = extrude(Plane.XZ * face, amount=-(y1 - y0))
    return sol.moved(Location((0, y0, 0)))


def prism_yz(pts, x0, x1):
    face = Polygon(*[(y, z) for y, z in pts], align=None)
    sol = extrude(Plane.YZ * face, amount=x1 - x0)
    return sol.moved(Location((x0, 0, 0)))


def front_x(z, inset=0.0):
    """X der Muldenvorderwand (außen) auf Höhe z."""
    p = P
    return p["hop_x1"] + (p["hop_front_top_x"] - p["hop_x1"]) * (z - p["hop_floor_z"]) / (p["hop_top_z"] - p["hop_floor_z"]) - inset


# ---------------------------------------------------------------- Baugruppen
def build_frame():
    p = P
    yc = (p["rail_y_in"] + p["rail_y_out"]) / 2
    zc = (p["rail_z0"] + p["rail_z1"]) / 2
    parts = []
    for s in (1, -1):
        parts.append(rect_tube_x(p["frame_x0"], p["frame_x1"], s * yc, zc, 40, 60, p["tube_t"]))
    # Querträger 40x40 (x-Position Mitte)
    for xc in (-700, 0, 485, 740):
        parts.append(rect_tube_y(-p["rail_y_in"], p["rail_y_in"], xc, 210, 40, 40, p["tube_t"]))
    # Kipplagerböcke: Distanzplatte am Längsträger + Lagerblech
    for s in (1, -1):
        parts.append(box(-730, -650, *sorted((s * 270, s * 280)), 170, 230))
        parts.append(box(-730, -650, *sorted((s * 280, s * 292)), 170, 300))
    # Technikboden vorne (Blech 6 mm) auf den Längsträgern
    parts.append(box(480, 760, -290, 290, 230, 236) - box(505, 680, -64, 64, 220, 240))
    # Zylinder-Fußgabel (2 Laschen 10 mm) vorn am Querträger x=485
    for s in (1, -1):
        parts.append(box(505, p["cyl_x"] + 20, *sorted((s * 16, s * 26)), 175, 240) + cyl_y(p["cyl_x"], p["cyl_base_z"], 25, *sorted((s * 16, s * 26))))
    # Konsolen für Gummipuffer sind direkt die Trägeroberseite
    frame = parts[0]
    for q in parts[1:]:
        frame = frame + q
    # Bohrungen: Achsstummel Ø30 durch Längsträger, Kippbolzen, Zylinder-Fußbolzen
    for x in (p["x_front"], p["x_rear"]):
        frame = frame - cyl_y(x, 200, 15, -300, 300)
    frame = frame - cyl_y(p["pivot_x"], p["pivot_z"], p["pivot_d"] / 2, -300, 300)
    frame = frame - cyl_y(p["cyl_x"], p["cyl_base_z"], 8, -40, 40)
    return frame


def hopper_shell():
    p = P
    t, tf = p["sheet"], p["floor_t"]
    zf, zt = p["hop_floor_z"], p["hop_top_z"]
    yf, yw, zk = p["hop_y_floor"], p["hop_y_wall"], p["hop_z_knee"]
    # Außenkontur Seitenansicht (XZ) und Querschnitt (YZ)
    side = [(p["hop_x0"], zf), (p["hop_x1"], zf), (p["hop_front_top_x"], zt), (p["hop_x0"], zt)]
    cross = [(-yf, zf), (yf, zf), (yw, zk), (yw, zt), (-yw, zt), (-yw, zk)]
    outer = prism_xz(side, -400, 400) & prism_yz(cross, -800, 600)
    # Innenkontur: um Blechdicke versetzt, oben und hinten offen
    ang_f = math.atan((p["hop_front_top_x"] - p["hop_x1"]) / (zt - zf))
    dxf = t / math.cos(ang_f)
    side_i = [(p["hop_x0"] - 50, zf + tf), (p["hop_x1"] - dxf, zf + tf),
              (p["hop_front_top_x"] - dxf + (100 * math.tan(ang_f)), zt + 100), (p["hop_x0"] - 50, zt + 100)]
    ang_s = math.atan((yw - yf) / (zk - zf))
    dys = t / math.cos(ang_s)
    # Knick: Innenpunkt so, dass beide Wandabschnitte Dicke t haben (Näherung)
    cross_i = [(-(yf - dys), zf + tf), (yf - dys, zf + tf), (yw - t, zk + 2), (yw - t, zt + 100),
               (-(yw - t), zt + 100), (-(yw - t), zk + 2)]
    inner = prism_xz(side_i, -400, 400) & prism_yz(cross_i, -900, 700)
    return outer - inner, inner


def build_hopper():
    p = P
    shell, _ = hopper_shell()
    parts = [shell]
    zt = p["hop_top_z"]
    # Oberer Randverstärker (Flachstahl 40x5 außen umlaufend an Seiten und Front)
    for s in (1, -1):
        parts.append(box(p["hop_x0"], front_x(zt - 40) + 2, *sorted((s * p["hop_y_wall"], s * (p["hop_y_wall"] + 5))), zt - 40, zt))
    # Unterrahmen: Längsrohre 40x40 über den Rahmenträgern, Querrohre
    yc = 250
    for s in (1, -1):
        parts.append(rect_tube_x(p["pivot_x"], 330, s * yc, 260, 40, 40, 3))
    for xc in (-600, 300):
        parts.append(rect_tube_y(-230, 230, xc, 260, 40, 40, 3))
    # Kipplaschen 10 mm an den Längsrohren (außen), rund um den Drehpunkt
    for s in (1, -1):
        y0, y1 = sorted((s * 270, s * 280))
        lug = box(p["pivot_x"], -640, y0, y1, 240, 280) + cyl_y(p["pivot_x"], p["pivot_z"], 28, y0, y1)
        parts.append(lug)
    # Heckklappen-Scharnierohren außen an den Seitenwänden
    for s in (1, -1):
        y0, y1 = sorted((s * p["hop_y_wall"], s * (p["hop_y_wall"] + 10)))
        ear = box(p["gate_hinge_x"], -660, y0, y1, 785, 830) + cyl_y(p["gate_hinge_x"], p["gate_hinge_z"], 18, y0, y1)
        parts.append(ear)
    # Zylinder-Kopfgabel an der Stirnwand (2 Laschen 10 mm + Verstärkungsblech)
    za = p["cyl_top_z"]
    dbl = [(front_x(za - 60) - 2, za - 60), (front_x(za + 60) - 2, za + 60), (front_x(za + 60) + 6, za + 60), (front_x(za - 60) + 6, za - 60)]
    parts.append(prism_xz(dbl, -60, 60))  # Doppler auf Stirnwand
    for s in (1, -1):
        y0, y1 = sorted((s * 16, s * 26))
        lug = [(front_x(za - 22) - 2, za - 22), (p["cyl_x"], za - 22), (p["cyl_x"], za + 45), (front_x(za + 45) - 2, za + 45)]
        parts.append(prism_xz(lug, y0, y1) + cyl_y(p["cyl_x"], za, 25, y0, y1))
    hop = parts[0]
    for q in parts[1:]:
        hop = hop + q
    hop = hop - cyl_y(p["pivot_x"], p["pivot_z"], p["pivot_d"] / 2, -300, 300)
    hop = hop - cyl_y(p["gate_hinge_x"], p["gate_hinge_z"], 6, -330, 330)
    hop = hop - cyl_y(p["cyl_x"], za, 8, -40, 40)
    return hop


def build_gate():
    p = P
    hx, hz = p["gate_hinge_x"], p["gate_hinge_z"]
    yf, yw, zk = p["hop_y_floor"], p["hop_y_wall"], p["hop_z_knee"]
    zb = p["hop_floor_z"] - 4
    pts = [(-(yf + 2), zb), (yf + 2, zb), (yw - 1, zk), (yw - 1, hz), (-(yw - 1), hz), (-(yw - 1), zk)]
    plate = prism_yz(pts, -704, -700)
    tube = cyl_y(hx, hz, 12, -(yw - 1), yw - 1) + box(hx, -700, -(yw - 1), yw - 1, hz - 12, hz)
    # Versteifungen (Flachstahl 30x5 horizontal)
    stiff = box(-712, -704, -(yf), yf, 420, 450) + box(-712, -704, -(yw - 20), yw - 20, 620, 650)
    gate = plate + tube + stiff
    gate = gate - cyl_y(hx, hz, 6, -330, 330)
    return gate


def build_wheel(side, x):
    """Rad: Reifen (Ring) + Felge mit Nabenbohrung. Gibt (Reifen, Felge) zurück."""
    p = P
    s = 1 if side == "L" else -1
    yc = s * p["wheel_y"]
    y0, y1 = yc - p["wheel_w"] / 2, yc + p["wheel_w"] / 2
    tyre = cyl_y(x, p["wheel_r"], p["wheel_r"], y0, y1) - cyl_y(x, p["wheel_r"], p["rim_r"], y0 - 1, y1 + 1)
    try:
        tyre = fillet(tyre.edges().filter_by(lambda e: e.radius > 150 if hasattr(e, "radius") else False), 25)
    except Exception:
        pass
    ry0, ry1 = yc - 40, yc + 40
    rim = cyl_y(x, p["wheel_r"], p["rim_r"], ry0, ry1)
    # Felgenschüssel: außen vertieft
    dish_y = (yc + s * 15, yc + s * 41)
    rim = rim - cyl_y(x, p["wheel_r"], 85, *sorted(dish_y))
    # Nabe zur Achse hin
    hub_y = sorted((yc - s * 40, yc - s * 52))
    rim = rim + cyl_y(x, p["wheel_r"], 45, *hub_y)
    rim = rim - cyl_y(x, p["wheel_r"], 15, *sorted((yc - s * 53, yc + s * 10)))
    for k in range(5):  # Radbolzen
        a = 2 * math.pi * k / 5
        rim = rim + cyl_y(x + 60 * math.cos(a), p["wheel_r"] + 60 * math.sin(a), 7, *sorted((yc + s * 15, yc + s * 25)))
    return tyre, rim


def build_drive(side, x):
    """Achsstummel, Flanschlager, Winkelgetriebe, Motor für ein Rad."""
    p = P
    s = 1 if side == "L" else -1
    zc = 200.0
    # Stummelwelle Ø30 von Getriebemitte bis in die Felge
    yA, yB = 165, p["wheel_y"] + 10
    shaft = cyl_y(x, zc, 15, *sorted((s * yA, s * yB)))
    # Flanschlager (4-Loch, UCF206-ähnlich) außen am Längsträger
    fy = sorted((s * 270, s * 293))
    bearing = box(x - 54, x + 54, *fy, zc - 54, zc + 54)
    bearing = bearing + cyl_y(x, zc, 40, *sorted((s * 270, s * 297)))
    bearing = bearing - cyl_y(x, zc, 15, *sorted((s * 260, s * 300)))
    # Winkelgetriebe (Schnecke) innen am Träger, Hohlwelle Ø30
    gy = sorted((s * 110, s * 230))
    gear = box(x - 60, x + 60, *gy, 145, 255)
    gear = gear - cyl_y(x, zc, 15, *sorted((s * 100, s * 240)))
    # Motor Ø90 Achse in X, zur Fahrzeugmitte hin
    dirx = -1 if x > 0 else 1
    mx0 = x + dirx * 60
    mx1 = x + dirx * 230
    motor = cyl_x(s * 170, 192, 45, *sorted((mx0, mx1)))
    motor = motor + cyl_x(s * 170, 192, 30, *sorted((mx1, mx1 + dirx * 25)))  # Geber/Bremse
    return shaft, bearing, gear, motor


def build_cylinder():
    """Teleskopzylinder (Gehäuse + 4 Stufen), lokal: Achse +Z, Ursprung = Fußauge B. Eingefahren."""
    p = P
    Lr = p["cyl_retracted"]
    r = p["cyl_r"]
    parts = []
    body_z0, body_z1 = 60, Lr - 70
    # Bodenstück konisch (Freigang zum Querträger bei großem Kippwinkel)
    cone = Cone(35, r[0], 25).moved(Location((0, 0, body_z0 + 12.5)))
    s0 = cone + cyl_z(0, 0, r[0], body_z0 + 25, body_z1) - cyl_z(0, 0, r[1], body_z0 + 26, body_z1 + 1)
    eye0 = cyl_y(0, 0, 20, -15, 15) + box(-15, 15, -15, 15, 0, body_z0 + 1)
    s0 = s0 + eye0 - cyl_y(0, 0, 8, -20, 20)
    parts.append(s0)
    n = len(r) - 1
    for i in range(1, n + 1):
        z0 = body_z0 + 25 + 10 * i
        z1 = body_z1 + 10 * i
        if i < n:
            st = cyl_z(0, 0, r[i], z0, z1) - cyl_z(0, 0, r[i + 1], z0 + 10, z1 + 1)
        else:
            z1 = Lr - 55  # Stange endet unterhalb der Kopfgabel, Hals 30 mm breit
            st = cyl_z(0, 0, r[i], z0, z1)
            eye = cyl_y(0, Lr, 20, -15, 15) + box(-15, 15, -15, 15, z1 - 1, Lr)
            st = st + eye - cyl_y(0, Lr, 8, -20, 20)
        parts.append(st)
    return parts


def build_payload(fill_z=780.0):
    """Ladung (Mist) als Volumen der Mulde bis Füllhöhe (für Masse/Schwerpunkt/Render)."""
    _, inner = hopper_shell()
    p = P
    lim = box(p["hop_x0"] + 0.5, 700, -400, 400, p["hop_floor_z"] + p["floor_t"] + 0.5, fill_z)
    return inner & lim


def build_extras():
    """Technikboxen, Sensorik, Sicherheitstechnik, Puffer. Liste von PartDef."""
    p = P
    out = []
    # Akku-Box links, Elektronik/Hydraulik-Box rechts (IP65-Gehäuse, Edelstahl)
    out.append(PartDef("Akkugehäuse (LiFePO4 48 V 100 Ah)", box(482, 760, 62, 290, 236, 700), "fixed", "box",
                       None, 62.0, "Gehäuse 1.4301, IP65, inkl. Akku 48 V/100 Ah (~45 kg)"))
    out.append(PartDef("Steuerungs-/Hydraulikgehäuse", box(482, 760, -290, -62, 236, 700), "fixed", "box",
                       None, 38.0, "Gehäuse IP65: Rechner, Motorregler, Sicherheitssteuerung, Hydraulikaggregat"))
    # Lidar-Mast + 3D-Lidar, GNSS, Rundumleuchte, Not-Aus
    out.append(PartDef("Sensormast", cyl_z(735, 175, 20, 700, 905), "fixed", "steel", 7850 * 0.25, None, "Rohr Ø40x2"))
    lid = cyl_z(735, 175, 33, 905, 965)
    out.append(PartDef("3D-Lidar (360°)", lid, "fixed", "sensor", None, 0.27, "z. B. Livox Mid-360"))
    out.append(PartDef("RTK-GNSS-Antenne", cyl_z(710, -200, 45, 700, 718), "fixed", "sensor", None, 0.4, "Multiband-Antenne"))
    out.append(PartDef("Rundumleuchte", cyl_z(530, -240, 40, 700, 790), "fixed", "beacon", None, 0.6, "LED, gelb/orange"))
    for s, nm in ((1, "links"), (-1, "rechts")):
        out.append(PartDef(f"Not-Halt {nm}", cyl_z(560, s * 120, 28, 700, 730) + cyl_z(560, s * 120, 20, 730, 760),
                           "fixed", "red", None, 0.3, "Pilztaster, 2-kanalig"))
    # Front-Kamera und Ultraschall
    out.append(PartDef("Frontkamera (Stereo)", box(760, 790, -100, 100, 600, 640), "fixed", "sensor", None, 0.4, "Stereo-/Tiefenkamera"))
    # Sicherheits-Bumper (Schaltleisten) vorn/hinten
    out.append(PartDef("Bumper vorn (Schaltleiste)", box(760, 800, -300, 300, 160, 236), "fixed", "yellow", None, 2.5, "Schaltleiste PL d"))
    out.append(PartDef("Bumper hinten (Schaltleiste)", box(-760, -720, -230, 230, 160, 225), "fixed", "yellow", None, 2.0, "Schaltleiste PL d"))
    out.append(PartDef("Heckkamera", box(-775, -760, -40, 40, 170, 210), "fixed", "sensor", None, 0.3, "Tiefenkamera, Rückfahren/Abkippen"))
    # Gummipuffer (Muldenauflage) 60x30x10 auf Längsträgern
    for xc in (-300, 250):
        for s in (1, -1):
            out.append(PartDef(f"Gummipuffer x{xc:+.0f} {'L' if s > 0 else 'R'}",
                               box(xc - 30, xc + 30, s * 250 - 15, s * 250 + 15, 230, 240), "fixed", "rubber", 1200, None, "NR 60 Shore A"))
    return out


def build_all():
    p = P
    parts = []
    parts.append(PartDef("Rahmen (Schweißbaugruppe)", build_frame(), "fixed", "frame", 7850, None,
                         "S235, Rechteckrohr 60x40x3 / 40x40x3, feuerverzinkt", weldment=True))
    parts.append(PartDef("Mulde (Schweißbaugruppe)", build_hopper(), "hopper", "hopper", 7850, None,
                         "S355 3/4 mm Blech, Unterrahmen 40x40x3, feuerverzinkt + pulverbeschichtet", weldment=True))
    parts.append(PartDef("Heckklappe (Pendelklappe)", build_gate(), "gate", "gate", 7850, None,
                         "Blech 4 mm, Scharnierrohr Ø24", weldment=True))
    parts.append(PartDef("Kippbolzen Ø25", cyl_y(p["pivot_x"], p["pivot_z"], p["pivot_d"] / 2, -292, 292),
                         "fixed", "chrome", 7850, None, "42CrMo4, verchromt, Sicherung Splint"))
    parts.append(PartDef("Klappenbolzen Ø12", cyl_y(p["gate_hinge_x"], p["gate_hinge_z"], 6, -(p["hop_y_wall"] + 10), p["hop_y_wall"] + 10),
                         "hopper", "chrome", 7850, None, "Edelstahl"))
    parts.append(PartDef("Zylinder-Fußbolzen Ø16", cyl_y(p["cyl_x"], p["cyl_base_z"], 8, -26, 26),
                         "fixed", "chrome", 7850, None, "42CrMo4"))
    parts.append(PartDef("Zylinder-Kopfbolzen Ø16", cyl_y(p["cyl_x"], p["cyl_top_z"], 8, -26, 26),
                         "hopper", "chrome", 7850, None, "42CrMo4"))
    for side in ("L", "R"):
        for pos, x in (("V", p["x_front"]), ("H", p["x_rear"])):
            tag = f"{pos}{side}"
            tyre, rim = build_wheel(side, x)
            shaft, bearing, gear, motor = build_drive(side, x)
            parts.append(PartDef(f"Reifen {tag}", tyre, f"wheel_{tag}", "tyre", 1150 * 0.45, None, "4.00-8 Profil AS, Luft oder pannensicher"))
            parts.append(PartDef(f"Felge {tag}", rim, f"wheel_{tag}", "rim", 7850 * 0.35, None, "Stahlfelge 8\" (hohl, Masse reduziert)"))
            parts.append(PartDef(f"Achsstummel {tag}", shaft, f"wheel_{tag}", "chrome", 7850, None, "C45 Ø30, Passfeder"))
            parts.append(PartDef(f"Flanschlager {tag}", bearing, "fixed", "steel", 7850 * 0.6, None, "UCF206 (Ø30), abgedichtet"))
            parts.append(PartDef(f"Winkelgetriebe {tag}", gear, "fixed", "drive", None, 7.5, "Schneckengetriebe i≈40, Hohlwelle Ø30, IP65"))
            parts.append(PartDef(f"Motor {tag}", motor, "fixed", "drive", None, 4.5, "BLDC 48 V 750 W mit Haltebremse"))
    for i, st in enumerate(build_cylinder()):
        st = st.moved(Location((p["cyl_x"], 0, p["cyl_base_z"])))
        parts.append(PartDef(f"Teleskopzylinder Stufe {i}", st, f"cyl{i}", "chrome" if i else "frame", 7850, None,
                             "4-stufig Ø91/76/61/46, einfachwirkend, Hub 1140" if i == 0 else ""))
    parts += build_extras()
    return parts


# ---------------------------------------------------------------- Verbindungen (für Freischwebend-Prüfung)
def joints():
    """(Teil A, Teil B, Art). Jede Verbindung muss geometrisch Kontakt haben (Abstand <= tol)."""
    J = []
    J += [("Kippbolzen Ø25", "Rahmen (Schweißbaugruppe)", "Bolzen in Lagerbock"),
          ("Kippbolzen Ø25", "Mulde (Schweißbaugruppe)", "Bolzen in Kipplasche (Drehgelenk)"),
          ("Klappenbolzen Ø12", "Mulde (Schweißbaugruppe)", "Bolzen in Scharnierohr"),
          ("Klappenbolzen Ø12", "Heckklappe (Pendelklappe)", "Drehgelenk Klappe"),
          ("Zylinder-Fußbolzen Ø16", "Rahmen (Schweißbaugruppe)", "Bolzen in Fußgabel"),
          ("Zylinder-Fußbolzen Ø16", "Teleskopzylinder Stufe 0", "Drehgelenk Fußauge"),
          ("Zylinder-Kopfbolzen Ø16", "Mulde (Schweißbaugruppe)", "Bolzen in Kopfgabel"),
          ("Zylinder-Kopfbolzen Ø16", "Teleskopzylinder Stufe 4", "Drehgelenk Kopfauge"),
          ("Teleskopzylinder Stufe 1", "Teleskopzylinder Stufe 0", "Führung"),
          ("Teleskopzylinder Stufe 2", "Teleskopzylinder Stufe 1", "Führung"),
          ("Teleskopzylinder Stufe 3", "Teleskopzylinder Stufe 2", "Führung"),
          ("Teleskopzylinder Stufe 4", "Teleskopzylinder Stufe 3", "Führung"),
          ("Mulde (Schweißbaugruppe)", "Gummipuffer x+250 L", "Auflage (Ruhelage)")]
    for side in ("L", "R"):
        for pos in ("V", "H"):
            t = f"{pos}{side}"
            J += [(f"Reifen {t}", f"Felge {t}", "aufgezogen"),
                  (f"Felge {t}", f"Achsstummel {t}", "Nabe/Passfeder"),
                  (f"Achsstummel {t}", f"Flanschlager {t}", "Lagersitz"),
                  (f"Achsstummel {t}", f"Winkelgetriebe {t}", "Hohlwelle"),
                  (f"Flanschlager {t}", "Rahmen (Schweißbaugruppe)", "verschraubt 4xM12"),
                  (f"Winkelgetriebe {t}", "Rahmen (Schweißbaugruppe)", "verschraubt"),
                  (f"Motor {t}", f"Winkelgetriebe {t}", "angeflanscht")]
    for nm in ("Akkugehäuse (LiFePO4 48 V 100 Ah)", "Steuerungs-/Hydraulikgehäuse", "Bumper vorn (Schaltleiste)",
               "Bumper hinten (Schaltleiste)"):
        J.append((nm, "Rahmen (Schweißbaugruppe)", "verschraubt"))
    J += [("Sensormast", "Akkugehäuse (LiFePO4 48 V 100 Ah)", "verschraubt"),
          ("3D-Lidar (360°)", "Sensormast", "verschraubt"),
          ("RTK-GNSS-Antenne", "Steuerungs-/Hydraulikgehäuse", "Magnetfuß/verschraubt"),
          ("Rundumleuchte", "Steuerungs-/Hydraulikgehäuse", "verschraubt"),
          ("Not-Halt links", "Akkugehäuse (LiFePO4 48 V 100 Ah)", "eingebaut"),
          ("Not-Halt rechts", "Steuerungs-/Hydraulikgehäuse", "eingebaut"),
          ("Frontkamera (Stereo)", "Akkugehäuse (LiFePO4 48 V 100 Ah)", "Halter"),
          ("Frontkamera (Stereo)", "Steuerungs-/Hydraulikgehäuse", "Halter"),
          ("Heckkamera", "Bumper hinten (Schaltleiste)", "Halter")]
    for xc in (-300, 250):
        for s in ("L", "R"):
            J.append((f"Gummipuffer x{xc:+.0f} {s}", "Rahmen (Schweißbaugruppe)", "verklebt/verschraubt"))
    return J

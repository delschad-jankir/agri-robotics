"""Kinematik: Lage aller Bewegungsgruppen in Abhängigkeit vom Kippwinkel theta (Grad)
und den Raddrehwinkeln. Liefert 4x4-Matrizen (Ruhelage -> Pose) in mm."""
import math
import numpy as np
from build123d import Location
from OCP.gp import gp_Trsf
from model import P


def rot_y(deg, about=(0, 0, 0)):
    """Drehung um eine Achse parallel +Y durch Punkt 'about' (x, z)."""
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    R = np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1.0]])
    T = np.eye(4); T[0, 3], T[2, 3] = about[0], about[1]
    Ti = np.eye(4); Ti[0, 3], Ti[2, 3] = -about[0], -about[1]
    return T @ R @ Ti


def trans(x, y, z):
    T = np.eye(4); T[:3, 3] = (x, y, z)
    return T


def apply(M, pt):
    v = M @ np.array([pt[0], pt[1], pt[2], 1.0])
    return v[:3]


PIV = (P["pivot_x"], P["pivot_z"])
A0 = np.array([P["cyl_x"], 0, P["cyl_top_z"]])
B = np.array([P["cyl_x"], 0, P["cyl_base_z"]])
H0 = np.array([P["gate_hinge_x"], 0, P["gate_hinge_z"]])


def hopper_M(theta):
    # Mulde vorne hoch = Drehung um +Y mit negativem Winkel
    return rot_y(-theta, PIV)


def cyl_length(theta):
    A = apply(hopper_M(theta), A0)
    return float(np.linalg.norm(A - B))


def theta_max_geom():
    """Größter Kippwinkel, den der Zylinderhub erlaubt."""
    Lmax = P["cyl_retracted"] + P["cyl_stroke"]
    lo, hi = 0.0, 89.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if cyl_length(mid) <= Lmax:
            lo = mid
        else:
            hi = mid
    return lo


def poses(theta, wheel_deg=0.0, gate_free=True):
    """dict gruppe -> 4x4."""
    M = {"fixed": np.eye(4)}
    Mh = hopper_M(theta)
    M["hopper"] = Mh
    H = apply(Mh, H0)
    # Pendelklappe hängt senkrecht (Weltlage = Ruhelage, nur verschoben)
    M["gate"] = trans(*(H - H0)) if gate_free else Mh
    A = apply(Mh, A0)
    d = A - B
    L = float(np.linalg.norm(d))
    beta = math.degrees(math.atan2(d[0], d[2]))
    e = L - P["cyl_retracted"]
    Rc = rot_y(beta, (B[0], B[2]))
    n = len(P["cyl_r"]) - 1
    for i in range(n + 1):
        ext = min(max(e, 0), P["cyl_stroke"]) * i / n
        M[f"cyl{i}"] = Rc @ trans(0, 0, ext)
    for tag, x in (("VL", P["x_front"]), ("HL", P["x_rear"]), ("VR", P["x_front"]), ("HR", P["x_rear"])):
        M[f"wheel_{tag}"] = rot_y(wheel_deg, (x, P["wheel_r"]))
    return M


def to_loc(M):
    t = gp_Trsf()
    t.SetValues(*M[0, :4], *M[1, :4], *M[2, :4])
    return Location(t)


def posed(shape, M):
    if np.allclose(M, np.eye(4)):
        return shape
    return shape.moved(to_loc(M))

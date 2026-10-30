"""Diagramme aus den Prüf- und Auslegungsergebnissen (docs/img/diag_*.png)."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

r = json.load(open("../out/check_report.json"))
SER = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # validiert (dataviz), Reihenfolge fest
INK, INK2, GRID = "#1f2328", "#59636e", "#e3e6e9"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})


def base(title, sub, ylabel, xlabel="Kippwinkel θ [°]"):
    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
    fig.subplots_adjust(left=0.1, right=0.8, top=0.82, bottom=0.12)
    fig.text(0.1, 0.94, title, fontsize=15, fontweight="bold", color=INK)
    fig.text(0.1, 0.885, sub, fontsize=10.5, color=INK2)
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    return fig, ax


def line(ax, x, y, i, label):
    ax.plot(x, y, color=SER[i], lw=2, label=label, solid_capstyle="round")
    ax.annotate(label, (x[-1], y[-1]), xytext=(6, 0), textcoords="offset points", va="center", color=INK, fontsize=10)


st = r["stability"]
th = [s["theta"] for s in st]
# 1 Zylinderkraft
fig, ax = base("Zylinderkraft über dem Kippwinkel", "Virtuelle Arbeit aus dem CAD-Modell · Ladung 0,32 m³ × 750 kg/m³ · Zylinder kann > 20 kN",
               "Kraft [kN]")
line(ax, th, [s["zylinderkraft_beladen_N"] / 1000 for s in st], 0, "beladen")
line(ax, th, [s["zylinderkraft_leer_N"] / 1000 for s in st], 1, "leer")
ax.set_ylim(0, None); ax.legend(frameon=False, loc="upper right")
fig.savefig("../docs/img/diag_zylinderkraft.png"); plt.close(fig)

# 2 Freigänge
sw = r["sweep"]
tw = [s["theta"] for s in sw]
fig, ax = base("Mindestabstände über den Kippweg", f"Kollisionsprüfung aller Teilepaare alle 2,5° · {sum(len(s['collisions']) for s in sw)} Kollisionen · 0 mm = Berührung",
               "Abstand [mm]")
for i, (k, lab) in enumerate([("Zylinder-Mulde", "Zylinder–Mulde"), ("Mulde-Reifen", "Mulde–Reifen"),
                              ("Klappe-Rahmen", "Klappe–Rahmen"), ("Mulde-Technikbox", "Mulde–Technikbox")]):
    line(ax, tw, [s["clearance"][k] for s in sw], i, lab)
line(ax, tw, [s["zmin_moving"] for s in sw], 0, "")
ax.lines[-1].set_color(INK2); ax.lines[-1].set_linestyle("--"); ax.lines[-1].set_linewidth(1.5)
ax.texts[-1].remove()
ax.text(31, 215, "Bodenabstand bewegter Teile", color=INK2, fontsize=9)
ax.set_yscale("symlog", linthresh=50); ax.set_ylim(0, 1000)
ax.legend(frameon=False, loc="upper left", fontsize=9)
fig.savefig("../docs/img/diag_freigaenge.png"); plt.close(fig)

# 3 Kippgrenzen
fig, ax = base("Statische Kippgrenze (beladen) über den Kippwinkel", "Hangneigung, bei der das Fahrzeug kippen würde · Linie = 15 % Steigung (8,5°)",
               "Kippgrenze [° Hangneigung]")
for i, (k, lab) in enumerate([("vorn", "nach vorn"), ("hinten", "nach hinten"), ("seite", "zur Seite")]):
    line(ax, th, [s["kippgrenze_beladen_deg"][k] for s in st], i, lab)
ax.axhline(8.5, color=INK2, lw=1.2, ls="--")
ax.text(1, 9.5, "15 % Rampe", color=INK2, fontsize=9)
ax.set_ylim(0, 50); ax.legend(frameon=False, loc="lower left")
fig.savefig("../docs/img/diag_kippgrenzen.png"); plt.close(fig)

# 4 Massen nach Baugruppe
groups = {}
for m in r["masses"]:
    n = m["teil"]
    key = ("Akku + Gehäuse" if n.startswith("Akku") else "Steuerung/Hydraulik" if n.startswith("Steuerung") else
           "Mulde + Klappe" if n.startswith(("Mulde", "Heckklappe")) else "Rahmen" if n.startswith("Rahmen") else
           "Radantriebe (4×)" if n.startswith(("Motor", "Winkel", "Flansch", "Achs")) else "Räder (4×)" if n.startswith(("Reifen", "Felge")) else
           "Kippzylinder" if n.startswith(("Teleskop", "Zylinder")) else "Sonstiges")
    groups[key] = groups.get(key, 0) + m["masse_kg"]
items = sorted(groups.items(), key=lambda kv: kv[1])
fig, ax = base("Masse nach Baugruppe", f"Leer {r['vehicle_mass_kg']:.0f} kg · beladen {r['mass_total_loaded_kg']:.0f} kg (aus CAD-Volumen × Dichte bzw. Katalogwerten)",
               "", xlabel="Masse [kg]")
ax.barh([k for k, _ in items], [v for _, v in items], color=SER[0], height=0.6)
for k, v in items:
    ax.text(v + 1, k, f"{v:.0f} kg", va="center", color=INK, fontsize=10)
ax.grid(axis="y", visible=False)
fig.savefig("../docs/img/diag_massen.png"); plt.close(fig)
print("Diagramme geschrieben")

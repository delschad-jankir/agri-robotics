"""Auslegung Fahrantrieb und Energie (Konzeptniveau). Liest Massen aus out/check_report.json."""
import json, math

r = json.load(open("../out/check_report.json"))
g = 9.81
m_e = r["vehicle_mass_kg"]
m_l = r["mass_total_loaded_kg"]
R = 0.200            # Radradius m
B = 0.700            # Spurweite m (Radmitte)
L = 0.800            # Radstand m
A = dict(
    v_max=1.2,        # m/s außen (Schrittgeschwindigkeit)
    v_stall=0.6,      # m/s in der Stallgasse
    slope=0.15,       # 15 % Rampe (Mistplatte / Hofauffahrt)
    c_rr_concrete=0.03, c_rr_gravel=0.10,   # Rollwiderstand Beton / Schotter, Matsch
    mu_lat=0.6,       # Querreibung Reifen beim Drehen auf der Stelle (Beton, trocken)
    a_acc=0.5,        # m/s^2
    eta=0.65,         # Wirkungsgrad Schneckengetriebe + Motor
    trips_per_day=40, dist_one_way=120.0,   # m
    p_base=60.0,      # W Rechner + Sensorik
    hours_on=4.0,     # h Betriebszeit pro Tag (inkl. Warten am Beladeplatz)
)
out = {}
# Längsfahrt beladen am Hang auf Schotter
a = math.atan(A["slope"])
F_slope = m_l * g * math.sin(a)
F_rr = m_l * g * math.cos(a) * A["c_rr_gravel"]
F_acc = m_l * A["a_acc"]
F_tot = F_slope + F_rr + F_acc
out["Zugkraft Hang+Schotter+Beschl. [N]"] = round(F_tot)
# Drehen auf der Stelle (Skid-Steer): Bohrmoment ~ mu*G*L/4 je ... vereinfachtes Modell (Wong)
M_turn = A["mu_lat"] * m_l * g * L / 4
F_turn_side = M_turn / B   # Umfangskraft je Seite (vorwärts/rückwärts)
out["Drehmoment Drehen auf Stelle [Nm]"] = round(M_turn)
out["Umfangskraft je Seite beim Drehen [N]"] = round(F_turn_side)
F_wheel = max(F_tot / 4, F_turn_side / 2)
T_wheel = F_wheel * R
out["Radmoment erforderlich je Rad [Nm]"] = round(T_wheel)
n_wheel = A["v_max"] / (2 * math.pi * R) * 60
out["Raddrehzahl bei v_max [1/min]"] = round(n_wheel, 1)
P_drive = F_tot * A["v_stall"] / A["eta"]  # Hang wird langsam gefahren
P_flat = (m_l * g * A["c_rr_concrete"]) * A["v_max"] / A["eta"]
out["Leistung Hang 0,6 m/s gesamt [W]"] = round(P_drive)
out["Leistung eben Beton 1,2 m/s gesamt [W]"] = round(P_flat)
# Reibwertgrenze: kann die Zugkraft übertragen werden? (mu Beton nass ~0,5, Mist ~0,3)
for mu in (0.5, 0.3):
    out[f"übertragbare Zugkraft mu={mu} [N]"] = round(mu * m_l * g * math.cos(a))
# Energie pro Tag
E_trip = 0.0
for loaded in (True, False):
    m = m_l if loaded else m_e
    F = m * g * (0.05)  # Mittel Rollwiderstand gemischt
    E_trip += F * A["dist_one_way"] / A["eta"]
E_turns = 6 * M_turn * math.pi / A["eta"]        # 6 Wenden à 180° je Fahrt
E_tip = 2 * r["payload"]["masse_kg"] * g * 0.35 / 0.5  # Anheben ~0,35 m Schwerpunkt, Hydraulik 50 %
E_trip_Wh = (E_trip + E_turns + E_tip) / 3600
E_day = E_trip_Wh * A["trips_per_day"] + A["p_base"] * A["hours_on"]
out["Energie je Fahrt [Wh]"] = round(E_trip_Wh, 1)
out["Energie je Tag [Wh]"] = round(E_day)
cap = 48 * 100 * 0.8  # nutzbar 80 % von 48 V 100 Ah
out["Akku nutzbar 48 V/100 Ah [Wh]"] = round(cap)
out["Reserve (Tage je Ladung)"] = round(cap / E_day, 1)
out["Annahmen"] = A
json.dump(out, open("../out/calc_report.json", "w"), indent=1, ensure_ascii=False)
for k, v in out.items():
    if k != "Annahmen":
        print(f"{k:45s} {v}")

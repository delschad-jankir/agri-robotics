# Lastenheft – Mist-Shuttle V1 (autonomer Elektro-Kipper)

Stand 30.10.2026 · Version 0.1 · Grundlage: [Gespräch 1](01_gespraech.md)

Kennzeichnung: **(A)** = Annahme, beim Besuch vor Ort prüfen. **(F)** = Festforderung, **(W)** = Wunsch.

## 1. Zweck

Ein fahrerloses Elektrofahrzeug mit Kippmulde übernimmt den **Transport des Mists von der Box bzw. Stallgasse zum Mistplatz**. Beladen wird weiter von Hand. Ziel ist, dass niemand mehr Schubkarren oder Container schiebt und niemand nur zum Hin- und Herfahren gebraucht wird.

Abgrenzung V1: kein automatisches Aufsammeln, kein Einstreuen, kein Container-Schleppen. Das Container-Schleppen ist als Modul für V2 vorgesehen; das Fahrgestell wird dafür vorbereitet.

## 2. Einsatzumgebung

| Merkmal | Wert | Art |
|---|---|---|
| Stallgasse, Breite | ≥ 2,5 m | (A) |
| Boxentür / Stalltor, lichte Breite | ≥ 1,0 m / ≥ 2,5 m | (A) |
| Boden innen | Beton bzw. Gummimatten, verschmutzt, nass | (A) |
| Boden außen | Pflaster, Schotter, im Winter Matsch und Schnee | (A) |
| Steigung (Rampe Mistplatte, Hof) | ≤ 15 % | (A) |
| Schwellen, Rinnen | ≤ 40 mm | (A) |
| Weg Box → Mistplatz (einfach) | 50 … 150 m | (A) |
| Mistplatz | ebenerdige Mistplatte mit Rückwand, Haufen wird von hinten angefahren | (A) |
| Temperatur | −15 … +35 °C, Kondenswasser, Ammoniak, Staub | (F) |
| Reinigung | Hochdruckreiniger | (F) |
| Lebewesen im Arbeitsraum | Menschen (auch Ortsfremde, Kinder), Pferde (auch frei laufend), Hunde, Katzen | (F) |

## 3. Funktionen

| Nr. | Funktion | Art |
|---|---|---|
| F1 | Beladen von Hand mit Mistgabel/Schaufel, Ladekante ≤ 850 mm | (F) |
| F2 | Start per Taster am Fahrzeug („Fahr los“), optional per App/Funk | (F) |
| F3 | Autonome Fahrt zur Mistplatte, auch rückwärts an den Haufen heran | (F) |
| F4 | Selbsttätiges Abkippen nach hinten, Kippwinkel ≥ 50°, Klappe öffnet selbsttätig | (F) |
| F5 | Autonome Rückfahrt zur letzten bzw. nächsten Box | (F) |
| F6 | Erkennen von Menschen, Pferden und Hindernissen, langsamer werden oder anhalten | (F) |
| F7 | Not-Halt am Fahrzeug (beidseitig) und per Funk | (F) |
| F8 | Handbetrieb: Fernsteuerung, Schieben bei Störung (Bremse lösbar) | (F) |
| F9 | Laden über Stecker; später Ladestation mit automatischem Andocken | (F) / (W) |
| F10 | Schnittstelle für Modul „Container-Schlepper“ (V2): Zugöse, Zugkraft ≥ 1,5 kN | (W) |
| F11 | Zählen der Fahrten / Mistmenge (Nachweis, Dokumentation) | (W) |

## 4. Leistungsdaten

| Merkmal | Forderung | Art |
|---|---|---|
| Muldenvolumen (gestrichen) | ≥ 0,30 m³ (≈ 3–4 Schubkarren) | (F) |
| Nutzlast | ≥ 240 kg (bei 750 kg/m³ nassem Mist mit Stroh) | (F) |
| Fahrgeschwindigkeit | ≤ 0,6 m/s im Stall, ≤ 1,2 m/s außen | (F) |
| Steigfähigkeit beladen | 15 % auf trockenem Untergrund | (F) |
| Wenden | auf der Stelle (Breite der Stallgasse genügt) | (F) |
| Abmessungen B × L × H | ≤ 800 × 1600 × 1000 mm | (F) |
| Bodenfreiheit | ≥ 120 mm | (F) |
| Einsatzdauer pro Akkuladung | ≥ 1 Arbeitstag (40 Fahrten à 2 × 120 m) | (F) |
| Kippzeit (hoch + ab) | ≤ 15 s | (W) |
| Lärm | ≤ 70 dB(A) in 1 m, Pferde nicht erschrecken | (W) |

## 5. Sicherheit (Grundlage für die spätere Risikobeurteilung)

- Rechtsrahmen: **EU-Maschinenverordnung (EU) 2023/1230** (gilt ab 20.01.2027; ersetzt die Maschinenrichtlinie 2006/42/EG).
- Normen zur Orientierung (zu prüfen): **ISO 3691-4** (fahrerlose Flurförderzeuge), **ISO 18497** (autonome Landmaschinen), **EN ISO 13849-1** (Sicherheitsfunktionen, Ziel PL d), **EN ISO 13850** (Not-Halt), **EN ISO 12100** (Risikobeurteilung).
- Gefährdungen, die konstruktiv adressiert werden müssen:
  - Anfahren von Personen und Pferden → Geschwindigkeitsbegrenzung, Schaltleisten vorn und hinten, Schutzfelder im 3D-Lidar
  - Quetschen beim Kippen (Mulde und Rahmen, Klappe) → Kippen nur bei freiem Heckbereich (Heckkamera); Kippen per Totmann/Freigabe in V1
  - Absenken der Mulde bei Schlauchbruch → Senkbremsventil bzw. Rohrbruchsicherung am Zylinder
  - Kippen des Fahrzeugs am Hang → statische Kippgrenze ≥ 15° in allen Richtungen, auch bei gekippter Mulde
  - Elektrik → Schutzkleinspannung 48 V, IP65, Akku mit BMS und Temperaturüberwachung

## 6. Robustheit, Wartung

- Stahlteile feuerverzinkt, Mulde zusätzlich pulverbeschichtet (W: PE-Auskleidung gegen Anhaften)
- Elektrik IP65, Stecker IP67, Gehäuse aus Edelstahl
- Wartung durch den Landwirt: Abschmieren der Gelenke, Reifendruck, Hydrauliköl; keine Spezialwerkzeuge
- Verschleißteile (Reifen, Lager, Schaltleisten) als Normteile

## 7. Wirtschaftliche Vorgaben

| Merkmal | Ziel |
|---|---|
| Hardware Prototyp 1 | ≤ 15.000 € (siehe [Kosten](04_kosten.md)) |
| Herstellkosten Serie (≥ 50 Stück) | Ziel < 8.000 € (A) |
| Energiekosten | < 1 €/Tag |

## 8. Offene Fragen für den Besuch vor Ort

Mitnehmen: Maßband, Neigungs-App, Fotos, Skizze des Hofs.

1. Wie breit sind die **Stallgasse, die Boxentüren und das Stalltor**? Gibt es Schwellen, Rinnen oder Stufen?
2. **Weg zum Mistplatz:** Wie lang ist er, welcher Untergrund, welche Steigung? Wie sieht der Weg im Winter aus?
3. **Mistplatz:** Ist es eine ebenerdige Platte oder ein Container? Gibt es eine Kante, über die gekippt werden muss? Wer schiebt den Haufen zusammen?
4. **Menge:** Wie viele Boxen, wie viele Schubkarren bzw. Container pro Tag? Wie lange dauert das Misten heute, und wie viele Personen sind dabei?
5. Wie groß sind die **Container**: Maße, Gewicht voll, Räder? (für das V2-Modul)
6. Laufen **Pferde in der Gasse**, während gemistet wird? Wie reagieren sie auf Maschinen (Teleskoplader)?
7. **Neuer Stall:** Ab wann wird geplant, wer plant? Was kann man jetzt noch vorsehen (Gassenbreite, Rampe, Ladepunkt)?
8. Was **kostet heute** eine Stunde Teleskoplader inklusive Fahrer? Was müsste ein Gerät können, damit sie dafür bezahlen würden? (Erst fragen, nachdem der Schmerz klar ist.)

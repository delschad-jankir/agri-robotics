# Kostenschätzung – Mist-Shuttle V1

Stand 30.10.2026 · Netto-Preise, Einzelstück · **Schätzung**: Katalog- und Marktpreise, noch keine Angebote eingeholt. Spannweite = günstige Zukaufteile bzw. Industriequalität.

## 1. Prototyp 1 (voll autonom), Hardware

| Baugruppe | Inhalt | von € | bis € |
|---|---|---:|---:|
| **Rahmen** | Rohre S235, Laserteile, Schweißen in Lohnfertigung, Feuerverzinken | 600 | 1.100 |
| **Mulde + Pendelklappe** | Blech 3/4 mm lasern, kanten, schweißen, verzinken, pulvern; Bolzen, Buchsen | 1.050 | 1.900 |
| **Räder + Lagerung** | 4 × Rad 4.00-8 AS-Profil, 4 Stummelwellen, 4 × Flanschlager UCF206 | 310 | 580 |
| **Fahrantrieb** | 4 × BLDC 48 V 750 W + Schneckengetriebe i ≈ 40 + Haltebremse | 1.400 | 2.800 |
| | Motorregler (4 Kanäle, CAN) | 400 | 1.000 |
| **Kipphydraulik** | Teleskopzylinder 4-stufig ¹ | 300 | 500 |
| | Kipperaggregat 24 V einfachwirkend ² + DC/DC 48→24 V | 300 | 650 |
| | Schläuche, Senkbremsventil, Drucksensor, Endlagensensor | 100 | 250 |
| **Energie** | LiFePO4 48 V 100 Ah mit BMS ³ | 600 | 1.000 |
| | Ladegerät 48 V / 20 A, Ladebuchse | 200 | 500 |
| | 2 Gehäuse Edelstahl IP65 | 300 | 700 |
| **Rechner + Sensorik** | Embedded-Rechner (GPU, z. B. Jetson-Klasse) | 500 | 1.200 |
| | 3D-Lidar 360° (z. B. Livox Mid-360) ⁴ | 750 | 1.100 |
| | Stereokamera vorn, Tiefenkamera hinten | 300 | 800 |
| | RTK-GNSS-Modul + Antenne (für den Hof) | 300 | 600 |
| **Sicherheit** | 2 Schaltleisten + Auswertung, Sicherheitsrelais bzw. -steuerung, 2 Not-Halt, Funk-Not-Halt, Rundumleuchte | 800 | 1.800 |
| **Verkabelung** | Kabel, Stecker IP67, Sicherungen, Hauptschütz | 300 | 600 |
| **Summe** | | **8.510** | **17.080** |
| Reserve 10 % | Nacharbeit, Ersatzteile, Versand | 850 | 1.710 |
| **Prototyp 1 gesamt** | | **≈ 9.400** | **≈ 18.800** |

**Realistischer Planwert: ≈ 12.000 €** (Mischung aus günstigen und Industrieteilen).

Nicht enthalten: eigene Arbeitszeit (Konstruktion, Software, Montage), Werkzeug, Fahrten zum Betrieb sowie externe Prüfungen (siehe 3.).

## 2. Günstiger Einstieg: Funktionsmuster ferngesteuert

Für den ersten Test beim Betrieb reicht ein **ferngesteuertes** Fahrzeug. Damit lassen sich Akzeptanz, Pferde, Traktion und Kippen klären, bevor Geld in die Autonomie fließt.

| Weglassen | spart |
|---|---:|
| Lidar, Kameras, GNSS, Rechner | 1.850 – 3.700 € |
| Teile der Sicherheitstechnik (Funk-Not-Halt bleibt) | 400 – 900 € |
| 2 statt 4 angetriebene Räder (Testbetrieb eben) | 700 – 1.400 € |
| dafür neu: Fernsteuerung (Industrie-Funk mit Not-Halt) | kostet + 300 – 600 € |

→ **Funktionsmuster ≈ 6.500 – 13.000 € inkl. 10 % Reserve, Planwert ≈ 8.000 €** (Mechanik und Antrieb sind dieselben wie bei Prototyp 1 und werden später weiterverwendet. Die Autonomie kommt dann für ≈ 3–5 k€ dazu.)

## 3. Weitere Kosten auf dem Weg zum Produkt (grob)

| Posten | Größenordnung | Bemerkung |
|---|---|---|
| Risikobeurteilung, Sicherheitskonzept, CE nach Maschinenverordnung (EU) 2023/1230 | 10.000 – 40.000 € | stark abhängig vom Umfang, externe Begleitung empfohlen |
| Festigkeitsnachweis (FEM), Detailkonstruktion, Zeichnungen | eigene Leistung oder 3.000 – 8.000 € extern | |
| Software (Navigation, Sicherheit, App) | Hauptaufwand des Teams | |
| **Herstellkosten in Serie** (≥ 50 Stück/Jahr) | grob **6.000 – 9.000 €/Stück** | Mengenrabatte Elektronik, Laserteile im Los, Sensorik günstiger |

## 4. Betriebskosten

- Strom: ≈ 1,5 kWh/Tag × 0,35 €/kWh ≈ **0,50 €/Tag**
- Wartung: Reifen, Lager, Hydrauliköl, Schaltleisten ≈ 150–300 €/Jahr (Schätzung)

## Quellen für Preisanker

¹ 3-stufige Kipper-Teleskopzylinder um ~270–330 € netto/brutto: [eBay](https://www.ebay.de/itm/193483481330), [Kleinanzeigen Agrotech](https://www.kleinanzeigen.de/pro/Agrotech-GmbH); 4-stufig Ø91/76/61/46: [eBay](https://www.ebay.de/itm/193472827883)
² 24-V-Kipperaggregate ~210–530 €: [eBay hydraulicsshop24](https://www.ebay.de/str/hydraulicsshop24), [eBay 24V einfachwirkend](https://www.ebay.de/itm/256040699199)
³ LiFePO4 48 V 50 Ah ~300–390 € (100 Ah entsprechend ~600–900 €): [mein-deal](https://www.mein-deal.com/?p=1939369), [eBay](https://www.ebay.de/itm/336431474591)
⁴ Livox Mid-360(S) ~750–810 € bei [OpenELAB](https://openelab.io/de/collections/new-arrivals?page=1); Herstellerseite [livoxtech.com](https://www.livoxtech.com/mid-360)

Alle anderen Positionen sind Erfahrungswerte bzw. Schätzungen und müssen mit Angeboten belegt werden.

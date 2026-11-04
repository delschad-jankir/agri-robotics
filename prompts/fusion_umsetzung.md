# Auftrag: Selbstladender Mist-Shuttle (autonomer Mini-Lader) als professionelles Fusion-Modell

Du arbeitest in einer **lokalen Claude-Code-Session auf Delschads Rechner**, auf dem **Autodesk Fusion** installiert und ein **Fusion-MCP-Server** eingerichtet ist. Ziel ist ein **natives, parametrisches Fusion-Modell** des verbesserten Fahrzeugs: ein **vollautomatischer, selbstladender Mist-Shuttle**. Er nimmt den Mist, den die Arbeiter vor die Boxentür in die Stallgasse werfen, **selbst mit einer Dunggabel-Schaufel auf**, fährt autonom zum Mistplatz, **kippt die Schaufel nach vorn aus** und setzt bzw. schiebt den Haufen. Danach kommt er zurück. Es muss mechanisch stimmen: keine Kollisionen, keine frei schwebenden Teile, Gelenke mit realistischen Grenzen, plausible Massen und Schwerpunkte, Standsicherheit, Antriebs- und Festigkeitsnachweise, und das Material fällt beim Entleeren frei vom Fahrzeug.

Das bisherige Modell ist **kein** Fusion-Modell. Es ist Python-Code (build123d) plus ein STEP-Export. Es dient als Referenz und Lernquelle. In Fusion wird **neu und besser** konstruiert, nicht nur importiert.

Lies diesen Prompt ganz, bevor du anfängst. Arbeite die Phasen der Reihe nach ab und zeig Delschad nach jeder Phase den Stand (Bilder plus kurze Zusammenfassung).

---

## Phase 0 – Kontext lesen (Pflicht)

| Datei | Wozu |
|---|---|
| `AGENTS.md` | Regeln des Repos (öffentlich, keine personenbezogenen Daten) |
| `docs/01_gespraech.md` | Gesprächsnotiz (enthält Übertreibungen, siehe Phase 5) |
| `docs/02_lastenheft.md` | Anforderungen, Annahmen (A), Fragen für den Besuch |
| `docs/03_konzept.md` | Konzept V1, Prüfergebnisse, Auslegung, Risiken |
| `docs/04_kosten.md` | Kostenschätzung |
| `cad/model.py`, `cad/kin.py`, `cad/check.py`, `cad/calc.py` | Referenzmodell V1: Maße, Kinematik, Prüflogik |
| `out/mist_shuttle_v1.step` | Referenzgeometrie V1 (nur zum Vergleichen, nicht als Basis) |
| `docs/img/` | Bilder und Videos V1 |

---

## Ausgangslage: Was der Landwirt wirklich gesagt hat

Wörtlich aus dem Transkript (anonymisiert):

> „Die erste Idee wäre, um dieses Misten ein bisschen zu erleichtern, dass man einen Roboter hat mit einem Dumper, also mit einer Mulde quasi. Da wird dann erst mal noch händisch der Mist reingeworfen. Aber dieser Roboter fährt dann zumindest schon mal selbstständig zum Mistplatz, wirft ihn ab und kommt wieder zurück zur Box. […] Weiß ich jetzt nicht, ob das … Also, das habe ich mir letztens mal überlegt. Das wäre schon mal ein guter Einstieg.“

> „Wir haben da Saisonkräfte. Die haben sehr große Container, wo immer der Mist reingeladen wird. Die müssen dann auch erst mal aus der Stallgasse rausgeschoben werden. Dann kommt jemand mit einem Teleskoplader und fährt den Container zum Mistplatz. Also auch wieder eine Person, die quasi die ganze Zeit nur am Traktorfahren ist. […] Und dieses Schieben durch die Stallgasse ist natürlich auch etwas, was körperlich anstrengend ist.“

> „Wir wollen demnächst auch noch mal einen Stall bauen und den jetzt so planen, dass der möglichst in Zukunft relativ automatisch bearbeitet werden kann.“

**Nicht gesagt, nur angenommen:** dass es Pferde sind (naheliegend wegen „Box“ und „Misten“), Zahl der Boxen, Mistmenge, Containergröße, Weglänge, ob der Teleskoplader die Container auch auskippt. Diese Punkte **niemals als Fakt** darstellen.

---

## Was an V1 („Mist-Shuttle“) falsch bzw. zu schwach war – das muss besser werden

1. **Material fällt aufs eigene Fahrzeug.** Bei 55° Kippwinkel liegt die Abwurfkante der Mulde bei x ≈ −712 mm und z ≈ 263 mm, direkt über Heck-Schaltleiste, Heckkamera und Rahmenende (x −720 … −775, z bis 225). Die alte Prüfung hat nur Bauteile gegeneinander geprüft, **nicht den Fallweg des Materials**.
2. **Zu kompliziert für 0,3 m³:** ein verkleinerter Lkw-Kipper mit 4-stufigem Teleskopzylinder (1,14 m Hub), Pendelklappe und einer Klappenverriegelung, die nie konstruiert wurde. Die Klappe hängt bei 55° nur 24 mm über dem Boden.
3. **Passt nicht zum Ablauf des Betriebs.** Die kleine Mulde (0,32 m³) ersetzt die großen Container. Das bedeutet viele Fahrten, und während das Fahrzeug unterwegs ist, wissen die Arbeiter nicht, wohin mit dem Mist. Es nimmt nur den Transport ab, sonst nichts.
4. **Darstellung:** Der Mist war in der Animation ein starrer Block, der durch Klappe und Boden glitt.
5. Frühere Befunde der V1-Prüfung, die als Lehre gelten: zu wenig Zylinderhub, Zylinderfuß kollidiert mit der Gabel, Stange dringt in die Kopfgabel ein, Zylinderrohr streift den Querträger. **Gelenkbereiche immer über den ganzen Bewegungsweg prüfen.**
6. Traktion: Auf einer mit Mist verschmierten 15-%-Rampe (μ ≈ 0,3) ist die übertragbare Zugkraft (≈ 1,74 kN) gerade so groß wie der Bedarf, ohne Reserve.

## Recherche-Ergebnisse, die du nutzen sollst

- **Kleine Elektro-Dumper** kippen fast immer **nach vorn mit einer Frontkippmulde**: schräge Vorderwand, **keine Klappe**, Drehpunkt nahe der Vorderachse, kurzer Hydraulikzylinder unter der Mulde. Billige Geräte kippen sogar von Hand mit Gasfedern. Beim **Hochkipper** wird die Mulde erst angehoben und dann gekippt, z. B. Wacker Neuson DT10e (Datenblatt nennt Front- und Hochkippmulde) oder Elektro-Dumper mit Scherenhub.
- **Selbstkippbehälter für Stapler:** kein eigener Antrieb. Eine Verriegelung wird gelöst (Seilzug oder Kontaktplatte), dann kippt der volle Behälter durch die Schwerkraft über **Abrollkufen** und richtet sich leer wieder auf. Manche haben eine Abfangbremse bei etwa 90°.
- **Mining-Muldenkipper** fahren ohne Heckklappe. Stattdessen ist das Heck hochgezogen („tail chute“), und der Drehpunkt sitzt am Rahmenende, damit das Material frei fällt.
- **Selbstladende Mini-Dumper** gibt es, z. B. Deleks M8000 mit Ladeschaufel, die das Material vorn aufnimmt und in die Mulde kippt. Hoflader nutzen für langes, verfilztes Stroh die **Dunggabel mit hydraulischem Niederhalter** („Krokodilgebiss“).
- Bei Kompaktladern gilt als Vorbild für die Nennlast: **Nennlast ≤ 50 % der statischen Kipplast** (Größenordnung nach ISO 14397-1, Norm im Detail prüfen).
- **Autonome Transportwagen** gibt es schon, z. B. Burro (folgt Menschen, fährt A→B, Obst- und Gemüsebau). Prototypen für Pferdeställe: POOPY (Gerard Robotics), STADY/Zauberzeug (EU-Projekt), ein schwedischer Stallhelfer (RISE). Rinderställe haben autonome Entmistungsroboter. → **Die Technik ist im Kern gelöst. Der Wert liegt darin, dass das Fahrzeug zum Ablauf im Betrieb passt.**

---

## Phase 1 – Konzept festlegen (Vorgabe von Delschad + offene Punkte klären)

**Festgelegt:** vollautomatischer, **selbstladender Mist-Shuttle** in Bauform eines **kleinen autonomen Laders**. Die Schaufel ist zugleich Transportbehälter, es gibt keine separate Mulde.

**Ablauf, den das Modell können muss:**
1. Arbeiter misten die Box von Hand und werfen den Mist **vor die Boxentür in die Stallgasse** (Haufen ca. 0,1–0,2 m³ je Box (A)).
2. Der Shuttle fährt zum Haufen, senkt die Schaufel auf den Boden (Schneidkante schabt wie ein Schiebeschild), fährt hinein, **schließt den Niederhalter**, kippt die Schaufel an (Ankippen nach hinten, damit nichts herausfällt) und hebt leicht an.
3. Er wiederholt das an weiteren Boxen, bis die Schaufel voll ist.
4. Er fährt autonom zum Mistplatz, hebt die Schwinge, öffnet den Niederhalter, **kippt die Schaufel nach vorn aus**. Das Material fällt frei vor dem Fahrzeug.
5. Optional schiebt er den Haufen zusammen bzw. setzt ihn höher (Hubhöhe des Schaufeldrehpunkts als Parameter, Ziel ≥ 1,2 m (A)).
6. Er fährt zurück und meldet sich bereit.

**Bauform, als Startpunkt (mit Zahlen begründen oder verbessern):**
- 4WD Skid-Steer, Elektroantrieb 48 V, Schaufel vorn, **Akku und Technik hinten als Gegengewicht**
- Ladeschwinge mit 2 Hubarmen, Hubzylinder, Kippzylinder, möglichst **Parallelführung** bzw. mechanische Selbstnivellierung, damit beim Heben nichts ausschüttet
- **Dunggabel-Schaufel mit Niederhalter** (Zinken unten, hydraulischer Greifer oben), Fassungsvermögen 0,25–0,35 m³ (A)
- Elektrohydraulisches Aggregat (Pumpe, Ventile, Senkbremsventile bzw. Rohrbruchsicherung)
- Sensorik: 3D-Lidar, Kamera für Haufenerkennung vorn, Heckkamera, Schaltleisten, Not-Halt
- Breite ≤ Boxentür − 200 mm, Ziel **≤ 800 mm**

**Vor dem Konstruieren mit Delschad klären (AskUserQuestion), sonst Annahmen (A) setzen:**
1. Ist es für den Betrieb okay, dass Mist kurz in der Stallgasse liegt? Wenn nicht: Ladeplatz vor dem Stall oder doch Container. → Notieren, nicht selbst entscheiden.
2. Einstreu: Stroh oder Späne? (Langes Stroh braucht den Niederhalter, Späne nicht unbedingt.)
3. Mistplatz: ebenerdige Platte, Platte mit Wand (Höhe?) oder Anhänger? → bestimmt die Hubhöhe.
4. Türbreite, Gassenbreite, Steigung zum Mistplatz bekannt? *(Default (A): Tür ≥ 1,0 m, Gasse ≥ 2,5 m, ≤ 15 %)*

**Nicht Teil dieses Auftrags:** Mist aus der Box selbst heraussuchen (Abäppeln). Das bleibt Handarbeit und ist ein späteres, eigenes Thema.

Schreibe Entscheidungen und Begründung nach `docs/06_konzept_v2.md`: morphologischer Kasten (Schaufel vs. Mulde + Ladeschaufel, Parallelführung ja/nein, Hydraulik vs. elektrisch, Rad vs. Raupe) mit Bewertungstabelle. Aktualisiere `docs/02_lastenheft.md` um die neuen Funktionen (Selbstladen, Haufen setzen, Gasse schaben).

## Phase 2 – Verbindung zu Fusion (vorhandenen Fusion-MCP nutzen)

Delschad hat einen **Fusion-MCP-Server** in Claude Code eingerichtet. Nutze ihn als Hauptweg.

1. **Werkzeuge erkunden:** Liste die Tools des Fusion-MCP auf und notiere in `fusion/README.md`, was sie können. Wichtig sind: beliebigen Fusion-Python-Code ausführen, Geometrie erzeugen, Parameter setzen, Gelenke anlegen/bewegen, Interferenzanalyse, physikalische Eigenschaften, Viewport-Bild speichern, STEP/F3D exportieren.
2. **Verbindung testen:** Mini-Test über den MCP (Würfel 100 mm erzeugen, Masse abfragen, Screenshot speichern) und das Ergebnis selbst prüfen. Läuft Fusion nicht oder ist der MCP nicht verbunden, Delschad Bescheid geben.
3. **Lücken schließen, nicht ersetzen:** Kann der MCP etwas Benötigtes nicht, und hat er ein Tool für „Python-Skript ausführen“, dann darüber gehen. Fehlt auch das, ergänze **minimal** ein eigenes Add-in in `fusion/bridge_addin/`: ein Ordner `fusion/inbox/` wird überwacht, Skripte werden über `app.fireCustomEvent` im Fusion-Hauptthread ausgeführt, Ergebnisse und Tracebacks landen in `fusion/outbox/`. Delschad lädt es einmalig über Dienstprogramme → Add-Ins → „+“.
4. **Reproduzierbarkeit:** Auch wenn du über den MCP interaktiv arbeitest, muss das Endergebnis als Skripte im Repo liegen (`fusion/build_model.py`, `fusion/checks.py`). Damit lässt sich das Modell jederzeit neu erzeugen und prüfen.
5. **Einheiten:** Die Fusion-API rechnet intern in **cm** (Längen) und **rad** (Winkel). Masse kommt in kg, Schwerpunkte in cm. Konsequent umrechnen und in einem Test prüfen.
6. Keinen Code aus dem Internet ungeprüft ausführen.

## Phase 3 – Natives, parametrisches Fusion-Modell

Ein Skript `fusion/build_model.py` erzeugt das komplette Modell **reproduzierbar** in einem neuen Design. Erneut ausgeführt, entsteht dasselbe Modell, also kein Klicken von Hand.

**Modellierungsregeln (wie in der Konstruktionsabteilung):**
- `design.designType = ParametricDesignType`. **Alle Hauptmaße als User Parameters** mit Kommentar: Spur, Radstand, Raddurchmesser, Behältermaße, Hubhöhe, Rahmenprofil, Wandstärken, Drehpunktlage usw. Abhängige Maße als Ausdrücke.
- **Komponentenstruktur** wie eine Stückliste: Rahmen (Schweißbaugruppe), Fahrwerk (4 Radmodule: Rad, Felge, Welle, Lager, Getriebe, Motor), Ladeschwinge (Hubarme, Querrohr, Lagerböcke), Schaufel mit Dunggabelzinken, Niederhalter, Hydraulik (Hub-, Kipp-, Niederhalterzylinder, Aggregat, Tank), ggf. Parallelführung (Koppelstangen/Umlenkhebel), Technikmodul hinten (Akku, Steuerung, Gegengewicht), Sensorik, Sicherheit (Schaltleisten, Not-Halt), Normteile (Bolzen, Buchsen). **Je Bauteil eine Komponente**, Körper sinnvoll benannt, **nur ASCII-Namen**.
- Geometrie über **Skizzen + Features** (Extrusion, Rotation, Blech, wo sinnvoll), nicht als importierte Netze. Zukaufteile (Motoren, Getriebe, Lager, Zylinder, Räder) als **vereinfachte Hüllgeometrie mit echten Katalogmaßen**. Notiere die Quelle der Maße.
- **Materialien** aus der Fusion-Materialbibliothek zuweisen (Stahl, Edelstahl, Aluminium, Gummi, Kunststoff). Für Zukaufteile ohne realistische Dichte die Katalogmasse über einen Ersatzkörper oder eine Korrekturtabelle abbilden und dokumentieren.
- **Gelenke** für alles, was sich bewegt: Drehgelenke (Räder, Schwingenlager, Schaufeldrehpunkt, Niederhalter, alle Zylinderaugen, Koppeln), Schiebegelenke (Kolbenstangen in Zylindern), mit **realistischen Grenzen** (Min/Max) entsprechend Anschlägen bzw. Hub. Starre Verbindungen über **As-built Joints oder Rigid Groups**. Rahmen **gegroundet**.
- Erscheinungen (Farben) sinnvoll: Rahmen anthrazit, Behälter signalfarben, Zukaufteile realistisch.
- **Ladung** als eigener Körper (Mist, 750 kg/m³ nass (A), gehäuft nach Schaufelnorm), nur für Masse/Schwerpunkt und Darstellung.
- Zylinder als echte Zylinder-Kolben-Paare mit Einbaulänge, Hub, Kolben- und Stangendurchmesser, sodass die Kinematik der Schwinge **aus den Gelenken folgt** und nicht nachgebaut wird.

## Phase 4 – Prüfungen in Fusion (Pflicht, automatisiert, Ergebnis als JSON)

Ein Skript `fusion/checks.py` erzeugt `fusion/outbox/check_report.json` und eine lesbare Zusammenfassung. **Erst wenn alles grün ist, gilt das Modell als fertig.** Jeder Fehler wird behoben, nicht wegdiskutiert.

| # | Prüfung | Umsetzung / Kriterium |
|---|---|---|
| P1 | Kollisionen in Ruhelage | `design.analyzeInterference` über alle Körper, Volumen > 1 mm³ = Fehler. Gewollte Presssitze explizit auflisten. |
| P2 | **Kollisionen über alle Bewegungen** | Jedes Gelenk in Schritten (≤ 2,5° bzw. ≤ 10 mm) über den ganzen Bereich fahren (`jointMotion.rotationValue` / `slideValue`), bei jedem Schritt Interferenz prüfen. Auch Kombinationen (z. B. Hub oben + Kippen). Mindestabstände kritischer Paare protokollieren. |
| P3 | Keine frei schwebenden Teile | Jede Komponente ist über Gelenke/Rigid Groups mit dem gegroundeten Rahmen verbunden (Graph-Prüfung). Jede Verbindung hat **geometrischen Kontakt** (Abstand ≤ 0,3 mm). |
| P4 | Masse und Schwerpunkt | `getPhysicalProperties` je Komponente und gesamt: leer, beladen, in jeder Bewegungsstellung. |
| P5 | Standsicherheit | Statische Kippgrenze nach vorn, hinten und zur Seite aus Schwerpunkt und Aufstandsfläche, **in allen Stellungen der Schwinge und Schaufel**, leer und beladen. Fahrstellung: **≥ 15° (≙ 27 %)** in jeder Richtung, dazu dynamischer Zuschlag fürs Bremsen (0,3 g). **Kipplast nach vorn** bei weitester Ausladung bestimmen: **Nennlast ≤ 50 % der statischen Kipplast**. Gegengewicht hinten danach auslegen. |
| P6 | **Materialfluss beim Auskippen** | Bei Auskippstellung zeigt der Schaufelboden **≥ 45° nach unten**. Die Schaufelkante liegt horizontal **≥ 300 mm vor** dem vordersten Fahrzeugteil (Räder, Schaltleiste, Rahmen), und im Fallkegel (±15°) unter der Kante liegt kein Fahrzeugteil. Auskipphöhe (Unterkante Schneide) als Ergebnis ausgeben. Geometrisch prüfen, nicht nur optisch. |
| P7 | **Laden** | (a) Schneidkante liegt in Ladestellung **auf dem Boden**, ohne dass Räder abheben. (b) **Eindringkraft**: Die Zugkraft aller 4 Räder (Traktionsgrenze μ = 0,3 und 0,5) reicht, um die Schaufel in einen Misthaufen zu schieben (Ansatz und Annahmen dokumentieren). (c) **Losbrechkraft** von Hub- und Kippzylinder an der Schneide ≥ Gewicht der vollen Schaufel × 2. (d) Beim Heben von Bodenhöhe bis Transporthöhe kippt die Schaufel nicht nach vorn (Parallelführung bzw. Kippwinkel ≥ 10° nach hinten). (e) Niederhalter schließt dicht auf die Zinken, ohne die Schaufel zu berühren. |
| P8 | Antrieb und Hydraulik | Fahrantrieb: 15 % Steigung beladen, Rollwiderstand Schotter, Drehen auf der Stelle, Traktion μ = 0,3/0,5. **Zylinderkräfte über den ganzen Hub- und Kippweg** (Kurve), daraus Systemdruck ≤ 160 bar, Pumpenförderstrom für Hubzeit ≤ 5 s, Aggregatleistung. Ausgewählte Zukaufteile mit Reserve ≥ 1,3. Energiebedarf pro Tag → Akkugröße. |
| P9 | Festigkeit (Handrechnung) | Bolzen (Abscheren, Biegung, Lochleibung), **Hubarme** (Biegung bei voller Last und weitester Ausladung, Knicken der Zylinder bei vollem Hub), Schwingenlager, Rahmen, Schaufel. Sicherheit **≥ 2,0 statisch** mit **Stoßfaktor 2** (Fahren über Schwellen mit angehobener Last). Rechne in `fusion/calc_strength.py` und dokumentiere. Für Hubarme und Rahmen eine **Fusion-Simulation (Statische Spannung)** vorbereiten und Delschad die Klickschritte geben, falls die API das nicht automatisiert. |
| P10 | Bauraum | Breite ≤ 800 mm (bzw. Boxentür − 200 mm), Bodenfreiheit ≥ 120 mm in Fahrstellung, Hüllkreis beim Drehen auf der Stelle **mit Schaufel in Transportstellung** ≤ Gassenbreite − 300 mm, maximale Bauhöhe in Fahrstellung ≤ 1.400 mm. |
| P11 | Montier- und Wartbarkeit, Sicherheit | Jede Schraubverbindung ist mit Werkzeug erreichbar. Akku tauschbar, Abschmierstellen zugänglich. **Quetsch- und Scherstellen** an Schwinge und Niederhalter benennen und Schutzkonzept beschreiben (Abstände nach EN ISO 13857 bzw. Sicherheitsabstände prüfen). Senkbremsventile an Hub- und Kippzylinder. |

## Phase 5 – Dokumentation, Medien, Repo

1. **Exporte:** `out/<name>_v2.f3d` (Fusion-Archiv), `out/<name>_v2.step`, Stückliste `out/<name>_v2_bom.csv` (Teil, Anzahl, Material, Masse, Zukauf/Fertigung, Quelle).
2. **Bilder aus Fusion** (`app.activeViewport.saveAsImageFile`): Ansicht vorn 3/4, hinten 3/4, Seite, Front, Draufsicht, Explosionsansicht, Details (Schaufel mit Niederhalter, Schwingenlager, Radmodul, Hydraulik), Ladestellung, Transportstellung, **Auskippstellung mit Fallkegel**, maximale Hubhöhe, Größenvergleich mit Person → `docs/img/v2_*.png`.
3. **Animationen aus Fusion:** Gelenke schrittweise fahren, Viewport-Bilder speichern, mit ffmpeg zu MP4 zusammensetzen: (1) Ladezyklus (absenken, einfahren, Niederhalter schließen, ankippen, heben), (2) Auskippen am Mistplatz und Haufen setzen, (3) volle Bewegung von Schwinge und Schaufel mit eingeblendeten Zylinderkräften und Kippsicherheit, (4) Rundumansicht, (5) Explosion. **Material darf nicht durch Bauteile gleiten.** Lieber einen einfachen, aber physikalisch plausiblen Ablauf darstellen (Partikel als kleine Körper oder ausblenden, sobald es die Kante verlässt) und klar „Schema“ dranschreiben.
4. **Dokumente aktualisieren:**
   - `docs/06_konzept_v2.md`: Konzept, Varianten, Prüfergebnisse P1–P11 als Tabelle, Auslegung, offene Punkte, Grenzen des Modells.
   - `docs/03_konzept.md`: oben einen Hinweis ergänzen, dass V1 durch V2 ersetzt ist, und die V1-Fehler aus diesem Prompt ehrlich dokumentieren.
   - `docs/01_gespraech.md` **korrigieren**: „Pferdebetrieb“ ist eine Annahme. Der Besuch wurde von Delschad angeboten, nicht vom Landwirt. Seine Unsicherheit („Weiß ich jetzt nicht, ob das …“) wörtlich aufnehmen. „Betriebsleitung“ und „Telefon/Video“ sind unbekannt.
   - `docs/05_marktrecherche.md`: bestehende Lösungen (siehe Recherche oben, mit Links) und die offene Frage, **warum sie sich im Pferdestall nicht durchgesetzt haben**.
   - `docs/04_kosten.md`: Kosten für V2 neu schätzen (Quellen oder klar als Schätzung). Hydraulik, Schwinge und Niederhalter kommen dazu, Teleskopzylinder und Klappe fallen weg.
   - `docs/02_lastenheft.md`: neue Funktionen und Fragen für den Besuch (Mist in der Gasse okay? Stroh oder Späne? Mistplatz-Bauart?).
   - `AGENTS.md` und `README.md`: neuer Stand, Pipeline für Fusion.
5. **Commits:** klein und beschreibend, auf `main` oder einem Branch nach Absprache mit Delschad. Keine Namen, Orte oder Kontaktdaten. Keine großen Zwischendateien (Frames, Logs) committen, `.gitignore` erweitern.

---

## Definition of Done

- [ ] `fusion/build_model.py` erzeugt das Modell reproduzierbar, alle Hauptmaße als User Parameters.
- [ ] Alle Bewegungen sind als Gelenke mit Grenzen angelegt und in Fusion von Hand bewegbar.
- [ ] `fusion/checks.py` meldet **0 Fehler** für P1–P11. Der Bericht liegt im Repo.
- [ ] Festigkeits- und Antriebsrechnung dokumentiert, Sicherheiten erfüllt.
- [ ] `.f3d`, `.step`, BOM, Bilder und Animationen exportiert und committet.
- [ ] Dokumente aktualisiert, Annahmen (A) markiert, Übertreibungen korrigiert.
- [ ] Delschad hat die Bilder gesehen und das Konzept bestätigt.

## Arbeitsweise

- Bei Unklarheit über Ablauf oder Maße **fragen statt raten**. Annahmen klar mit (A) markieren.
- **Ehrlich berichten:** Wenn eine Prüfung fehlschlägt oder etwas in Fusion nicht automatisierbar ist, sag es und schlag den manuellen Weg vor.
- Die einfachste Lösung, die die Anforderungen erfüllt, schlägt die eindrucksvollste. Orientiere dich an bewährten Hofladern und Kompaktladern, statt Neues zu erfinden.
- Keine Produktversprechen. Es bleibt ein Konzept, bis es beim Betrieb getestet ist.

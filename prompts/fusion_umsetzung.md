# Auftrag: Stall-Fahrzeug als professionelles, funktionsfähiges Fusion-Modell

Du arbeitest in einer **lokalen Claude-Code-Session auf Delschads Rechner**, auf dem **Autodesk Fusion** installiert und ein **Fusion-MCP-Server** eingerichtet ist. Ziel ist ein **natives, parametrisches Fusion-Modell** des verbesserten Fahrzeugs. Es muss mechanisch stimmen: keine Kollisionen, keine frei schwebenden Teile, Gelenke mit realistischen Grenzen, plausible Massen und Schwerpunkte, Standsicherheit, Antriebs- und Festigkeitsnachweise, und das Material fällt beim Entleeren frei vom Fahrzeug.

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
- **Autonome Transportwagen** gibt es schon, z. B. Burro (folgt Menschen, fährt A→B, Obst- und Gemüsebau). Prototypen für Pferdeställe: POOPY (Gerard Robotics), STADY/Zauberzeug (EU-Projekt), ein schwedischer Stallhelfer (RISE). Rinderställe haben autonome Entmistungsroboter. → **Die Technik ist im Kern gelöst. Der Wert liegt darin, dass das Fahrzeug zum Ablauf im Betrieb passt.**

---

## Phase 1 – Konzept festlegen (mit Delschad klären, bevor du konstruierst)

Stell Delschad diese Fragen (AskUserQuestion). Was er nicht weiß, wird zur markierten Annahme (A):

1. Wie groß sind die Container des Betriebs (L × B × H, Volumen), haben sie **Gabeltaschen oder Räder**, und wie schwer sind sie voll? *(Default (A): 0,75 m³, ~500 kg voll, Stapler-Kippbehälter-Format)*
2. Kippt heute der Teleskoplader die Container aus, und wohin: ebenerdige Mistplatte, über eine Wand, in einen Anhänger?
3. Breite der Boxentüren und der Stallgasse? *(Default (A): Tür ≥ 1,0 m, Gasse ≥ 2,5 m)*
4. Welche Variante soll gebaut werden? Empfehlung:

**Variante B – Container-Shuttle (empfohlen, weil sie zum heutigen Ablauf passt):**
- Das Fahrzeug **nimmt Container auf**, die die Arbeiter wie bisher befüllen. Zwei oder mehr Container wechseln sich ab: Einer wird befüllt, einer ist unterwegs, also keine Wartezeit.
- Es **fährt den Container bis an die jeweilige Box** (Folge- oder Positioniermodus), damit niemand Schubkarre fährt oder Container schiebt.
- Ist der Container voll, fährt es **autonom zur Mistplatte**. Entleert wird über einen **Selbstkippbehälter**: Verriegelung lösen, Schwerkraft kippt, leer richtet er sich wieder auf, also **kein eigener Kippzylinder**. Ein kleiner Aktor oder ein fester Anschlag an der Mistplatte löst die Verriegelung.
- **Rückfahrt mit Nutzlast:** Einstreu, Späne-Paletten oder Heu in den Stall.
- Die Aufnahme ist zu bewerten zwischen (a) Gabel vorn mit Gegengewicht (Stapler-Prinzip), (b) Portal/Straddle (Fahrzeug umfährt den Behälter, keine Kippgefahr nach vorn, aber breiter) und (c) Unterfahren mit Hubplatte (Behälter auf Füßen). Entscheide nach Stabilität, Breite (Boxentür!), Masse, Kosten und Einfachheit, **mit Zahlen**, und empfiehl eine.

**Variante A – verbesserter Mist-Shuttle (Rückfallebene):** Frontkippmulde nach Dumper-Vorbild (schräge Abwurfwand, keine Klappe, kurzer doppeltwirkender Zylinder, Drehpunkt nahe Vorderachse, Abwurfkante frei vor dem Fahrzeug). Die Mulde als **austauschbares Modul**, damit später Variante B möglich ist.

Schreibe die Entscheidung mit Begründung nach `docs/06_konzept_v2.md`, inklusive eines morphologischen Kastens und einer Bewertungstabelle.

---

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
- **Komponentenstruktur** wie eine Stückliste: Rahmen (Schweißbaugruppe), Fahrwerk (4 Radmodule: Rad, Felge, Welle, Lager, Getriebe, Motor), Hub/Aufnahme, Behälter, Technikmodul (Akku, Steuerung), Sensorik, Sicherheit (Schaltleisten, Not-Halt), Normteile (Bolzen, Buchsen). **Je Bauteil eine Komponente**, Körper sinnvoll benannt, **nur ASCII-Namen**.
- Geometrie über **Skizzen + Features** (Extrusion, Rotation, Blech, wo sinnvoll), nicht als importierte Netze. Zukaufteile (Motoren, Getriebe, Lager, Zylinder, Räder) als **vereinfachte Hüllgeometrie mit echten Katalogmaßen**. Notiere die Quelle der Maße.
- **Materialien** aus der Fusion-Materialbibliothek zuweisen (Stahl, Edelstahl, Aluminium, Gummi, Kunststoff). Für Zukaufteile ohne realistische Dichte die Katalogmasse über einen Ersatzkörper oder eine Korrekturtabelle abbilden und dokumentieren.
- **Gelenke** für alles, was sich bewegt: Drehgelenke (Räder, Kipp- und Drehpunkte, Klappen, Verriegelung), Schiebegelenke (Hub, Zylinderstufen), mit **realistischen Grenzen** (Min/Max) entsprechend Anschlägen bzw. Hub. Starre Verbindungen über **As-built Joints oder Rigid Groups**. Rahmen **gegroundet**.
- Erscheinungen (Farben) sinnvoll: Rahmen anthrazit, Behälter signalfarben, Zukaufteile realistisch.
- **Ladung** als eigener Körper (Mist, 750 kg/m³ nass, Annahme), nur für Masse/Schwerpunkt und Darstellung.

## Phase 4 – Prüfungen in Fusion (Pflicht, automatisiert, Ergebnis als JSON)

Ein Skript `fusion/checks.py` erzeugt `fusion/outbox/check_report.json` und eine lesbare Zusammenfassung. **Erst wenn alles grün ist, gilt das Modell als fertig.** Jeder Fehler wird behoben, nicht wegdiskutiert.

| # | Prüfung | Umsetzung / Kriterium |
|---|---|---|
| P1 | Kollisionen in Ruhelage | `design.analyzeInterference` über alle Körper, Volumen > 1 mm³ = Fehler. Gewollte Presssitze explizit auflisten. |
| P2 | **Kollisionen über alle Bewegungen** | Jedes Gelenk in Schritten (≤ 2,5° bzw. ≤ 10 mm) über den ganzen Bereich fahren (`jointMotion.rotationValue` / `slideValue`), bei jedem Schritt Interferenz prüfen. Auch Kombinationen (z. B. Hub oben + Kippen). Mindestabstände kritischer Paare protokollieren. |
| P3 | Keine frei schwebenden Teile | Jede Komponente ist über Gelenke/Rigid Groups mit dem gegroundeten Rahmen verbunden (Graph-Prüfung). Jede Verbindung hat **geometrischen Kontakt** (Abstand ≤ 0,3 mm). |
| P4 | Masse und Schwerpunkt | `getPhysicalProperties` je Komponente und gesamt: leer, beladen, in jeder Bewegungsstellung. |
| P5 | Standsicherheit | Statische Kippgrenze nach vorn, hinten und zur Seite aus Schwerpunkt und Aufstandsfläche, in allen Stellungen, leer und beladen. **≥ 15° (≙ 27 %)** in jeder Richtung, zusätzlich dynamischer Zuschlag fürs Bremsen (0,3 g). Beim Stapler-Prinzip: Lastmoment gegen Gegengewicht nachweisen. |
| P6 | **Materialfluss beim Entleeren** | Die Abwurfkante liegt bei Entleerwinkel **horizontal ≥ 150 mm** vor/hinter jedem Fahrzeugteil, und unterhalb der Kante liegt kein Fahrzeugteil im Fallkegel (±15°). Rutschwinkel für Mist mindestens 45° Bodenneigung beim Entleeren. Prüfe das geometrisch, nicht nur optisch. |
| P7 | Selbstkippbehälter (falls Variante B) | Voll: Schwerpunkt liegt nach dem Entriegeln **vor** dem Abrollpunkt der Kufen → kippt sicher. Leer: Schwerpunkt **hinter** dem Abrollpunkt → richtet sich selbst auf. Auch bei 50 % Füllung und anhaftendem Rest (10 %) prüfen. |
| P8 | Antrieb und Hub | Kräfte, Momente und Leistung über den ganzen Weg: Fahrantrieb (15 % Steigung, Rollwiderstand Schotter, Drehen auf der Stelle), Traktion bei μ = 0,3 und 0,5, Hubkraft und Hubgeschwindigkeit, Zylinder- bzw. Aktordruck. Ausgewählte Zukaufteile müssen mit Reserve ≥ 1,3 passen. |
| P9 | Festigkeit (Handrechnung) | Bolzen (Abscheren, Biegung, Lochleibung), Hauptträger (Biegung, Durchbiegung), Hubgabel/Hubplatte, Schweißnähte vereinfacht. Sicherheit **≥ 2,0 statisch** mit **Stoßfaktor 2** für Fahren über Schwellen. Rechne in `fusion/calc_strength.py` und dokumentiere. Für den Rahmen eine **Fusion-Simulation (Statische Spannung)** vorbereiten und Delschad die Klickschritte geben, falls die API das nicht automatisiert. |
| P10 | Bauraum | Breite ≤ Boxentür − 2 × 100 mm, Bodenfreiheit ≥ 120 mm, Hüllkreis beim Drehen auf der Stelle ≤ Gassenbreite − 300 mm, Ladekante ≤ 1.000 mm (Mistgabel). |
| P11 | Montier- und Wartbarkeit | Jede Schraubverbindung ist mit Werkzeug erreichbar (Plausibilitätsprüfung, dokumentieren). Akku tauschbar. Abschmierstellen zugänglich. |

## Phase 5 – Dokumentation, Medien, Repo

1. **Exporte:** `out/<name>_v2.f3d` (Fusion-Archiv), `out/<name>_v2.step`, Stückliste `out/<name>_v2_bom.csv` (Teil, Anzahl, Material, Masse, Zukauf/Fertigung, Quelle).
2. **Bilder aus Fusion** (`app.activeViewport.saveAsImageFile`): Ansicht vorn 3/4, hinten 3/4, Seite, Front, Draufsicht, Explosionsansicht, Details (Aufnahme, Entriegelung, Radmodul), **Entleerstellung mit Fallkegel** → `docs/img/v2_*.png`.
3. **Animationen aus Fusion:** Gelenke schrittweise fahren, Viewport-Bilder speichern, mit ffmpeg zu MP4 zusammensetzen: Aufnehmen des Containers, Fahren, Entleeren (Schwerkraftkippen und Wiederaufrichten), Abstellen, Rückfahrt mit Einstreu. **Material darf nicht durch Bauteile gleiten.** Lieber einen einfachen, aber physikalisch plausiblen Ablauf darstellen (Partikel als kleine Körper oder ausblenden, sobald es die Kante verlässt) und klar „Schema“ dranschreiben.
4. **Dokumente aktualisieren:**
   - `docs/06_konzept_v2.md`: Konzept, Varianten, Prüfergebnisse P1–P11 als Tabelle, Auslegung, offene Punkte, Grenzen des Modells.
   - `docs/03_konzept.md`: oben einen Hinweis ergänzen, dass V1 durch V2 ersetzt ist, und die V1-Fehler aus diesem Prompt ehrlich dokumentieren.
   - `docs/01_gespraech.md` **korrigieren**: „Pferdebetrieb“ ist eine Annahme. Der Besuch wurde von Delschad angeboten, nicht vom Landwirt. Seine Unsicherheit („Weiß ich jetzt nicht, ob das …“) wörtlich aufnehmen. „Betriebsleitung“ und „Telefon/Video“ sind unbekannt.
   - `docs/05_marktrecherche.md`: bestehende Lösungen (siehe Recherche oben, mit Links) und die offene Frage, **warum sie sich im Pferdestall nicht durchgesetzt haben**.
   - `docs/04_kosten.md`: Kosten für V2 neu schätzen (Quellen oder klar als Schätzung).
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
- Die einfachste Lösung, die die Anforderungen erfüllt, schlägt die eindrucksvollste. Ein Behälter, der durch die Schwerkraft kippt, ist besser als ein Zylinder, der dasselbe tut.
- Keine Produktversprechen. Es bleibt ein Konzept, bis es beim Betrieb getestet ist.

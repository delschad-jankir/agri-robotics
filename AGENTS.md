# AGENTS.md – agri-robotics

Gründungsidee von Delschad Jankir (KI/Data Science) und einem Partner mit Robotik-Hintergrund: Robotik für landwirtschaftliche Betriebe. Derzeitiger Fokus: **Pferdestall, Mist-Transport** (siehe `docs/01_gespraech.md`). Es gibt noch kein Produkt. Ziel sind Discovery-Gespräche (Mom Test) und ein glaubwürdiges, technisch sauberes Konzept.

## Harte Regeln

1. **Öffentliches Repo:** keine Namen von Gesprächspartnern, keine Hof-/Ortsangaben, keine Telefonnummern oder E-Mails. Gespräche nur anonymisiert zusammenfassen.
2. **Konstruktion wie ein Maschinenbauer:** Jede Modelländerung muss `python3 cad/check.py` mit **0 Fehlern** bestehen: keine Kollisionen (Ruhelage und ganzer Kippweg), keine freischwebenden Teile, alle Verbindungen mit Kontakt, Standsicherheit. Neue Teile brauchen einen Eintrag in `joints()` (Verbindung zum Rest).
3. Annahmen im Lastenheft mit **(A)** kennzeichnen und nach dem Besuch vor Ort ersetzen.
4. Preise nur mit Quelle oder klar als Schätzung markieren.
5. Nichts in Commits oder Dokumente schreiben, was nach Produktversprechen klingt. Es ist ein Konzept.

## Struktur

| Pfad | Inhalt |
|---|---|
| `docs/01_gespraech.md` | anonymisierte Gesprächsnotiz |
| `docs/02_lastenheft.md` | Anforderungen, Annahmen, Fragen für den Besuch |
| `docs/03_konzept.md` | Variantenwahl, Aufbau, Prüfergebnisse, Auslegung, Risiken |
| `docs/04_kosten.md` | Kostenschätzung Prototyp / Funktionsmuster / Serie |
| `docs/img/` | Renderings, Animationen (mp4/gif), Diagramme |
| `cad/model.py` | parametrisches CAD-Modell (build123d, mm, X vorn, Y links, Z oben) – Parameter oben in `P` |
| `cad/kin.py` | Kinematik (Kippwinkel → Lage aller Teile, Zylinder, Klappe, Räder) |
| `cad/check.py` | automatische Design-Review → `out/check_report.json` |
| `cad/calc.py` | Auslegung Antrieb/Energie → `out/calc_report.json` |
| `cad/export.py` | STEP-Baugruppe für Fusion 360 + STL/Posen für den Renderer |
| `cad/charts.py` | Diagramme aus den Prüfberichten |
| `render/` | three.js-Szene + Playwright-Renderer für Bilder und Videos |
| `out/mist_shuttle_v1.step` | aktuelle STEP-Baugruppe |
| `prompts/fusion_umsetzung.md` | **offener Auftrag:** V2 „selbstladender Mist-Shuttle“ (autonomer Mini-Lader mit Dunggabel-Schaufel) als natives, geprüftes Fusion-Modell |

## Pipeline

```bash
pip install -r cad/requirements.txt
cd cad && python3 check.py && python3 calc.py && python3 export.py && python3 charts.py
cd ../render && npm install
node render.mjs stills           # 12 Standbilder (1600×900)
node render.mjs tip 8772         # Animation Kippen (je Animation eigener Port → parallel möglich)
node render.mjs turn 8771 | explode 8773 | scenario 8774
```

Rendering läuft per Software-GL (SwiftShader): allein ~0,3–0,5 s/Bild, bei 4 parallelen Prozessen ~4–7 s/Bild. Besser nacheinander rendern.

## Stand

- **30.10.2026:** Lastenheft und Konzept V1 „Mist-Shuttle“ (autonomer Elektro-Hinterkipper, 0,32 m³) mit 52 Teilen. Alle Prüfungen bestanden. Kosten Prototyp ≈ 9–19 k€, Planwert 12 k€. Nächster Schritt: Besuch vor Ort, Annahmen messen.
- **04.11.2026:** Kritische Prüfung von V1: Material fällt beim Kippen auf die Heck-Schaltleiste, die Mechanik ist zu kompliziert, und das Fahrzeug passt nicht zum Container-Ablauf des Betriebs. Entscheidung Delschad: V2 wird ein vollautomatischer, selbstladender Mist-Shuttle (nimmt den Mist aus der Stallgasse mit Schaufel und Niederhalter auf, kippt vorn aus). Nächster Schritt: `prompts/fusion_umsetzung.md` lokal mit dem Fusion-MCP ausführen.

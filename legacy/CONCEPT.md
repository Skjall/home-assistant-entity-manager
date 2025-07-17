# Home Assistant Entitäten-Umbenennungsplan

## 📊 System-Übersicht
- **Gesamt-Entitäten:** 2.115
- **Domains:** 40
- **Home Assistant URL:** https://homeassistant.skjall.de
- **Backup erstellt:** ✅

## 🏠 Erkannte Räume & Normalisierung

### Aktuelle Raumnamen (inkonsistent)
- `wohnzimmer` ✅
- `buro` → `buero` (Normalisierung nötig)
- `eingang` ✅
- `kuche` → `kueche` (für Konsistenz)
- `balkon` ✅
- `kammer` ✅
- `dusche` ✅
- `badezimmer` ✅
- `diele` ✅
- `schlafzimmer` ✅
- `kinderzimmer` ✅

### Zusätzliche Bereiche
- `keller` (aus lock.keller erkannt)
- `aussen` (für Außenbereiche)
- `system` (für System-Entitäten)
- `netzwerk` (für Netzwerk-Equipment)

## 📝 Neue Namenskonvention

### Entity ID Format ⚡ KORRIGIERT
```
domain.raum_geraet_entitaet
```

### Struktur-Erklärung
- **Domain:** Automatisch (light, sensor, switch, etc.)
- **Raum:** Eindeutige Raumbezeichnung
- **Gerät:** Physisches Gerät (ohne Seriennummern)
- **Entität:** Was genau gemessen/gesteuert wird

### Beispiel eines Multi-Entitäts-Geräts
```
# Ein smarter Spot mit mehreren Sensoren:
light.wohnzimmer_deckenleuchte_sofa_spot_1_licht      # Das Licht selbst
sensor.wohnzimmer_deckenleuchte_sofa_spot_1_verbrauch # Stromverbrauch
sensor.wohnzimmer_deckenleuchte_sofa_spot_1_spannung  # Spannung
binary_sensor.wohnzimmer_deckenleuchte_sofa_spot_1_erreichbar # Online-Status
```

### Regeln
1. **Keine Umlaute:** ä→ae, ö→oe, ü→ue, ß→ss
2. **Kleinschreibung:** Nur lowercase + Unterstriche
3. **Konsistente Raumnamen:** Siehe Tabelle oben
4. **Aussagekräftige Gerätenamen:** Keine Seriennummern/MAC-Adressen
5. **Standardisierte Entitäts-Bezeichnungen:** Siehe Katalog unten
6. **Friendly Names:** Deutsche Bezeichnungen mit korrekter Rechtschreibung
7. **AI-Label:** Jede geprüfte Entität bekommt Label "ai_reviewed"

### Entitäts-Katalog (Standardisiert)

#### Beleuchtung
- `licht` - Das Licht selbst
- `helligkeit` - Helligkeitswert
- `farbe` - Farbwert/RGB
- `farbtemperatur` - Warmweiß/Kaltweiß
- `verbrauch` - Stromverbrauch (W)
- `spannung` - Spannung (V)
- `strom` - Stromstärke (A)
- `erreichbar` - Online-Status

#### Heizung/Klima
- `temperatur` - Aktuelle Temperatur
- `soll_temperatur` - Ziel-Temperatur
- `heizung` - Heizungs-Steuerung
- `kuehlung` - Kühlungs-Steuerung
- `luftfeuchtigkeit` - Relative Luftfeuchtigkeit
- `ventil` - Ventilstellung (%)
- `kindersicherung` - Kindersicherung an/aus

#### Steckdosen/Schalter
- `zustand` - Ein/Aus-Zustand
- `verbrauch` - Stromverbrauch
- `spannung` - Spannung
- `strom` - Stromstärke
- `energie` - Gesamtenergie (kWh)
- `ueberlast` - Überlastschutz

#### Sensoren
- `bewegung` - Bewegungsmelder
- `helligkeit` - Lichtsensor (lx)
- `temperatur` - Temperatursensor
- `luftfeuchtigkeit` - Feuchtigkeitssensor
- `co2` - CO2-Konzentration
- `druck` - Luftdruck
- `batterie` - Batteriestand (%)
- `signal` - Signalstärke

#### Multimedia
- `wiedergabe` - Play/Pause/Stop
- `lautstaerke` - Lautstärke (%)
- `quelle` - Input-Quelle
- `titel` - Aktueller Titel
- `kuenstler` - Aktueller Künstler

### Korrekte Beispiele
| Domain | Alt (Falsch) | Neu (Korrekt) | Friendly Name |
|--------|--------------|---------------|---------------|
| light | `wohnzimmer_deckenleuchte_sofa_spot_1_licht` | `wohnzimmer_deckenleuchte_sofa_spot_1_licht` | Wohnzimmer Deckenleuchte Sofa Spot 1 Licht |
| sensor | `buro_heizung_temperatur` | `buero_heizung_temperatur` | Büro Heizung Temperatur |
| switch | `eve_energy_20ebo8301` | `buero_steckdose_schreibtisch_zustand` | Büro Steckdose Schreibtisch |
| sensor | `eve_energy_20ebo8301_power` | `buero_steckdose_schreibtisch_verbrauch` | Büro Steckdose Schreibtisch Verbrauch |

## 🔍 Detaillierte Analyse nach Domains

### 💡 Lights (63 Entitäten) - PRIORITÄT 1

#### Wohnzimmer (10 Entitäten) ✅ Bereits korrekt strukturiert
```
AKTUELL                                           → AKTION
light.wohnzimmer_deckenleuchte_sofa_spot_1_licht → ✅ Korrekt (nur Label hinzufügen)
light.wohnzimmer_deckenleuchte_sofa_spot_2_licht → ✅ Korrekt (nur Label hinzufügen)
light.wohnzimmer_deckenleuchte_sofa_spot_3_licht → ✅ Korrekt (nur Label hinzufügen)
light.wohnzimmer_deckenleuchte_sofa_spot_4_licht → ✅ Korrekt (nur Label hinzufügen)
light.wohnzimmer_deckenleuchte_sofa_flache_licht → light.wohnzimmer_deckenleuchte_sofa_flaeche_licht
light.wohnzimmer_deckenspot_durchgang_1_licht    → ✅ Korrekt (nur Label hinzufügen)
light.wohnzimmer_deckenspot_durchgang_2_licht    → ✅ Korrekt (nur Label hinzufügen)
light.wohnzimmer_deckenspot_durchgang_3_licht    → ✅ Korrekt (nur Label hinzufügen)
light.wohnzimmer_deckenspot_durchgang_4_licht    → ✅ Korrekt (nur Label hinzufügen)
light.wohnzimmer_deckenspot_durchgang_5_licht    → ✅ Korrekt (nur Label hinzufügen)
```

#### Büro (6 Entitäten) - Raum-Normalisierung nötig
```
AKTUELL                          → NEU
light.buro_bucherregal_indirekt  → light.buero_buecherregal_indirekt_licht
light.buro_deckenleuchte_spot_1  → light.buero_deckenleuchte_spot_1_licht
light.buro_deckenleuchte_spot_2  → light.buero_deckenleuchte_spot_2_licht
light.buro_deckenleuchte         → light.buero_deckenleuchte_licht
light.buro_bucherregal_spots     → light.buero_buecherregal_spots_licht
light.buro_deckenleuchte_flache  → light.buero_deckenleuchte_flaeche_licht
```

#### Weitere Lichter (47 Entitäten)
- Eingang: 7 Entitäten (nur "_licht" entfernen)
- Küche: 4 Entitäten
- Badezimmer: 6 Entitäten
- Schlafzimmer: 7 Entitäten
- Dusche: 3 Entitäten
- Balkon, Kammer, Diele: je 1-2 Entitäten

### 🌡️ Sensors (1056 Entitäten) - PRIORITÄT 2

#### Kritische Umbenennungen
```
AKTUELL                                          → NEU
sensor.bslkon_powerstream_solar_leistung         → sensor.balkon_powerstream_leistung
sensor.plugs_it_gesamt                          → sensor.kammer_steckdosen_leistung_it
sensor.plugs_tv_gesamt                          → sensor.wohnzimmer_steckdosen_leistung_tv
sensor.plugs_haushalt_gesamt                    → sensor.steckdosen_leistung_haushalt
sensor.plugs_media_gesamt                       → sensor.steckdosen_leistung_media
sensor.plugs_restverbrauch_gesamt               → sensor.steckdosen_leistung_rest
```

#### Temperatursensoren (bereits gut)
```
sensor.wohnzimmer_bewegungsmelder_durchgang_temperatur ✅
sensor.wohnzimmer_bewegungsmelder_durchgang_helligkeit ✅
```

### 🔌 Switches (222 Entitäten) - PRIORITÄT 2

#### Steckdosen
```
AKTUELL                                        → NEU
switch.eve_energy_20ebo8301                    → switch.buero_steckdose_schreibtisch
switch.buro_schreibtisch_wiebke_steckdose_zustand → switch.buero_steckdose_wiebke
switch.kammer_it_steckdose_zustand             → switch.kammer_steckdose_it
```

#### Heizung Kindersicherungen (bereits gut benannt)
```
switch.buro_heizung_kindersicherung    → switch.buero_heizung_kindersicherung
switch.kuche_heizung_kindersicherung   → switch.kueche_heizung_kindersicherung
(Rest bereits korrekt)
```

### 🌡️ Climate (10 Entitäten) - PRIORITÄT 3
**Bereits sehr gut benannt!** Nur `buro` → `buero`, `kuche` → `kueche`

### 🤖 Automations (27 Entitäten) - PRIORITÄT 3
**Bereits sehr gut benannt!** Nur `buro` → `buero`, `kuche` → `kueche`

## 🎯 Prioritäten-Matrix

### Stufe 1: Kritisch (Sofort) - ~150 Entitäten
- **Büro-Entitäten:** `buro` → `buero` + fehlende `_licht` Endungen
- **Küche-Entitäten:** `kuche` → `kueche` für Konsistenz
- **Unklare Gerätenamen:** Eve Energy, Seriennummern ersetzen
- **Fehlende Entitäts-Bezeichner:** Schalter ohne `_zustand`

### Stufe 2: Wichtig (Diese Woche) - ~200 Entitäten
- **Sensoren:** Technische IDs vs logische Namen (PowerStream, etc.)
- **Umlaute normalisieren:** `flache` → `flaeche`, `bucherregal` → `buecherregal`
- **Multi-Entitäts-Geräte:** Vollständig strukturieren
- **Deaktivierte Entitäten:** Prüfen und ggf. aktivieren

### Stufe 3: Labels & Qualität (Parallel) - Alle Entitäten
- **AI-Labels vergeben:** `ai_reviewed` für jede geprüfte Entität
- **Geräte-Completion:** `ai_device_complete` wenn alle Entitäten fertig
- **Konsistenz-Checks:** Alle Entitäten eines Geräts gleiche Struktur

### Stufe 3: Optional (Später) - ~Rest
- **System-Entitäten:** Backup, Sun, Updates (meist OK)
- **Netzwerk:** UniFi, CloudKey (technisch korrekt)
- **Auto/BMW:** Bereits sehr gut strukturiert

## 🏷️ Label-System & Qualitätskontrolle

### Entitäts-Labels
- **`ai_reviewed`** - Entität wurde vom KI-System überprüft und normalisiert
- **`naming_compliant`** - Entspricht der neuen Namenskonvention
- **`legacy_name`** - Entität hat noch alte Benennung (Übergangsphase)
- **`device_complete`** - Alle Entitäten dieses Geräts sind normalisiert

### Geräte-Labels
- **`ai_device_complete`** - Alle Entitäten dieses Geräts wurden bearbeitet
- **`multi_entity_device`** - Gerät mit mehreren Entitäten
- **`single_entity_device`** - Gerät mit nur einer Entität

### Deaktivierte Entitäten
**Aktion:** Alle deaktivierten Entitäten prüfen und ggf. aktivieren
```python
# Script-Feature: Deaktivierte Entitäten finden und aktivieren
disabled_entities = [entity for entity in all_entities if entity.disabled_by == "user"]
```

## 🔍 Multi-Entitäts-Geräte Beispiele

### Smart Plug mit Sensoren
```
# Eve Energy Steckdose → Standardisiert:
switch.buero_steckdose_schreibtisch_zustand           # Ein/Aus
sensor.buero_steckdose_schreibtisch_verbrauch         # Leistung (W)
sensor.buero_steckdose_schreibtisch_energie           # Energie (kWh)
sensor.buero_steckdose_schreibtisch_spannung          # Spannung (V)
sensor.buero_steckdose_schreibtisch_strom             # Strom (A)
binary_sensor.buero_steckdose_schreibtisch_erreichbar # Online-Status
```

### Smart Light mit Sensoren
```
# Philips Hue mit integrierten Sensoren:
light.wohnzimmer_stehlampe_ecke_licht                 # Das Licht
sensor.wohnzimmer_stehlampe_ecke_verbrauch            # Stromverbrauch
sensor.wohnzimmer_stehlampe_ecke_bewegung             # Bewegungssensor
sensor.wohnzimmer_stehlampe_ecke_helligkeit           # Lichtsensor
sensor.wohnzimmer_stehlampe_ecke_temperatur           # Temperatursensor
binary_sensor.wohnzimmer_stehlampe_ecke_erreichbar    # Erreichbarkeit
```

### Heizungsthermostat
```
# Tado/Zigbee Thermostat:
climate.schlafzimmer_heizung                          # Hauptsteuerung
sensor.schlafzimmer_heizung_temperatur                # Ist-Temperatur
sensor.schlafzimmer_heizung_soll_temperatur           # Soll-Temperatur
sensor.schlafzimmer_heizung_ventil                    # Ventilstellung (%)
sensor.schlafzimmer_heizung_batterie                  # Batteriestand
switch.schlafzimmer_heizung_kindersicherung           # Kindersicherung
binary_sensor.schlafzimmer_heizung_erreichbar         # Online-Status
```

### Automationen mit Entity-Referenzen
```yaml
# Diese Automationen müssen nach Umbenennung angepasst werden:
automation.buro_deckenleuchte_schalten          → automation.buero_deckenleuchte_schalten
automation.buro_lichtsteuerung                  → automation.buero_lichtsteuerung
automation.kuche_lichtsteuerung                 → automation.kueche_lichtsteuerung
automation.kuche_heizungssteuerung              → automation.kueche_heizungssteuerung
```

### Szenen (46 Entitäten)
```yaml
scene.buro_normal  → scene.buero_normal
(Weitere Analyse erforderlich)
```

## 🛠️ Technische Umsetzung

### Python-Script-Anforderungen

```python
# Erforderliche Bibliotheken
import asyncio
import aiohttp
import json
import yaml
from typing import Dict, List, Tuple
import re
```

### Websocket API Endpunkte
```python
# Home Assistant Websocket API
WEBSOCKET_URL = "wss://homeassistant.skjall.de/api/websocket"
ACCESS_TOKEN = "YOUR_LONG_LIVED_TOKEN"

# Wichtige API Calls
entity_registry_list = {"type": "config/entity_registry/list"}
entity_registry_update = {
    "type": "config/entity_registry/update",
    "entity_id": "old_id",
    "new_entity_id": "new_id",
    "name": "New Friendly Name"
}
```

### Mapping-Struktur
```python
ROOM_MAPPING = {
    "buro": "buero",
    "kuche": "kueche",
    # Weitere Mappings
}

ENTITY_MAPPINGS = {
    # Format: "alte_entity_id": ("neue_entity_id", "Friendly Name")
    "light.buro_deckenleuchte": ("light.buero_deckenleuchte", "Büro Deckenleuchte"),
    "light.wohnzimmer_deckenleuchte_sofa_spot_1_licht": ("light.wohnzimmer_deckenleuchte_sofa_spot_1", "Wohnzimmer Deckenleuchte Sofa Spot 1"),
    # ... weitere Mappings
}
```

## 📋 Schritt-für-Schritt Plan

### Phase 1: Vorbereitung
1. **✅ Backup erstellt**
2. **✅ Analyse abgeschlossen**
3. **Nächste Schritte:**
   - Python-Script entwickeln
   - Test-Mapping für 5-10 Entitäten erstellen
   - Dependency-Scanner implementieren

### Phase 2: Test-Lauf
1. **Test-Entitäten auswählen:** 5 Büro-Lichter
2. **Script ausführen** (Dry-Run Modus)
3. **Abhängigkeiten prüfen**
4. **Echte Umbenennung** von Test-Entitäten
5. **Validierung** (Funktioniert alles?)

### Phase 3: Batch-Umbenennung
1. **Domain-weise Abarbeitung:**
   - Lichter (63)
   - Schalter (222)
   - Sensoren (1056)
   - Rest nach Bedarf
2. **Nach jeder Domain:** Automationen/Szenen updaten
3. **Validierung:** Alle Funktionen testen

### Phase 4: Finalisierung
1. **UI/Dashboard** aktualisieren
2. **Dokumentation** der neuen Struktur
3. **Backup** der finalen Konfiguration

## 🔧 Script-Features

### Must-Have
- **Websocket-Connection** zu Home Assistant
- **Batch-Umbenennung** mit Mapping-File basierend auf korrektem Schema
- **Label-Management:** AI-Labels für Entitäten und Geräte vergeben
- **Deaktivierte Entitäten:** Finden, prüfen und optional aktivieren
- **Multi-Entitäts-Geräte:** Gruppierte Bearbeitung (alle Entitäten eines Geräts)
- **Dependency-Detection** (Automationen/Szenen scannen)
- **Dry-Run Modus** (Preview ohne Änderungen)
- **Rollback-Funktionalität**
- **Progress-Tracking** mit Logging

### Nice-to-Have
- **Interactive Mode** (Bestätigung pro Entität/Gerät)
- **Entitäts-Katalog Validation** (prüft gegen Standardbezeichnungen)
- **Device-Grouping** (zeigt alle Entitäten eines Geräts)
- **Export/Import** von Mapping-Files
- **Statistics** (Erfolg/Fehler-Rate, Label-Coverage)
- **Backup-Integration**

### Script-API Erweiterungen
```python
# Neue API Calls für Labels
entity_registry_update_labels = {
    "type": "config/entity_registry/update",
    "entity_id": "sensor.example",
    "labels": ["ai_reviewed", "naming_compliant"]
}

# Deaktivierte Entitäten aktivieren
entity_registry_enable = {
    "type": "config/entity_registry/update",
    "entity_id": "sensor.example",
    "disabled_by": None  # Aktiviert die Entität
}

# Device-Registry für Geräte-Labels
device_registry_update = {
    "type": "config/device_registry/update",
    "device_id": "device_uuid",
    "labels": ["ai_device_complete", "multi_entity_device"]
}
```

## ⚠️ Risiken & Mitigationen

### Risiken
1. **Automationen brechen** nach Umbenennung
2. **UI/Dashboards** zeigen "unavailable"
3. **Historische Daten** gehen verloren
4. **Rollback** kompliziert

### Mitigationen
1. **Backup vor jedem Schritt**
2. **Dependency-Scanner** vor Umbenennung
3. **Test-Lauf** mit wenigen Entitäten
4. **Automatisches Update** von Automationen/Szenen
5. **Schritt-für-Schritt** statt Masse-Update

## 🚀 Ready for Claude Code

Diese Dokumentation ist bereit für die Übergabe an **Claude Code** zur Script-Entwicklung.

**Nächste Schritte:**
1. Python-Script für Websocket-API entwickeln
2. Mapping-Dateien generieren
3. Dependency-Scanner implementieren
4. Test-Framework aufbauen

**Alle benötigten Informationen sind dokumentiert!**
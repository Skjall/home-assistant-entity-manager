# Home Assistant Entity Manager - Web UI

Eine moderne Web-Oberfläche für das Home Assistant Entity Renaming Tool.

## Features

- **Raum-basierte Navigation**: Wähle zuerst einen Raum, dann die Domain
- **Dynamische Domain-Filter**: Zeigt nur Domains an, die im gewählten Raum Entities haben
- **Interaktive Vorschau**: 
  - Zeigt aktuelle und neue Entity IDs
  - Unterscheidet zwischen Umbenennungen und bereits korrekten Entities
  - Individuelle Auswahl möglich
- **Label-Management**: Option zum Überspringen von Entities mit "Maintained" Label
- **Dependencies-Anzeige**: Zeigt Abhängigkeiten für jede Entity (Automationen, Scripts, etc.)
- **Moderne UI**: 
  - Responsive Design mit Tailwind CSS
  - Alpine.js für reaktive Komponenten
  - Smooth Animations und Transitions

## Installation

```bash
# Dependencies installieren
pip install -r requirements.txt

# Web UI starten
python web_ui.py
```

## Verwendung

1. Öffne http://localhost:5001 im Browser
2. Wähle einen Raum aus der Dropdown-Liste
3. Wähle eine Domain (nur verfügbare Domains werden angezeigt)
4. Optional: Aktiviere "Überspringe mit Maintained Label"
5. Klicke auf "Vorschau" um die Änderungen zu sehen
6. Wähle die gewünschten Entities aus (Standard: alle ausgewählt)
7. Klicke auf "X Entities verarbeiten" um die Änderungen durchzuführen

## Technische Details

- **Backend**: Flask mit async Support
- **Frontend**: Vanilla JS mit Alpine.js für Reaktivität
- **Styling**: Tailwind CSS für modernes Design
- **Icons**: Remix Icons

## API Endpoints

- `GET /api/areas` - Alle Räume mit Entity-Anzahl
- `POST /api/preview` - Vorschau der Änderungen
- `POST /api/execute` - Führt ausgewählte Änderungen durch
- `GET /api/dependencies/<entity_id>` - Zeigt Dependencies einer Entity
- `GET /api/stats` - Allgemeine Statistiken

## Hinweise

- Die Web UI nutzt die gleiche Konfiguration (.env) wie das CLI Tool
- Änderungen werden sofort in Home Assistant durchgeführt
- Dependencies werden automatisch aktualisiert
- Das "Maintained" Label wird bei allen verarbeiteten Entities gesetzt
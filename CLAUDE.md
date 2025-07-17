# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Home Assistant Entity Manager - A Python tool for standardizing entity names in Home Assistant according to German naming conventions.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run main entity renaming tool
python rename_entities.py [--test] [--limit N] [--force] [--only-hue]

# Start web interface
python web_ui.py

# Run tests
python test_api.py
python test_websocket_registry.py
python test_scene_deps.py
```

## Architecture

### Core API Clients
- **ha_websocket.py**: WebSocket client for real-time Home Assistant communication
- **ha_client.py**: HTTP client for REST API operations

### Entity Management
- **entity_registry.py**: CRUD operations for entities
- **device_registry.py**: Device management operations
- **entity_restructurer.py**: Core renaming logic and naming convention implementation

### Dependency Management
- **dependency_scanner.py**: Finds entity references in automations/scenes
- **dependency_updater.py**: Updates references after entity renames

### Web Interface
- **web_ui.py**: Flask app providing visualization and management UI
- Templates in `templates/` using Tailwind CSS

## Key Concepts

1. **Naming Convention**: Entities follow pattern `{room}.{device_type}.{location/name}`
   - Example: `buero.licht.decke` (office ceiling light)
   - Room normalization: `buro` → `buero`, `bad` → `badezimmer`

2. **Safe Operations**: 
   - Always use `--test` flag first for dry runs
   - Dependency scanning ensures automations/scenes are updated
   - Label system tracks entity quality/status

3. **Configuration**:
   - `.env` file required with `HA_TOKEN` and `HA_URL`
   - `naming_overrides.json` for custom naming rules

## Important Notes

- The project uses asyncio for WebSocket operations but Flask (synchronous) for web UI
- Entity IDs in Home Assistant are immutable - renaming creates new entities with migration
- Always verify dependency updates before applying changes
- German documentation in README.md and CONCEPT.md contains detailed specifications
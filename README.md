# Home Assistant Entity Manager

A comprehensive tool for standardizing and managing entity names in Home Assistant according to a consistent naming convention.

## Features

- **Batch Entity Renaming**: Rename multiple entities according to a standardized pattern
- **German Naming Convention**: Follows the pattern `{room}.{device_type}.{location/name}`
- **Room Normalization**: Automatically normalizes room names (e.g., `buro` → `buero`)
- **Dependency Tracking**: Finds and updates entity references in automations and scenes
- **Label Management**: Track entity quality and processing status
- **Web Interface**: Visualize and manage entities through an intuitive UI
- **Safe Operations**: Dry-run mode and comprehensive validation before changes

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/home-assistant-entity-manager.git
cd home-assistant-entity-manager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Home Assistant credentials:
```env
HA_TOKEN=your_long_lived_access_token
HA_URL=http://your-home-assistant:8123
```

## Usage

### Command Line Interface

```bash
# Dry run - analyze entities without making changes
python rename_entities.py --test

# Limit to first 10 entities
python rename_entities.py --test --limit 10

# Process only Hue devices
python rename_entities.py --test --only-hue

# Execute renaming (be careful!)
python rename_entities.py --force

# Skip entities with 'maintained' label
python rename_entities.py --skip-reviewed

# Show only entities with 'maintained' label
python rename_entities.py --show-reviewed
```

### Web Interface

Start the web interface:
```bash
python web_ui.py
```

Then open http://localhost:5000 in your browser.

The web interface provides:
- Visual overview of all entities organized by area
- Entity renaming preview
- Label management
- Real-time status updates

## Naming Convention

Entities follow this pattern:
```
{room}.{device_type}.{location/name}
```

Examples:
- `buero.licht.decke` - Office ceiling light
- `wohnzimmer.sensor.temperatur` - Living room temperature sensor
- `kueche.schalter.steckdose_1` - Kitchen power outlet switch 1

## Configuration

### Naming Overrides

Create a `naming_overrides.json` file to customize naming:

```json
{
  "areas": {
    "area_id_here": {
      "name": "Custom Room Name"
    }
  },
  "devices": {
    "device_id_here": {
      "name": "Custom Device Name"
    }
  },
  "entities": {
    "entity_registry_id_here": {
      "name": "Custom Entity Name"
    }
  }
}
```

## Safety Features

1. **Dry Run Mode**: Always test with `--test` flag first
2. **Dependency Scanning**: Automatically finds and updates entity references
3. **Label System**: Track which entities have been processed
4. **Validation**: Comprehensive checks before applying changes
5. **WebSocket & REST API**: Reliable communication with Home Assistant

## Project Structure

```
├── rename_entities.py      # Main CLI tool
├── web_ui.py              # Flask web interface
├── entity_restructurer.py  # Core renaming logic
├── dependency_scanner.py   # Find entity references
├── dependency_updater.py   # Update references
├── ha_websocket.py        # WebSocket client
├── ha_client.py           # REST API client
├── entity_registry.py     # Entity management
├── device_registry.py     # Device management
├── label_registry.py      # Label operations
└── templates/             # Web UI templates
```

## Development

### Example Scripts

The `examples/` directory contains various test scripts and utilities:

```bash
cd examples/
python test_api.py              # Test API connectivity
python test_websocket_registry.py  # Test WebSocket connections
python check_dependencies.py    # Check entity dependencies
```

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for Home Assistant
- Uses the Home Assistant WebSocket and REST APIs
- Web interface built with Flask and Tailwind CSS
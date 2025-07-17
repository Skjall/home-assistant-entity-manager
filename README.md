# Home Assistant Entity Manager

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Skjall/home-assistant-entity-manager.svg?style=flat-square)](https://github.com/Skjall/home-assistant-entity-manager/releases)
[![License](https://img.shields.io/github/license/Skjall/home-assistant-entity-manager.svg?style=flat-square)](LICENSE)

A Home Assistant integration for standardizing and managing entity names according to a consistent naming convention. Available through HACS (Home Assistant Community Store).

## Features

- **Batch Entity Renaming**: Rename multiple entities according to a standardized pattern
- **German Naming Convention**: Follows the pattern `{room}.{device_type}.{location/name}`
- **Room Normalization**: Automatically normalizes room names (e.g., `buro` → `buero`)
- **Dependency Tracking**: Finds and updates entity references in automations and scenes
- **Label Management**: Track entity quality and processing status
- **Web Interface**: Visualize and manage entities through an intuitive UI
- **Safe Operations**: Dry-run mode and comprehensive validation before changes

## Installation

### Via HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Skjall&repository=home-assistant-entity-manager&category=integration)

#### Manual steps:
1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add this repository URL: `https://github.com/Skjall/home-assistant-entity-manager`
5. Select "Integration" as the category
6. Click "Add"
7. Search for "Entity Manager" and install it
8. Restart Home Assistant
9. Go to Settings → Devices & Services → Add Integration → Entity Manager

### Manual Installation

1. Copy the `custom_components/entity_manager` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration → Entity Manager

## Usage

### Using Services

After installation, the integration provides several services:

#### `entity_manager.analyze_entities`
Preview entity renaming without making changes.

```yaml
service: entity_manager.analyze_entities
data:
  limit: 10
  skip_reviewed: true
```

#### `entity_manager.rename_entity`
Rename a single entity.

```yaml
service: entity_manager.rename_entity
data:
  entity_id: light.kitchen_ceiling
```

#### `entity_manager.rename_bulk`
Rename multiple entities at once.

```yaml
service: entity_manager.rename_bulk
data:
  limit: 50
  skip_reviewed: true
  dry_run: false  # Set to true for preview only
```

### Using the Web Interface

After installation, the Entity Manager provides a web interface panel in Home Assistant:

1. Navigate to the sidebar in Home Assistant
2. Click on "Entity Manager" (admin access required)
3. Select an area from the dropdown
4. Optionally filter by domain (light, switch, sensor, etc.)
5. Preview entities that need renaming
6. Select entities to process
7. Click "Process X entities" to apply changes

The web interface features:
- **Area-based navigation**: Browse entities organized by room/area
- **Domain filtering**: Filter entities by type
- **Visual indicators**: See which entities need renaming
- **Batch operations**: Select and rename multiple entities at once
- **Skip maintained**: Option to hide entities already processed

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

## Troubleshooting

### Common Issues

#### Service not found
If you get "Service entity_manager.analyze_entities not found":
1. Check the integration is properly installed and loaded
2. Restart Home Assistant
3. Check logs for any errors during startup

#### Entity rename fails
If entity renaming fails:
1. Check the entity ID is valid
2. Ensure the entity is not locked or read-only
3. Check if the new entity ID already exists
4. Review logs for specific error messages

#### Missing entities in analysis
If entities are missing from analysis:
1. Check if they have the "maintained" label (use `show_reviewed: true`)
2. Increase the `limit` parameter
3. Verify entities are registered in Home Assistant

### Debug Logging

Enable debug logging for the integration:

```yaml
logger:
  default: info
  logs:
    custom_components.entity_manager: debug
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests with coverage
pytest tests/ -v --cov=custom_components.entity_manager

# Run specific test
pytest tests/test_services.py -v

# Run with coverage report
pytest tests/ --cov=custom_components.entity_manager --cov-report=html
```

### Code Quality

```bash
# Format code
black custom_components tests

# Sort imports
isort custom_components tests

# Type checking
mypy custom_components

# Linting
flake8 custom_components
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Ensure tests pass and coverage is maintained
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Guidelines

- All code must have type hints
- All functions must have docstrings
- Test coverage must be maintained above 80%
- Follow Home Assistant development guidelines
- Use semantic commit messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for Home Assistant
- Follows Home Assistant development standards
- Community contributions welcome
# Home Assistant Entity Manager Add-on (Alpha)

⚠️ **ALPHA VERSION - DEVELOPMENT USE ONLY** ⚠️

This is an early alpha version of the Entity Manager Add-on. It is NOT ready for production use and may cause issues with your Home Assistant installation.

## Installation

### Prerequisites
- Home Assistant OS or Home Assistant Supervised
- Advanced mode enabled in your user profile

### Add Repository

1. Navigate to Supervisor → Add-on Store
2. Click the three dots menu → Repositories
3. Add this repository: `https://github.com/Skjall/home-assistant-entity-manager`
4. Click "Add"

### Install Add-on

1. Find "Entity Manager (Alpha)" in the add-on store
2. Click on it and then click "Install"
3. **READ THE WARNINGS** - This is alpha software!

## Configuration

No configuration needed. The add-on will automatically connect to your Home Assistant instance.

## Usage

1. Start the add-on
2. Click "OPEN WEB UI" to access the Entity Manager interface
3. The UI will be integrated into your Home Assistant sidebar

## ⚠️ Important Warnings

- **BACKUP YOUR HOME ASSISTANT** before using this add-on
- This add-on can rename entities which may break automations
- Always use the preview feature before applying changes
- Test in a development environment first

## Features

- Batch entity renaming according to logical patterns
- Dependency tracking (finds entities used in automations/scenes)
- Preview changes before applying
- Integrated into Home Assistant UI via Ingress

## Known Issues

- Alpha version - expect bugs
- Large entity counts may cause performance issues
- Some entity types may not rename properly

## Support

This is alpha software provided as-is. Use at your own risk.

Report issues at: https://github.com/Skjall/home-assistant-entity-manager/issues
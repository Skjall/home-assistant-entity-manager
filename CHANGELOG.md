# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-17

### Added
- Initial release of Entity Manager for Home Assistant
- Service `entity_manager.analyze_entities` for previewing entity renaming
- Service `entity_manager.rename_entity` for renaming single entities
- Service `entity_manager.rename_bulk` for bulk entity renaming
- Support for German naming convention with proper normalization
- Area, device, and entity override support via `naming_overrides.json`
- Label system for tracking processed entities (`maintained` label)
- Comprehensive error handling and validation
- Full type hints and docstrings throughout codebase
- Unit tests with >80% coverage
- GitHub Actions for CI/CD
- HACS compatibility

### Technical Details
- Follows Home Assistant Bronze quality scale requirements
- Async service implementation
- Proper input validation using voluptuous schemas
- Comprehensive logging at appropriate levels
- Service responses for all operations

### Known Limitations
- Web UI panel not yet implemented (coming in future release)
- Limited to renaming entities (automations/scenes update coming soon)
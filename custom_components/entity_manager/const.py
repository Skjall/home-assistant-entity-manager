"""Constants for the Entity Manager integration."""

from typing import Final

DOMAIN: Final = "entity_manager"

# Configuration
CONF_SKIP_REVIEWED: Final = "skip_reviewed"
CONF_SHOW_REVIEWED: Final = "show_reviewed"
CONF_LIMIT: Final = "limit"
CONF_DRY_RUN: Final = "dry_run"

# Services
SERVICE_ANALYZE_ENTITIES: Final = "analyze_entities"
SERVICE_RENAME_ENTITY: Final = "rename_entity"
SERVICE_RENAME_BULK: Final = "rename_bulk"

# Labels
LABEL_MAINTAINED: Final = "maintained"
LABEL_ERROR: Final = "entity_manager_error"
LABEL_RENAMED: Final = "entity_manager_renamed"

# Defaults
DEFAULT_LIMIT: Final = 10
DEFAULT_DRY_RUN: Final = True

# Errors
ERROR_ENTITY_NOT_FOUND: Final = "entity_not_found"
ERROR_RENAME_FAILED: Final = "rename_failed"
ERROR_INVALID_CONFIG: Final = "invalid_config"

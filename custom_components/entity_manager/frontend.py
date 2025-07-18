"""Frontend for Entity Manager."""

from __future__ import annotations

import logging

from homeassistant.components import frontend
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Entity Manager frontend."""

    hass.http.register_static_path(
        f"/entity_manager_static",
        hass.config.path(f"custom_components/{DOMAIN}/panel"),
        cache_headers=False,
    )

    await frontend.async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title="Entity Manager",
        sidebar_icon="mdi:rename-box",
        frontend_url_path=DOMAIN,
        config={
            "_panel_custom": {
                "name": "entity-manager-panel",
                "embed_iframe": False,
                "trust_external": False,
            }
        },
        require_admin=True,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Entity Manager frontend."""
    frontend.async_remove_panel(hass, DOMAIN)
    return True

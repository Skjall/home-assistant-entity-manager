"""Config flow for Entity Manager integration."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, ERROR_INVALID_CONFIG

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional("name", default="Entity Manager"): str,
    }
)


class EntityManagerConfigError(HomeAssistantError):
    """Error to indicate we cannot configure the integration."""


async def validate_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the user input allows us to connect.

    Args:
        hass: The Home Assistant instance.
        data: User input data.

    Returns:
        Dictionary with configuration title.

    Raises:
        EntityManagerConfigError: If validation fails.
    """
    # Validate name is not empty
    name = data.get("name", "").strip()
    if not name:
        raise EntityManagerConfigError("Name cannot be empty")

    # Future validation can be added here
    # For example, checking if required services are available

    return {"title": name}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Entity Manager.

    This class manages the configuration flow for the Entity Manager integration,
    allowing users to set up the integration through the Home Assistant UI.
    """

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._errors: Dict[str, str] = {}
        self._user_input: Optional[Dict[str, Any]] = None

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step.

        This is the first step in the config flow where users provide
        basic configuration for the integration.

        Args:
            user_input: User input from the form.

        Returns:
            FlowResult with the next step or created entry.
        """
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                description_placeholders={
                    "docs_url": "https://github.com/jangrossheim/home-assistant-entity-manager"
                },
            )

        self._errors = {}
        self._user_input = user_input

        try:
            # Validate the input
            info = await validate_input(self.hass, user_input)

            # Check if already configured
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()

            # Create the config entry
            _LOGGER.info(
                "Creating Entity Manager config entry with title: %s", info["title"]
            )
            return self.async_create_entry(
                title=info["title"],
                data=user_input,
                description="Entity naming convention manager",
            )

        except EntityManagerConfigError as err:
            _LOGGER.error("Configuration validation error: %s", err)
            self._errors["base"] = ERROR_INVALID_CONFIG

        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception during configuration: %s", err)
            self._errors["base"] = "unknown"

        # Show form again with errors
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=self._errors,
            description_placeholders={
                "docs_url": "https://github.com/jangrossheim/home-assistant-entity-manager"
            },
        )

    async def async_step_import(self, import_data: Dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml.

        Args:
            import_data: Data imported from configuration.yaml.

        Returns:
            FlowResult with created entry or abort.
        """
        # Check if already configured
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        return await self.async_step_user(import_data)

"""Tests for Entity Manager config flow."""

from unittest.mock import patch

import pytest
from homeassistant import config_entries

from custom_components.entity_manager.const import DOMAIN


async def test_form(hass):
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}

    with patch(
        "custom_components.entity_manager.config_flow.validate_input",
        return_value={"title": "Entity Manager"},
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"name": "Entity Manager"},
        )
        await hass.async_block_till_done()

    assert result2["type"] == "create_entry"
    assert result2["title"] == "Entity Manager"
    assert result2["data"] == {"name": "Entity Manager"}


async def test_form_cannot_create_duplicate(hass):
    """Test we cannot create a duplicate config entry."""
    # Create an existing entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=DOMAIN,
        data={"name": "Entity Manager"},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.entity_manager.config_flow.validate_input",
        return_value={"title": "Entity Manager"},
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"name": "Entity Manager"},
        )

    assert result2["type"] == "abort"
    assert result2["reason"] == "already_configured"


class MockConfigEntry:
    """Mock config entry."""

    def __init__(self, domain, unique_id, data):
        """Initialize mock entry."""
        self.domain = domain
        self.unique_id = unique_id
        self.data = data
        self.entry_id = "mock_entry_id"

    def add_to_hass(self, hass):
        """Add entry to hass."""
        if not hasattr(hass.config_entries, "_entries"):
            hass.config_entries._entries = []
        hass.config_entries._entries.append(self)

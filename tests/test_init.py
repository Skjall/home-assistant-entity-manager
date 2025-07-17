"""Tests for Entity Manager initialization."""

from unittest.mock import call, patch

import pytest

from custom_components.entity_manager import async_setup_entry, async_unload_entry
from custom_components.entity_manager.const import DOMAIN


async def test_setup_entry(mock_hass, mock_config_entry):
    """Test setting up the integration."""
    mock_hass.data = {}

    # Mock the service registration
    with patch(
        "custom_components.entity_manager.async_setup_services"
    ) as mock_setup_services:
        result = await async_setup_entry(mock_hass, mock_config_entry)

    assert result is True
    assert DOMAIN in mock_hass.data
    assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]
    assert "naming_overrides" in mock_hass.data[DOMAIN][mock_config_entry.entry_id]
    mock_setup_services.assert_called_once_with(mock_hass)


async def test_unload_entry(mock_hass, mock_config_entry):
    """Test unloading the integration."""
    mock_hass.data = {DOMAIN: {mock_config_entry.entry_id: {"naming_overrides": {}}}}

    result = await async_unload_entry(mock_hass, mock_config_entry)

    assert result is True
    assert mock_config_entry.entry_id not in mock_hass.data[DOMAIN]


async def test_service_registration(mock_hass):
    """Test that services are registered correctly."""
    from custom_components.entity_manager import async_setup_services

    await async_setup_services(mock_hass)

    # Check that services were registered
    assert mock_hass.services.async_register.call_count == 2

    # Verify the service names
    calls = mock_hass.services.async_register.call_args_list
    assert calls[0][0][0] == DOMAIN
    assert calls[0][0][1] == "analyze_entities"
    assert calls[1][0][0] == DOMAIN
    assert calls[1][0][1] == "rename_entity"

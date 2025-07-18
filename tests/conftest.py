"""Global fixtures for Entity Manager tests."""

import os
from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

from homeassistant.core import HomeAssistant
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

# Add the custom_components directory to the path so tests can find it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# This is required for pytest-homeassistant-custom-component
pytest_plugins = "pytest_homeassistant_custom_component.common"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture
def mock_hass():
    """Return a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {}
    hass.services = MagicMock()
    hass.helpers = MagicMock()
    return hass


@pytest.fixture
def mock_config_entry():
    """Return a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {"name": "Entity Manager"}
    return entry


@pytest.fixture
def mock_entity_registry():
    """Return a mock entity registry."""
    registry = MagicMock()
    registry.entities = {
        "light.test_light": MagicMock(
            entity_id="light.test_light",
            id="abc123",
            original_name="Test Light",
            device_id="device123",
            area_id="area123",
            labels=set(),
        )
    }
    return registry


@pytest.fixture
def mock_device_registry():
    """Return a mock device registry."""
    registry = MagicMock()
    registry.devices = {
        "device123": MagicMock(
            id="device123",
            name="Test Device",
            name_by_user=None,
            model="Test Model",
            area_id="area123",
        )
    }
    return registry


@pytest.fixture
def mock_area_registry():
    """Return a mock area registry."""
    registry = MagicMock()
    registry.areas = {"area123": MagicMock(id="area123", name="Test Room")}
    return registry

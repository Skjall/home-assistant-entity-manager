"""Global fixtures for Entity Manager tests."""
import pytest
from unittest.mock import patch, MagicMock
from homeassistant.core import HomeAssistant


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
            labels=set()
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
            area_id="area123"
        )
    }
    return registry


@pytest.fixture
def mock_area_registry():
    """Return a mock area registry."""
    registry = MagicMock()
    registry.areas = {
        "area123": MagicMock(
            id="area123",
            name="Test Room"
        )
    }
    return registry
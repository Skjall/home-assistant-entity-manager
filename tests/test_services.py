"""Tests for Entity Manager services."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from custom_components.entity_manager import async_setup_services
from custom_components.entity_manager.const import (
    DOMAIN,
    SERVICE_ANALYZE_ENTITIES,
    SERVICE_RENAME_ENTITY,
    SERVICE_RENAME_BULK,
    LABEL_MAINTAINED,
)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {DOMAIN: {"test_entry": {"naming_overrides": MagicMock()}}}
    hass.services = MagicMock()
    hass.helpers = MagicMock()
    return hass


@pytest.fixture
def mock_registries(mock_hass):
    """Create mock registries."""
    # Mock entity registry
    entity_reg = MagicMock()
    entity_reg.entities = {
        "light.test_light": MagicMock(
            entity_id="light.test_light",
            id="entity1",
            device_id="device1",
            area_id="area1",
            labels=set(),
            original_name="Test Light"
        ),
        "light.maintained_light": MagicMock(
            entity_id="light.maintained_light",
            id="entity2",
            device_id="device2",
            area_id="area1",
            labels={LABEL_MAINTAINED},
            original_name="Maintained Light"
        )
    }
    entity_reg.async_get = lambda eid: entity_reg.entities.get(eid)
    entity_reg.async_update_entity = MagicMock()
    
    # Mock device registry
    device_reg = MagicMock()
    device_reg.devices = {
        "device1": MagicMock(
            id="device1",
            name="Test Device",
            name_by_user=None,
            model="Test Model",
            area_id="area1"
        ),
        "device2": MagicMock(
            id="device2",
            name="Maintained Device",
            name_by_user="User Device",
            model="Test Model",
            area_id="area1"
        )
    }
    
    # Mock area registry
    area_reg = MagicMock()
    area_reg.areas = {
        "area1": MagicMock(id="area1", name="Living Room")
    }
    
    return entity_reg, device_reg, area_reg


@pytest.mark.asyncio
async def test_analyze_entities_service(mock_hass, mock_registries):
    """Test analyze entities service."""
    entity_reg, device_reg, area_reg = mock_registries
    
    with patch("custom_components.entity_manager.er.async_get", return_value=entity_reg), \
         patch("custom_components.entity_manager.dr.async_get", return_value=device_reg), \
         patch("custom_components.entity_manager.ar.async_get", return_value=area_reg):
        
        await async_setup_services(mock_hass)
        
        # Get the registered service
        service_call = mock_hass.services.async_register.call_args_list[0]
        assert service_call[0][1] == SERVICE_ANALYZE_ENTITIES
        analyze_service = service_call[0][2]
        
        # Test basic analysis
        call = MagicMock()
        call.data = {"limit": 10, "skip_reviewed": False}
        
        result = await analyze_service(call)
        
        assert "entities" in result
        assert "total_analyzed" in result
        assert result["total_analyzed"] == 2
        
        # Test with skip_reviewed
        call.data = {"limit": 10, "skip_reviewed": True}
        result = await analyze_service(call)
        
        # Should only analyze non-maintained entity
        assert result["total_analyzed"] == 1
        assert result["entities"][0]["current_id"] == "light.test_light"


@pytest.mark.asyncio
async def test_rename_entity_service(mock_hass, mock_registries):
    """Test rename entity service."""
    entity_reg, device_reg, area_reg = mock_registries
    
    with patch("custom_components.entity_manager.er.async_get", return_value=entity_reg), \
         patch("custom_components.entity_manager.dr.async_get", return_value=device_reg), \
         patch("custom_components.entity_manager.ar.async_get", return_value=area_reg):
        
        await async_setup_services(mock_hass)
        
        # Get the registered service
        service_call = mock_hass.services.async_register.call_args_list[1]
        assert service_call[0][1] == SERVICE_RENAME_ENTITY
        rename_service = service_call[0][2]
        
        # Test successful rename
        call = MagicMock()
        call.data = {"entity_id": "light.test_light"}
        
        result = await rename_service(call)
        
        assert result["success"] is True
        assert result["old_id"] == "light.test_light"
        assert "new_id" in result
        assert "friendly_name" in result
        
        # Verify update was called
        assert entity_reg.async_update_entity.called
        
        # Test entity not found
        call.data = {"entity_id": "light.nonexistent"}
        
        with pytest.raises(ServiceValidationError) as exc_info:
            await rename_service(call)
        
        assert "not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_rename_bulk_service(mock_hass, mock_registries):
    """Test bulk rename service."""
    entity_reg, device_reg, area_reg = mock_registries
    
    with patch("custom_components.entity_manager.er.async_get", return_value=entity_reg), \
         patch("custom_components.entity_manager.dr.async_get", return_value=device_reg), \
         patch("custom_components.entity_manager.ar.async_get", return_value=area_reg):
        
        await async_setup_services(mock_hass)
        
        # Get the registered service
        service_call = mock_hass.services.async_register.call_args_list[2]
        assert service_call[0][1] == SERVICE_RENAME_BULK
        bulk_service = service_call[0][2]
        
        # Test dry run
        call = MagicMock()
        call.data = {"limit": 10, "skip_reviewed": True, "dry_run": True}
        
        result = await bulk_service(call)
        
        assert result["dry_run"] is True
        assert "processed" in result
        assert "skipped" in result
        assert "errors" in result
        
        # Should not actually rename in dry run
        assert not entity_reg.async_update_entity.called
        
        # Test actual rename
        call.data = {"entity_ids": ["light.test_light"], "dry_run": False}
        entity_reg.async_update_entity.reset_mock()
        
        result = await bulk_service(call)
        
        assert result["dry_run"] is False
        assert len(result["processed"]) > 0
        
        # Should have called update
        assert entity_reg.async_update_entity.called


@pytest.mark.asyncio
async def test_service_error_handling(mock_hass, mock_registries):
    """Test service error handling."""
    entity_reg, device_reg, area_reg = mock_registries
    
    # Make entity registry throw an error
    entity_reg.async_update_entity.side_effect = Exception("Test error")
    
    with patch("custom_components.entity_manager.er.async_get", return_value=entity_reg), \
         patch("custom_components.entity_manager.dr.async_get", return_value=device_reg), \
         patch("custom_components.entity_manager.ar.async_get", return_value=area_reg):
        
        await async_setup_services(mock_hass)
        
        # Get rename service
        service_call = mock_hass.services.async_register.call_args_list[1]
        rename_service = service_call[0][2]
        
        # Test error during rename
        call = MagicMock()
        call.data = {"entity_id": "light.test_light"}
        
        with pytest.raises(HomeAssistantError) as exc_info:
            await rename_service(call)
        
        assert "Failed to rename entity" in str(exc_info.value)


@pytest.mark.asyncio
async def test_analyze_entities_validation(mock_hass, mock_registries):
    """Test analyze entities parameter validation."""
    entity_reg, device_reg, area_reg = mock_registries
    
    with patch("custom_components.entity_manager.er.async_get", return_value=entity_reg), \
         patch("custom_components.entity_manager.dr.async_get", return_value=device_reg), \
         patch("custom_components.entity_manager.ar.async_get", return_value=area_reg):
        
        await async_setup_services(mock_hass)
        
        # Get the service
        service_call = mock_hass.services.async_register.call_args_list[0]
        analyze_service = service_call[0][2]
        
        # Test conflicting parameters
        call = MagicMock()
        call.data = {"skip_reviewed": True, "show_reviewed": True}
        
        with pytest.raises(ServiceValidationError) as exc_info:
            await analyze_service(call)
        
        assert "Cannot use both" in str(exc_info.value)
"""Tests for entity restructurer."""
import pytest
from unittest.mock import MagicMock, patch
from custom_components.entity_manager.entity_restructurer import EntityRestructurer
from custom_components.entity_manager.naming_overrides import NamingOverrides


class TestEntityRestructurer:
    """Test EntityRestructurer class."""
    
    @pytest.fixture
    def naming_overrides(self):
        """Create naming overrides fixture."""
        return NamingOverrides()
    
    @pytest.fixture
    def restructurer(self, naming_overrides):
        """Create restructurer fixture."""
        return EntityRestructurer(None, naming_overrides)
    
    def test_normalize_name(self, restructurer):
        """Test name normalization."""
        # Test German umlauts
        assert restructurer.normalize_name("Büro") == "buero"
        assert restructurer.normalize_name("Küche") == "kueche"
        assert restructurer.normalize_name("Großes Zimmer") == "grosses_zimmer"
        
        # Test special characters
        assert restructurer.normalize_name("Living Room") == "living_room"
        assert restructurer.normalize_name("Test-Name") == "test_name"
        assert restructurer.normalize_name("Test  Multiple  Spaces") == "test_multiple_spaces"
        
        # Test edge cases
        assert restructurer.normalize_name("") == ""
        assert restructurer.normalize_name(None) == ""
        assert restructurer.normalize_name("   ") == ""
        assert restructurer.normalize_name("_test_") == "test"
    
    def test_get_entity_type(self, restructurer):
        """Test entity type detection."""
        # Test direct domain mapping
        assert restructurer.get_entity_type("light.test", None) == "licht"
        assert restructurer.get_entity_type("switch.test", None) == "schalter"
        assert restructurer.get_entity_type("climate.test", None) == "heizung"
        
        # Test sensor with device class
        assert restructurer.get_entity_type("sensor.test", "temperature") == "temperatur"
        assert restructurer.get_entity_type("sensor.test", "humidity") == "luftfeuchtigkeit"
        assert restructurer.get_entity_type("sensor.test", "unknown") == "sensor"
        
        # Test binary sensor
        assert restructurer.get_entity_type("binary_sensor.test", "motion") == "bewegung"
        assert restructurer.get_entity_type("binary_sensor.test", "door") == "tuer"
        
        # Test fallback
        assert restructurer.get_entity_type("unknown.test", None) == "sensor"
        
        # Test invalid entity ID
        assert restructurer.get_entity_type("invalid", None) == "sensor"
        assert restructurer.get_entity_type("", None) == "sensor"
    
    def test_generate_new_entity_id_simple(self, restructurer):
        """Test simple entity ID generation."""
        # Setup test data
        restructurer.areas = {
            "area1": {"area_id": "area1", "name": "Living Room"}
        }
        restructurer.devices = {
            "device1": {
                "id": "device1",
                "name": "Ceiling Light",
                "name_by_user": None,
                "model": "Hue Bulb",
                "area_id": "area1"
            }
        }
        restructurer.entities = {
            "light.ceiling": {
                "entity_id": "light.ceiling",
                "id": "entity1",
                "device_id": "device1",
                "area_id": None,
                "labels": set()
            }
        }
        
        # Generate new ID
        new_id, friendly_name = restructurer.generate_new_entity_id(
            "light.ceiling", {"attributes": {}}
        )
        
        assert new_id == "light.living_room_ceiling_light_licht"
        assert "Living Room" in friendly_name
        assert "Ceiling Light" in friendly_name
    
    def test_generate_new_entity_id_with_area_override(self, restructurer):
        """Test entity ID generation with area override."""
        # Setup naming overrides
        restructurer.naming_overrides._overrides = {
            "areas": {
                "area1": {"name": "Büro"}
            }
        }
        
        restructurer.areas = {
            "area1": {"area_id": "area1", "name": "Office"}
        }
        restructurer.devices = {
            "device1": {
                "id": "device1",
                "name": "Desktop Light",
                "name_by_user": None,
                "model": "LED Strip",
                "area_id": "area1"
            }
        }
        restructurer.entities = {
            "light.desktop": {
                "entity_id": "light.desktop",
                "id": "entity1",
                "device_id": "device1",
                "area_id": None,
                "labels": set()
            }
        }
        
        # Generate new ID
        new_id, friendly_name = restructurer.generate_new_entity_id(
            "light.desktop", {"attributes": {}}
        )
        
        assert new_id == "light.buero_desktop_light_licht"
        assert "Büro" in friendly_name
    
    def test_generate_new_entity_id_no_device(self, restructurer):
        """Test entity ID generation without device."""
        restructurer.areas = {
            "area1": {"area_id": "area1", "name": "Kitchen"}
        }
        restructurer.entities = {
            "light.kitchen_light": {
                "entity_id": "light.kitchen_light",
                "id": "entity1",
                "device_id": None,
                "area_id": "area1",
                "labels": set()
            }
        }
        
        # Generate new ID
        new_id, friendly_name = restructurer.generate_new_entity_id(
            "light.kitchen_light", {"attributes": {}}
        )
        
        # Should extract device name from entity ID
        assert "kitchen" in new_id
        assert "licht" in new_id
    
    def test_generate_new_entity_id_invalid_input(self, restructurer):
        """Test entity ID generation with invalid input."""
        # Test with empty entity ID
        new_id, friendly_name = restructurer.generate_new_entity_id("", {})
        assert new_id == ""
        assert friendly_name == ""
        
        # Test with None
        new_id, friendly_name = restructurer.generate_new_entity_id(None, {})
        assert new_id == ""
        assert friendly_name == ""
        
        # Test with malformed entity ID
        new_id, friendly_name = restructurer.generate_new_entity_id("invalid", {})
        assert new_id == "invalid"
        assert friendly_name == "invalid"
    
    @pytest.mark.asyncio
    async def test_load_structure_with_websocket(self, restructurer):
        """Test loading structure with websocket."""
        mock_ws = MagicMock()
        mock_ws._send_message = MagicMock(return_value=1)
        mock_ws._receive_message = MagicMock(side_effect=[
            {"id": 1, "success": True, "result": [
                {"area_id": "area1", "name": "Living Room"}
            ]},
            {"id": 2, "success": True, "result": [
                {"id": "device1", "name": "Test Device", "area_id": "area1"}
            ]},
            {"id": 3, "success": True, "result": [
                {"entity_id": "light.test", "id": "entity1", "labels": ["maintained"]}
            ]}
        ])
        
        await restructurer.load_structure(mock_ws)
        
        assert len(restructurer.areas) == 1
        assert "area1" in restructurer.areas
        assert len(restructurer.devices) == 1
        assert "device1" in restructurer.devices
        assert len(restructurer.entities) == 1
        assert "light.test" in restructurer.entities
    
    @pytest.mark.asyncio
    async def test_load_structure_without_websocket(self, restructurer):
        """Test loading structure without websocket."""
        await restructurer.load_structure(None)
        
        # Should initialize empty structures
        assert restructurer.areas == {}
        assert restructurer.devices == {}
        assert restructurer.entities == {}
    
    @pytest.mark.asyncio
    async def test_analyze_entities(self, restructurer):
        """Test analyzing entities."""
        # Setup test data
        restructurer.areas = {"area1": {"area_id": "area1", "name": "Living Room"}}
        restructurer.devices = {}
        restructurer.entities = {
            "light.test1": {"entity_id": "light.test1", "labels": set()},
            "light.test2": {"entity_id": "light.test2", "labels": {"maintained"}}
        }
        
        states = [
            {"entity_id": "light.test1", "attributes": {}},
            {"entity_id": "light.test2", "attributes": {}}
        ]
        
        # Test without skipping reviewed
        mapping = await restructurer.analyze_entities(states, skip_reviewed=False)
        assert len(mapping) == 2
        
        # Test with skipping reviewed
        mapping = await restructurer.analyze_entities(states, skip_reviewed=True)
        assert len(mapping) == 1
        assert "light.test1" in mapping
        
        # Test showing only reviewed
        mapping = await restructurer.analyze_entities(states, show_reviewed=True)
        assert len(mapping) == 1
        assert "light.test2" in mapping
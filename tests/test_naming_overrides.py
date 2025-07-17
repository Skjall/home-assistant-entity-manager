"""Tests for naming overrides."""
import pytest
import json
import tempfile
from pathlib import Path
from custom_components.entity_manager.naming_overrides import NamingOverrides


class TestNamingOverrides:
    """Test NamingOverrides class."""
    
    def test_init_empty(self):
        """Test initialization with no file."""
        overrides = NamingOverrides()
        assert overrides._overrides == {"areas": {}, "devices": {}, "entities": {}}
    
    def test_init_with_file(self, tmp_path):
        """Test initialization with override file."""
        # Create test override file
        override_data = {
            "areas": {"area1": {"name": "Custom Area"}},
            "devices": {"device1": {"name": "Custom Device"}},
            "entities": {"entity1": {"name": "Custom Entity"}}
        }
        
        override_file = tmp_path / "overrides.json"
        override_file.write_text(json.dumps(override_data))
        
        overrides = NamingOverrides(str(override_file))
        assert overrides._overrides == override_data
    
    def test_init_with_invalid_file(self, tmp_path):
        """Test initialization with invalid JSON file."""
        # Create invalid JSON file
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("invalid json content")
        
        # Should not raise, but log error
        overrides = NamingOverrides(str(invalid_file))
        assert overrides._overrides == {"areas": {}, "devices": {}, "entities": {}}
    
    def test_init_with_nonexistent_file(self):
        """Test initialization with nonexistent file."""
        overrides = NamingOverrides("/nonexistent/path/file.json")
        assert overrides._overrides == {"areas": {}, "devices": {}, "entities": {}}
    
    def test_get_area_override(self):
        """Test getting area override."""
        overrides = NamingOverrides()
        overrides._overrides = {
            "areas": {"area1": {"name": "Custom Area"}}
        }
        
        assert overrides.get_area_override("area1") == {"name": "Custom Area"}
        assert overrides.get_area_override("area2") is None
        assert overrides.get_area_override(None) is None
        assert overrides.get_area_override("") is None
    
    def test_get_device_override(self):
        """Test getting device override."""
        overrides = NamingOverrides()
        overrides._overrides = {
            "devices": {"device1": {"name": "Custom Device"}}
        }
        
        assert overrides.get_device_override("device1") == {"name": "Custom Device"}
        assert overrides.get_device_override("device2") is None
        assert overrides.get_device_override(None) is None
        assert overrides.get_device_override("") is None
    
    def test_get_entity_override(self):
        """Test getting entity override."""
        overrides = NamingOverrides()
        overrides._overrides = {
            "entities": {"entity1": {"name": "Custom Entity"}}
        }
        
        assert overrides.get_entity_override("entity1") == {"name": "Custom Entity"}
        assert overrides.get_entity_override("entity2") is None
        assert overrides.get_entity_override(None) is None
        assert overrides.get_entity_override("") is None
    
    def test_load_overrides_valid(self, tmp_path):
        """Test loading valid overrides."""
        overrides = NamingOverrides()
        
        # Create valid override file
        override_data = {
            "areas": {"area1": {"name": "Test Area"}},
            "devices": {},
            "entities": {}
        }
        
        override_file = tmp_path / "valid.json"
        override_file.write_text(json.dumps(override_data))
        
        # Load overrides
        result = overrides._load_overrides(str(override_file))
        assert result == override_data
    
    def test_load_overrides_missing_sections(self, tmp_path):
        """Test loading overrides with missing sections."""
        overrides = NamingOverrides()
        
        # Create override file with missing sections
        override_data = {"areas": {"area1": {"name": "Test Area"}}}
        
        override_file = tmp_path / "partial.json"
        override_file.write_text(json.dumps(override_data))
        
        # Load overrides - should add missing sections
        result = overrides._load_overrides(str(override_file))
        assert "areas" in result
        assert "devices" in result
        assert "entities" in result
        assert result["areas"]["area1"]["name"] == "Test Area"
        assert result["devices"] == {}
        assert result["entities"] == {}
    
    def test_get_override_edge_cases(self):
        """Test edge cases for get override methods."""
        overrides = NamingOverrides()
        
        # Test with empty overrides
        assert overrides.get_area_override("any") is None
        assert overrides.get_device_override("any") is None
        assert overrides.get_entity_override("any") is None
        
        # Test with missing sections
        overrides._overrides = {}
        assert overrides.get_area_override("any") is None
        assert overrides.get_device_override("any") is None
        assert overrides.get_entity_override("any") is None
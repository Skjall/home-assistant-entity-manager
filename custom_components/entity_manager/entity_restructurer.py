#!/usr/bin/env python3
"""
Home Assistant Entity Restructurer

Creates completely new Entity IDs based on the actual structure:
- Room (Area)
- Device
- Entity (what it is)
"""
import logging
import re
from typing import Dict, List, Tuple, Optional, Any

from .naming_overrides import NamingOverrides

logger = logging.getLogger(__name__)


class EntityRestructurer:
    """Handles the restructuring of Home Assistant entity IDs based on area, device, and entity type."""
    
    def __init__(self, client: Optional[Any] = None, naming_overrides: Optional[NamingOverrides] = None) -> None:
        """
        Initialize the EntityRestructurer.
        
        Args:
            client: Optional client for Home Assistant connection (not used in HA integration).
            naming_overrides: Optional NamingOverrides instance for custom naming rules.
        """
        self.client = client  # Not used in HA integration
        self.devices: Dict[str, Dict[str, Any]] = {}
        self.areas: Dict[str, Dict[str, Any]] = {}
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.naming_overrides = naming_overrides or NamingOverrides()
        
        # Standard entity type mappings
        self.entity_types: Dict[str, Any] = {
            "light": "licht",
            "switch": "schalter",
            "sensor": {
                "temperature": "temperatur",
                "humidity": "luftfeuchtigkeit", 
                "power": "leistung",
                "energy": "energie",
                "battery": "batterie",
                "illuminance": "helligkeit",
                "motion": "bewegung",
                "co2": "co2",
                "pressure": "druck",
                "voltage": "spannung",
                "current": "strom"
            },
            "binary_sensor": {
                "motion": "bewegung",
                "door": "tuer",
                "window": "fenster",
                "smoke": "rauch",
                "moisture": "feuchtigkeit",
                "connectivity": "verbindung"
            },
            "climate": "heizung",
            "cover": "rollo",
            "media_player": "player"
        }
        
    def normalize_name(self, name: str) -> str:
        """
        Normalize names for entity IDs according to Home Assistant standards.
        
        Args:
            name: The name to normalize.
            
        Returns:
            Normalized name suitable for entity IDs.
        """
        if not name:
            return ""
        
        try:
            # Replace German umlauts according to HA standard
            replacements = {
                "ä": "a", "ö": "o", "ü": "u", "ß": "ss",
                "Ä": "a", "Ö": "o", "Ü": "u"
            }
            
            normalized = name.lower()
            for old, new in replacements.items():
                normalized = normalized.replace(old, new)
                
            # Only alphanumeric and underscores allowed
            normalized = re.sub(r'[^a-z0-9]+', '_', normalized)
            normalized = re.sub(r'_+', '_', normalized)
            normalized = normalized.strip('_')
            
            return normalized
        except Exception as e:
            logger.error(f"Error normalizing name '{name}': {e}")
            return ""
        
    async def load_structure(self, ws_client: Optional[Any] = None) -> None:
        """
        Load the complete structure from Home Assistant via WebSocket.
        
        Args:
            ws_client: Optional WebSocket client for communication with Home Assistant.
        """
        if not ws_client:
            logger.warning("No WebSocket client available, using limited mode")
            self.areas = {}
            self.devices = {}
            self.entities = {}
            return
        
        # Load Areas via WebSocket
        try:
            logger.info("Loading areas via WebSocket...")
            msg_id = await ws_client._send_message({"type": "config/area_registry/list"})
            response = await ws_client._receive_message()
            while response.get("id") != msg_id:
                response = await ws_client._receive_message()
                
            if response.get("success"):
                areas_data = response.get("result", [])
                self.areas = {area["area_id"]: area for area in areas_data}
                logger.info(f"Successfully loaded {len(self.areas)} areas via WebSocket")
            else:
                logger.error(f"Failed to load areas: {response}")
                self.areas = {}
                
        except Exception as e:
            logger.error(f"Error loading areas via WebSocket: {e}")
            self.areas = {}
        
        # Load Devices via WebSocket
        try:
            logger.info("Loading devices via WebSocket...")
            msg_id = await ws_client._send_message({"type": "config/device_registry/list"})
            response = await ws_client._receive_message()
            while response.get("id") != msg_id:
                response = await ws_client._receive_message()
                
            if response.get("success"):
                devices_data = response.get("result", [])
                self.devices = {device["id"]: device for device in devices_data}
                logger.info(f"Successfully loaded {len(self.devices)} devices via WebSocket")
            else:
                logger.error(f"Failed to load devices: {response}")
                self.devices = {}
                
        except Exception as e:
            logger.error(f"Error loading devices via WebSocket: {e}")
            self.devices = {}
        
        # Load Entity Registry
        try:
            logger.info("Loading entity registry...")
            
            msg_id = await ws_client._send_message({
                "type": "config/entity_registry/list"
            })
            
            response = await ws_client._receive_message()
            while response.get("id") != msg_id:
                response = await ws_client._receive_message()
            
            if response.get("success"):
                entities = response.get("result", [])
                self.entities = {e["entity_id"]: e for e in entities}
                logger.info(f"Successfully loaded {len(self.entities)} entities from registry")
                
                # Count entities with maintained label
                maintained_count = sum(1 for e in self.entities.values() if "maintained" in e.get("labels", []))
                if maintained_count > 0:
                    logger.info(f"Found {maintained_count} entities with maintained label")
            else:
                logger.error(f"Failed to load entity registry: {response}")
                self.entities = {}
                
        except Exception as e:
            logger.error(f"Failed to load entity registry: {e}")
            self.entities = {}
                
    def get_entity_type(self, entity_id: str, device_class: Optional[str] = None) -> str:
        """
        Determine the entity type based on domain and device class.
        
        Args:
            entity_id: The entity ID to analyze.
            device_class: Optional device class for more specific type determination.
            
        Returns:
            The entity type as a string.
        """
        if not entity_id:
            logger.warning("Empty entity_id provided to get_entity_type")
            return "sensor"
        
        try:
            parts = entity_id.split(".")
            if len(parts) < 2:
                logger.warning(f"Invalid entity_id format: {entity_id}")
                return "sensor"
                
            domain = parts[0]
            
            if domain in ["light", "switch", "climate", "cover", "media_player"]:
                return self.entity_types.get(domain, domain)
                
            if domain in ["sensor", "binary_sensor"] and device_class:
                type_map = self.entity_types.get(domain, {})
                if isinstance(type_map, dict):
                    return type_map.get(device_class, device_class)
                    
            # Fallback: Try to guess from entity name
            entity_name = parts[-1].lower()
            domain_types = self.entity_types.get(domain, {})
            if isinstance(domain_types, dict):
                for key, value in domain_types.items():
                    if key in entity_name:
                        return value
                        
            return "sensor"  # Default
        except Exception as e:
            logger.error(f"Error determining entity type for '{entity_id}': {e}")
            return "sensor"
        
    def generate_new_entity_id(self, entity_id: str, state_info: Dict[str, Any]) -> Tuple[str, str]:
        """
        Generate new entity ID based on area, device name, and entity type.
        
        Args:
            entity_id: The original entity ID.
            state_info: State information dictionary containing attributes.
            
        Returns:
            Tuple of (new_entity_id, friendly_name).
        """
        if not entity_id:
            logger.warning("Empty entity_id provided to generate_new_entity_id")
            return "", ""
        
        try:
            parts = entity_id.split(".")
            if len(parts) < 2:
                logger.warning(f"Invalid entity_id format: {entity_id}")
                return entity_id, entity_id
                
            domain = parts[0]
            
            # Get entity registry info
            entity_reg = self.entities.get(entity_id, {})
            device_id = entity_reg.get("device_id")
            
            # Determine room/area
            room = None
            room_display = None  # For friendly name with area override
            device = None
            
            if device_id and device_id in self.devices:
                device_info = self.devices[device_id]
                device = device_info
                
                # Get room from device
                if device_info.get("area_id"):
                    area_id = device_info["area_id"]
                    area = self.areas.get(area_id)
                    if area:
                        # Check for area override
                        area_override = self.naming_overrides.get_area_override(area_id)
                        if area_override:
                            room = self.normalize_name(area_override["name"])
                            room_display = area_override["name"]
                        else:
                            room = self.normalize_name(area.get("name", ""))
                            room_display = area.get("name", "")
                        
            # If no room from device, try directly from entity
            if not room and entity_reg.get("area_id"):
                area_id = entity_reg["area_id"]
                area = self.areas.get(area_id)
                if area:
                    # Check for area override
                    area_override = self.naming_overrides.get_area_override(area_id)
                    if area_override:
                        room = self.normalize_name(area_override["name"])
                        room_display = area_override["name"]
                    else:
                        room = self.normalize_name(area.get("name", ""))
                        room_display = area.get("name", "")
                    
            # If still no room, try to extract from entity ID
            if not room:
                # Known rooms in HA convention
                known_rooms = ["wohnzimmer", "buro", "kuche", "schlafzimmer", "badezimmer", 
                              "kinderzimmer", "eingang", "diele", "balkon", "kammer", "dusche", "keller"]
                entity_parts = parts[-1].split("_")
                for part in entity_parts:
                    if part in known_rooms:
                        room = part
                        break
                        
            # Determine device name
            device_name = ""
            if device:
                # Check for device override
                device_override = self.naming_overrides.get_device_override(device_id) if device_id else None
                if device_override:
                    device_name = self.normalize_name(device_override["name"])
                else:
                    # Use device name or model
                    device_name = device.get("name_by_user") or device.get("name") or device.get("model", "")
                    device_name = self.normalize_name(device_name)
            else:
                # No device found - try to extract from entity name
                entity_parts = parts[-1].split("_")
                # Remove known room names and entity types
                known_rooms = ["wohnzimmer", "buro", "kuche", "schlafzimmer", "badezimmer", 
                              "kinderzimmer", "eingang", "diele", "balkon", "kammer", "dusche", "keller"]
                filtered_parts = []
                for part in entity_parts:
                    if part not in known_rooms and part not in ["licht", "sensor", "schalter"]:
                        filtered_parts.append(part)
                if filtered_parts:
                    device_name = "_".join(filtered_parts)
                
            # Determine entity type
            device_class = state_info.get("attributes", {}).get("device_class")
            entity_type = self.get_entity_type(entity_id, device_class)
            
            # Check for entity override
            registry_id = entity_reg.get("id", "")  # The immutable UUID
            entity_override = self.naming_overrides.get_entity_override(registry_id) if registry_id else None
            
            # If override exists, use it as basis for entity type
            if entity_override and entity_override.get("name"):
                # Override is the "nice" name (e.g. "Ceiling Light")
                # Normalize for entity ID
                entity_type = self.normalize_name(entity_override["name"])
            
            # Build new entity ID
            parts = []
            
            # Check if device_name already starts with room
            if room and device_name:
                # Normalize both for comparison
                room_normalized = room.lower()
                device_name_normalized = device_name.lower()
                
                # If device_name does NOT start with room, add room
                if not device_name_normalized.startswith(room_normalized):
                    parts.append(room)
                parts.append(device_name)
            elif room:
                parts.append(room)
            elif device_name:
                parts.append(device_name)
                
            parts.append(entity_type)
            
            new_entity_id = f"{domain}.{'_'.join(parts)}"
            
            # Build friendly name
            friendly_parts = []
            
            # Get device name for friendly name
            device_friendly_name = None
            if device:
                device_override = self.naming_overrides.get_device_override(device_id) if device_id else None
                if device_override:
                    device_friendly_name = device_override["name"]
                else:
                    device_friendly_name = device.get("name_by_user") or device.get("name")
            
            # Check if device name already starts with room
            if room and device_friendly_name:
                # Use room_display if available (with area override), otherwise format room
                if not room_display:
                    room_display = room.replace("u", "ü").replace("o", "ö").replace("a", "ä").title()
                
                # If device name doesn't start with room, add room
                if not device_friendly_name.lower().startswith(room_display.lower()):
                    friendly_parts.append(room_display)
                friendly_parts.append(device_friendly_name)
            elif room:
                # Use room_display if available (with area override), otherwise format room
                if not room_display:
                    room_display = room.replace("u", "ü").replace("o", "ö").replace("a", "ä")
                friendly_parts.append(room_display.title())
            elif device_friendly_name:
                friendly_parts.append(device_friendly_name)
                
            # Entity type for friendly name
            if entity_override and entity_override.get("name"):
                # Use the override directly (already "nice")
                friendly_entity_type = entity_override["name"]
            else:
                # Convert generated type to nice name
                friendly_entity_type = entity_type.replace("_", " ").title()
                
            friendly_parts.append(friendly_entity_type)
            
            friendly_name = " ".join(friendly_parts)
            
            logger.debug(f"Generated new entity ID: {entity_id} -> {new_entity_id} ({friendly_name})")
            
            return new_entity_id, friendly_name
            
        except Exception as e:
            logger.error(f"Error generating new entity ID for '{entity_id}': {e}")
            return entity_id, entity_id
    
    def calculate_new_entity_name(self, entity_id: str, force_recalculate: bool = False) -> Tuple[str, str]:
        """
        Calculate new entity name based on current device/area data.
        
        Args:
            entity_id: The entity ID to process.
            force_recalculate: Whether to force recalculation (not used).
            
        Returns:
            Tuple of (new_entity_id, new_friendly_name).
        """
        if not entity_id:
            logger.warning("Empty entity_id provided to calculate_new_entity_name")
            return "", ""
        
        try:
            # Get entity from registry
            entity = self.entities.get(entity_id, {})
            if not entity:
                logger.warning(f"Entity '{entity_id}' not found in registry")
                return entity_id, entity_id  # Fallback if entity not found
                
            # Calculate new name with current data
            new_id, friendly_name = self.generate_new_entity_id(entity_id, entity)
            
            return new_id, friendly_name
        except Exception as e:
            logger.error(f"Error calculating new entity name for '{entity_id}': {e}")
            return entity_id, entity_id
        
    async def analyze_entities(self, states: List[Dict[str, Any]], skip_reviewed: bool = False, show_reviewed: bool = False) -> Dict[str, Tuple[str, str]]:
        """
        Analyze all entities and create a mapping of old to new entity IDs.
        
        Args:
            states: List of state dictionaries containing entity information.
            skip_reviewed: Whether to skip entities with the 'maintained' label.
            show_reviewed: Whether to show only entities with the 'maintained' label.
            
        Returns:
            Dictionary mapping original entity IDs to tuples of (new_entity_id, friendly_name).
        """
        if not states:
            logger.warning("No states provided to analyze_entities")
            return {}
        
        try:
            mapping = {}
            skipped_count = 0
            processed_count = 0
            
            logger.info(f"Analyzing {len(states)} entities...")
            
            for state in states:
                if not isinstance(state, dict):
                    logger.warning(f"Invalid state object: {state}")
                    continue
                    
                entity_id = state.get("entity_id")
                if not entity_id:
                    logger.warning("State object missing entity_id")
                    continue
                
                # Check if entity has already been processed
                entity_reg = self.entities.get(entity_id, {})
                has_maintained_label = "maintained" in entity_reg.get("labels", [])
                
                # Filter based on options
                if skip_reviewed and has_maintained_label:
                    skipped_count += 1
                    logger.debug(f"Skipping maintained entity: {entity_id}")
                    continue
                elif show_reviewed and not has_maintained_label:
                    logger.debug(f"Skipping non-maintained entity: {entity_id}")
                    continue
                    
                new_entity_id, friendly_name = self.generate_new_entity_id(entity_id, state)
                
                # Always add to mapping, even if nothing changes
                # The maintained label decides whether it's skipped
                mapping[entity_id] = (new_entity_id, friendly_name)
                processed_count += 1
                logger.info(f"Would process: {entity_id} -> {new_entity_id}")
                    
            if skipped_count > 0:
                logger.info(f"Skipped {skipped_count} entities with maintained label")
            
            logger.info(f"Analysis complete. Processed {processed_count} entities")
                    
            return mapping
            
        except Exception as e:
            logger.error(f"Error analyzing entities: {e}")
            return {}
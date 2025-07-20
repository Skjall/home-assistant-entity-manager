#!/usr/bin/env python3
"""
Home Assistant Entity Restructurer
Creates completely new entity IDs based on the actual structure:
- Area
- Device
- Entity (what it is)
"""
import logging
from typing import Dict, List, Optional, Tuple

from ha_client import HomeAssistantClient
from naming_overrides import NamingOverrides

logger = logging.getLogger(__name__)


class EntityRestructurer:
    def __init__(
        self,
        client: HomeAssistantClient,
        naming_overrides: Optional[NamingOverrides] = None,
    ):
        self.client = client
        self.devices = {}
        self.areas = {}
        self.entities = {}
        self.naming_overrides = naming_overrides or NamingOverrides()

        # Entity type mappings - using English technical terms
        # These are now only used as fallbacks since the frontend handles suggestions
        self.entity_types = {
            "light": "light",
            "switch": "switch",
            "sensor": {
                "temperature": "temperature",
                "humidity": "humidity",
                "power": "power",
                "energy": "energy",
                "battery": "battery",
                "illuminance": "illuminance",
                "motion": "motion",
                "co2": "co2",
                "pressure": "pressure",
                "voltage": "voltage",
                "current": "current",
            },
            "binary_sensor": {
                "motion": "motion",
                "door": "door",
                "window": "window",
                "smoke": "smoke",
                "moisture": "moisture",
                "connectivity": "connectivity",
            },
            "climate": "climate",
            "cover": "cover",
            "media_player": "media_player",
        }

    def normalize_name(self, name: str) -> str:
        """Normalize names for entity IDs (HA standard)"""
        if not name:
            return ""

        # Replace umlauts according to HA standard
        replacements = {
            "ä": "a",
            "ö": "o",
            "ü": "u",
            "ß": "ss",
            "Ä": "a",
            "Ö": "o",
            "Ü": "u",
        }

        normalized = name.lower()
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)

        # Only alphanumeric and underscores
        import re

        normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
        normalized = re.sub(r"_+", "_", normalized)
        normalized = normalized.strip("_")

        return normalized

    async def load_structure(self, ws_client=None):
        """Load the complete structure from Home Assistant via WebSocket"""
        # If no WebSocket client was provided, use REST API fallback
        if not ws_client:
            logger.warning("No WebSocket client available, using limited mode")
            self.areas = {}
            self.devices = {}
            self.entities = {}
            return

        try:
            # Load areas via WebSocket
            logger.info("Loading areas via WebSocket...")
            msg_id = await ws_client._send_message({"type": "config/area_registry/list"})
            response = await ws_client._receive_message()
            while response.get("id") != msg_id:
                response = await ws_client._receive_message()

            if response.get("success"):
                areas_data = response.get("result", [])
                self.areas = {area["area_id"]: area for area in areas_data}
                logger.info(f"Loaded {len(self.areas)} areas via WebSocket")
            else:
                logger.error(f"Failed to load areas: {response}")

        except Exception as e:
            logger.error(f"Error loading areas via WebSocket: {e}")

        try:
            # Load devices via WebSocket
            logger.info("Loading devices via WebSocket...")
            msg_id = await ws_client._send_message({"type": "config/device_registry/list"})
            response = await ws_client._receive_message()
            while response.get("id") != msg_id:
                response = await ws_client._receive_message()

            if response.get("success"):
                devices_data = response.get("result", [])
                self.devices = {device["id"]: device for device in devices_data}
                logger.info(f"Loaded {len(self.devices)} devices via WebSocket")
            else:
                logger.error(f"Failed to load devices: {response}")

        except Exception as e:
            logger.error(f"Error loading devices via WebSocket: {e}")

        # Load entity registry directly
        try:
            logger.info("Loading entity registry...")

            msg_id = await ws_client._send_message({"type": "config/entity_registry/list"})

            response = await ws_client._receive_message()
            while response.get("id") != msg_id:
                response = await ws_client._receive_message()

            if response.get("success"):
                entities = response.get("result", [])
                self.entities = {e["entity_id"]: e for e in entities}
                logger.info(f"Loaded {len(self.entities)} entities from registry")

                # Count maintained labels
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
        """Determine entity type based on domain and device class"""
        domain = entity_id.split(".")[0]

        if domain in ["light", "switch", "climate", "cover", "media_player"]:
            return self.entity_types.get(domain, domain)

        if domain in ["sensor", "binary_sensor"] and device_class:
            type_map = self.entity_types.get(domain, {})
            if isinstance(type_map, dict):
                return type_map.get(device_class, device_class)

        # Fallback: Try to guess from entity name
        entity_name = entity_id.split(".")[-1].lower()
        for key, value in self.entity_types.get(domain, {}).items():
            if key in entity_name:
                return value

        return "sensor"  # Default

    def generate_new_entity_id(self, entity_id: str, state_info: Dict) -> Tuple[str, str]:
        """
        Generiere neue Entity ID basierend auf:
        1. Area of the device or entity
        2. Device Name
        3. Entity Type
        """
        domain = entity_id.split(".")[0]

        # Hole Entity Registry Info
        entity_reg = self.entities.get(entity_id, {})
        device_id = entity_reg.get("device_id")

        # Determine area
        room = None
        room_display = None  # For friendly name with area override
        device = None

        if device_id and device_id in self.devices:
            device_info = self.devices[device_id]
            device = device_info

            # Area from device
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

        # If no area from device, try directly from entity
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

        # If still no area, leave it empty
        # (We don't try to guess from entity ID as that's unreliable and language-specific)

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
            # No device found - use entity name parts as fallback
            entity_parts = entity_id.split(".")[-1].split("_")
            # Use all parts as we don't want to make language-specific assumptions
            if entity_parts:
                device_name = "_".join(entity_parts)

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

        # Baue neue Entity ID
        parts = []

        # Check if device_name already starts with room
        if room and device_name:
            # Normalize both for comparison
            room_normalized = room.lower()
            device_name_normalized = device_name.lower()

            # If device_name does NOT start with area, add area
            if not device_name_normalized.startswith(room_normalized):
                parts.append(room)
            parts.append(device_name)
        elif room:
            parts.append(room)
        elif device_name:
            parts.append(device_name)

        parts.append(entity_type)

        new_entity_id = f"{domain}.{'_'.join(parts)}"

        # Friendly Name
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
            # Use room_display if available (with area override), otherwise use room
            if not room_display:
                room_display = room.title()

            # If device name doesn't start with area, add area
            if not device_friendly_name.lower().startswith(room_display.lower()):
                friendly_parts.append(room_display)
            friendly_parts.append(device_friendly_name)
        elif room:
            # Use room_display if available (with area override), otherwise use room
            if not room_display:
                room_display = room
            friendly_parts.append(room_display.title())
        elif device_friendly_name:
            friendly_parts.append(device_friendly_name)

        # Entity type for friendly name
        if entity_override and entity_override.get("name"):
            # Use the override directly (already formatted nicely)
            friendly_entity_type = entity_override["name"]
        else:
            # Convert generated type to nice name
            friendly_entity_type = entity_type.replace("_", " ").title()

        friendly_parts.append(friendly_entity_type)

        friendly_name = " ".join(friendly_parts)

        return new_entity_id, friendly_name

    def calculate_new_entity_name(self, entity_id: str, force_recalculate: bool = False) -> Tuple[str, str]:
        """
        Berechne neuen Entity Namen basierend auf aktuellen Device/Area Daten

        Returns:
            Tuple[new_entity_id, new_friendly_name]
        """
        # Hole Entity aus Registry
        entity = self.entities.get(entity_id, {})
        if not entity:
            return entity_id, entity_id  # Fallback wenn Entity nicht gefunden

        # Calculate new name with current data
        new_id, friendly_name = self.generate_new_entity_id(entity_id, entity)

        return new_id, friendly_name

    async def analyze_entities(
        self,
        states: List[Dict],
        skip_reviewed: bool = False,
        show_reviewed: bool = False,
    ) -> Dict[str, Tuple[str, str]]:
        """Analyze all entities and create mapping"""
        # Structure should already be loaded - don't load again!

        mapping = {}
        skipped_count = 0

        for state in states:
            entity_id = state["entity_id"]

            # Check if entity has already been processed
            entity_reg = self.entities.get(entity_id, {})
            has_maintained_label = "maintained" in entity_reg.get("labels", [])

            # Filter basierend auf Optionen
            if skip_reviewed and has_maintained_label:
                skipped_count += 1
                continue
            elif show_reviewed and not has_maintained_label:
                continue

            new_entity_id, friendly_name = self.generate_new_entity_id(entity_id, state)

            # ALWAYS include in mapping, even if nothing changes
            # The maintained label decides whether it's skipped
            mapping[entity_id] = (new_entity_id, friendly_name)
            logger.info(f"Would process: {entity_id} -> {new_entity_id}")

        if skipped_count > 0:
            logger.info(f"Skipped {skipped_count} entities with maintained label")

        return mapping

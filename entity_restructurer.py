#!/usr/bin/env python3
"""
Home Assistant Entity Restructurer
Erstellt komplett neue Entity IDs basierend auf der tatsächlichen Struktur:
- Raum (Area)
- Gerät (Device)
- Entität (Was es ist)
"""
import logging
from typing import Dict, List, Tuple, Optional
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

        # Standard Entity-Bezeichnungen
        self.entity_types = {
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
                "current": "strom",
            },
            "binary_sensor": {
                "motion": "bewegung",
                "door": "tuer",
                "window": "fenster",
                "smoke": "rauch",
                "moisture": "feuchtigkeit",
                "connectivity": "verbindung",
            },
            "climate": "heizung",
            "cover": "rollo",
            "media_player": "player",
        }

    def normalize_name(self, name: str) -> str:
        """Normalisiere Namen für Entity IDs (HA-Standard)"""
        if not name:
            return ""

        # Umlaute nach HA-Standard
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

        # Nur alphanumerisch und Unterstriche
        import re

        normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
        normalized = re.sub(r"_+", "_", normalized)
        normalized = normalized.strip("_")

        return normalized

    async def load_structure(self, ws_client=None):
        """Lade die komplette Struktur von Home Assistant über WebSocket"""
        # Wenn kein WebSocket Client übergeben wurde, verwende REST API Fallback
        if not ws_client:
            logger.warning(
                "Kein WebSocket Client verfügbar, nutze eingeschränkten Modus"
            )
            self.areas = {}
            self.devices = {}
            self.entities = {}
            return

        try:
            # Lade Areas über WebSocket
            logger.info("Loading areas via WebSocket...")
            msg_id = await ws_client._send_message(
                {"type": "config/area_registry/list"}
            )
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
            # Lade Devices über WebSocket
            logger.info("Loading devices via WebSocket...")
            msg_id = await ws_client._send_message(
                {"type": "config/device_registry/list"}
            )
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

        # Lade Entity Registry direkt
        try:
            logger.info("Loading entity registry...")

            msg_id = await ws_client._send_message(
                {"type": "config/entity_registry/list"}
            )

            response = await ws_client._receive_message()
            while response.get("id") != msg_id:
                response = await ws_client._receive_message()

            if response.get("success"):
                entities = response.get("result", [])
                self.entities = {e["entity_id"]: e for e in entities}
                logger.info(f"Loaded {len(self.entities)} entities from registry")

                # Zähle maintained Labels
                maintained_count = sum(
                    1
                    for e in self.entities.values()
                    if "maintained" in e.get("labels", [])
                )
                if maintained_count > 0:
                    logger.info(
                        f"Found {maintained_count} entities with maintained label"
                    )
            else:
                logger.error(f"Failed to load entity registry: {response}")
                self.entities = {}

        except Exception as e:
            logger.error(f"Failed to load entity registry: {e}")
            self.entities = {}

    def get_entity_type(
        self, entity_id: str, device_class: Optional[str] = None
    ) -> str:
        """Bestimme den Entity-Typ basierend auf Domain und Device Class"""
        domain = entity_id.split(".")[0]

        if domain in ["light", "switch", "climate", "cover", "media_player"]:
            return self.entity_types.get(domain, domain)

        if domain in ["sensor", "binary_sensor"] and device_class:
            type_map = self.entity_types.get(domain, {})
            if isinstance(type_map, dict):
                return type_map.get(device_class, device_class)

        # Fallback: Versuche aus dem Entity Namen zu raten
        entity_name = entity_id.split(".")[-1].lower()
        for key, value in self.entity_types.get(domain, {}).items():
            if key in entity_name:
                return value

        return "sensor"  # Default

    def generate_new_entity_id(
        self, entity_id: str, state_info: Dict
    ) -> Tuple[str, str]:
        """
        Generiere neue Entity ID basierend auf:
        1. Area/Raum des Geräts oder der Entity
        2. Device Name
        3. Entity Type
        """
        domain = entity_id.split(".")[0]

        # Hole Entity Registry Info
        entity_reg = self.entities.get(entity_id, {})
        device_id = entity_reg.get("device_id")

        # Bestimme Raum
        room = None
        room_display = None  # Für Friendly Name mit Area Override
        device = None

        if device_id and device_id in self.devices:
            device_info = self.devices[device_id]
            device = device_info

            # Raum vom Device
            if device_info.get("area_id"):
                area_id = device_info["area_id"]
                area = self.areas.get(area_id)
                if area:
                    # Prüfe auf Area Override
                    area_override = self.naming_overrides.get_area_override(area_id)
                    if area_override:
                        room = self.normalize_name(area_override["name"])
                        room_display = area_override["name"]
                    else:
                        room = self.normalize_name(area.get("name", ""))
                        room_display = area.get("name", "")

        # Falls kein Raum vom Device, versuche direkt von Entity
        if not room and entity_reg.get("area_id"):
            area_id = entity_reg["area_id"]
            area = self.areas.get(area_id)
            if area:
                # Prüfe auf Area Override
                area_override = self.naming_overrides.get_area_override(area_id)
                if area_override:
                    room = self.normalize_name(area_override["name"])
                    room_display = area_override["name"]
                else:
                    room = self.normalize_name(area.get("name", ""))
                    room_display = area.get("name", "")

        # Falls immer noch kein Raum, versuche aus Entity ID zu extrahieren
        if not room:
            # Known rooms in HA convention
            known_rooms = [
                "wohnzimmer",
                "buro",
                "kuche",
                "schlafzimmer",
                "badezimmer",
                "kinderzimmer",
                "eingang",
                "diele",
                "balkon",
                "kammer",
                "dusche",
                "keller",
            ]
            entity_parts = entity_id.split(".")[-1].split("_")
            for part in entity_parts:
                if part in known_rooms:
                    room = part
                    break

        # Bestimme Gerätenamen
        device_name = ""
        if device:
            # Prüfe auf Device Override
            device_override = (
                self.naming_overrides.get_device_override(device_id)
                if device_id
                else None
            )
            if device_override:
                device_name = self.normalize_name(device_override["name"])
            else:
                # Verwende den Device Namen oder Modell
                device_name = (
                    device.get("name_by_user")
                    or device.get("name")
                    or device.get("model", "")
                )
                device_name = self.normalize_name(device_name)
        else:
            # Kein Device gefunden - versuche aus Entity Name zu extrahieren
            entity_parts = entity_id.split(".")[-1].split("_")
            # Entferne bekannte Raumnamen und Entity-Typen
            known_rooms = [
                "wohnzimmer",
                "buro",
                "kuche",
                "schlafzimmer",
                "badezimmer",
                "kinderzimmer",
                "eingang",
                "diele",
                "balkon",
                "kammer",
                "dusche",
                "keller",
            ]
            filtered_parts = []
            for part in entity_parts:
                if part not in known_rooms and part not in [
                    "licht",
                    "sensor",
                    "schalter",
                ]:
                    filtered_parts.append(part)
            if filtered_parts:
                device_name = "_".join(filtered_parts)

        # Bestimme Entity-Typ
        device_class = state_info.get("attributes", {}).get("device_class")
        entity_type = self.get_entity_type(entity_id, device_class)

        # Prüfe auf Entity Override
        registry_id = entity_reg.get("id", "")  # Die unveränderliche UUID
        entity_override = (
            self.naming_overrides.get_entity_override(registry_id)
            if registry_id
            else None
        )

        # Wenn Override vorhanden, verwende ihn als Basis für Entity Type
        if entity_override and entity_override.get("name"):
            # Override ist der "schöne" Name (z.B. "Deckenlampe")
            # Normalisiere für Entity ID
            entity_type = self.normalize_name(entity_override["name"])

        # Baue neue Entity ID
        parts = []

        # Prüfe ob device_name bereits mit dem Raum beginnt
        if room and device_name:
            # Normalisiere beide für Vergleich
            room_normalized = room.lower()
            device_name_normalized = device_name.lower()

            # Wenn device_name NICHT mit dem Raum beginnt, füge Raum hinzu
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

        # Hole Device Name für Friendly Name
        device_friendly_name = None
        if device:
            device_override = (
                self.naming_overrides.get_device_override(device_id)
                if device_id
                else None
            )
            if device_override:
                device_friendly_name = device_override["name"]
            else:
                device_friendly_name = device.get("name_by_user") or device.get("name")

        # Prüfe ob Device Name bereits mit Raum beginnt
        if room and device_friendly_name:
            # Verwende room_display wenn vorhanden (mit Area Override), sonst formatiere room
            if not room_display:
                room_display = (
                    room.replace("u", "ü").replace("o", "ö").replace("a", "ä").title()
                )

            # Wenn Device Name nicht mit Raum beginnt, füge Raum hinzu
            if not device_friendly_name.lower().startswith(room_display.lower()):
                friendly_parts.append(room_display)
            friendly_parts.append(device_friendly_name)
        elif room:
            # Verwende room_display wenn vorhanden (mit Area Override), sonst formatiere room
            if not room_display:
                room_display = (
                    room.replace("u", "ü").replace("o", "ö").replace("a", "ä")
                )
            friendly_parts.append(room_display.title())
        elif device_friendly_name:
            friendly_parts.append(device_friendly_name)

        # Entity Type für Friendly Name
        if entity_override and entity_override.get("name"):
            # Verwende den Override direkt (ist bereits "schön")
            friendly_entity_type = entity_override["name"]
        else:
            # Konvertiere generierten Typ zu schönem Namen
            friendly_entity_type = entity_type.replace("_", " ").title()

        friendly_parts.append(friendly_entity_type)

        friendly_name = " ".join(friendly_parts)

        return new_entity_id, friendly_name

    def calculate_new_entity_name(
        self, entity_id: str, force_recalculate: bool = False
    ) -> Tuple[str, str]:
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
        """Analysiere alle Entities und erstelle Mapping"""
        # Struktur sollte bereits geladen sein - nicht nochmal laden!

        mapping = {}
        skipped_count = 0

        for state in states:
            entity_id = state["entity_id"]

            # Prüfe ob Entity bereits bearbeitet wurde
            entity_reg = self.entities.get(entity_id, {})
            has_maintained_label = "maintained" in entity_reg.get("labels", [])

            # Filter basierend auf Optionen
            if skip_reviewed and has_maintained_label:
                skipped_count += 1
                continue
            elif show_reviewed and not has_maintained_label:
                continue

            new_entity_id, friendly_name = self.generate_new_entity_id(entity_id, state)

            # IMMER ins Mapping aufnehmen, auch wenn sich nichts ändert
            # Das maintained Label entscheidet, ob es übersprungen wird
            mapping[entity_id] = (new_entity_id, friendly_name)
            logger.info(f"Would process: {entity_id} -> {new_entity_id}")

        if skipped_count > 0:
            logger.info(f"Skipped {skipped_count} entities with maintained label")

        return mapping

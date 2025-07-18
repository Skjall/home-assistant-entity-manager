import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from ha_websocket import HomeAssistantWebSocket
from label_registry import LabelRegistry

logger = logging.getLogger(__name__)


class EntityRegistry:
    def __init__(self, websocket: HomeAssistantWebSocket):
        self.ws = websocket
        self.entities: Dict[str, Dict] = {}
        self.label_registry = LabelRegistry(websocket)

    async def list_entities(self) -> List[Dict[str, Any]]:
        msg_id = await self.ws._send_message({"type": "config/entity_registry/list"})

        response = await self.ws._receive_message()
        while response.get("id") != msg_id:
            response = await self.ws._receive_message()

        if not response.get("success"):
            raise Exception(f"Failed to list entities: {response}")

        self.entities = {e["entity_id"]: e for e in response.get("result", [])}
        return response.get("result", [])

    async def update_entity(
        self,
        entity_id: str,
        new_entity_id: Optional[str] = None,
        name: Optional[str] = None,
        labels: Optional[List[str]] = None,
        disabled_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        message = {"type": "config/entity_registry/update", "entity_id": entity_id}

        if new_entity_id:
            message["new_entity_id"] = new_entity_id
        if name:
            message["name"] = name
        if labels is not None:
            message["labels"] = labels
        if disabled_by is not None:
            message["disabled_by"] = disabled_by

        msg_id = await self.ws._send_message(message)

        response = await self.ws._receive_message()
        while response.get("id") != msg_id:
            response = await self.ws._receive_message()

        if not response.get("success"):
            raise Exception(f"Failed to update entity {entity_id}: {response}")

        return response.get("result", {})

    async def rename_entity(
        self,
        old_entity_id: str,
        new_entity_id: str,
        friendly_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.update_entity(
            entity_id=old_entity_id, new_entity_id=new_entity_id, name=friendly_name
        )

    async def add_labels(self, entity_id: str, labels: List[str]) -> Dict[str, Any]:
        # Stelle sicher, dass alle Labels existieren
        for label in labels:
            if label and label.strip():
                await self.label_registry.ensure_label_exists(label)

        # Hole aktuelle Entity-Informationen direkt von Home Assistant
        try:
            msg_id = await self.ws._send_message(
                {"type": "config/entity_registry/get", "entity_id": entity_id}
            )

            response = await self.ws._receive_message()
            while response.get("id") != msg_id:
                response = await self.ws._receive_message()

            if response.get("success"):
                entity = response.get("result", {})
                existing_labels = entity.get("labels", [])
                # Filtere leere Labels heraus
                existing_labels = [l for l in existing_labels if l and l.strip()]
                # Füge zu existierenden Labels hinzu
                new_labels = list(set(existing_labels + labels))
                # Nochmal filtern um sicherzustellen
                new_labels = [l for l in new_labels if l and l.strip()]
            else:
                # Wenn Entity nicht gefunden, setze Labels trotzdem
                logger.warning(
                    f"Could not get entity {entity_id}, setting labels directly"
                )
                new_labels = [l for l in labels if l and l.strip()]

        except Exception as e:
            logger.warning(
                f"Error getting entity {entity_id}: {e}, setting labels directly"
            )
            new_labels = [l for l in labels if l and l.strip()]

        return await self.update_entity(entity_id=entity_id, labels=new_labels)

    async def enable_entity(self, entity_id: str) -> Dict[str, Any]:
        return await self.update_entity(entity_id=entity_id, disabled_by=None)

    def get_disabled_entities(self) -> List[Dict[str, Any]]:
        return [
            entity
            for entity in self.entities.values()
            if entity.get("disabled_by") is not None
        ]

    def get_entities_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        return [
            entity
            for entity_id, entity in self.entities.items()
            if entity_id.startswith(f"{domain}.")
        ]

    def get_entities_by_room(self, room: str) -> List[Dict[str, Any]]:
        return [
            entity
            for entity_id, entity in self.entities.items()
            if f".{room}_" in entity_id
        ]

    def get_entities_with_label(self, label: str) -> List[Dict[str, Any]]:
        return [
            entity
            for entity in self.entities.values()
            if label in entity.get("labels", [])
        ]

    def get_entities_without_label(self, label: str) -> List[Dict[str, Any]]:
        return [
            entity
            for entity in self.entities.values()
            if label not in entity.get("labels", [])
        ]


class DeviceRegistry:
    def __init__(self, websocket: HomeAssistantWebSocket):
        self.ws = websocket
        self.devices: Dict[str, Dict] = {}

    async def list_devices(self) -> List[Dict[str, Any]]:
        msg_id = await self.ws._send_message({"type": "config/device_registry/list"})

        response = await self.ws._receive_message()
        while response.get("id") != msg_id:
            response = await self.ws._receive_message()

        if not response.get("success"):
            raise Exception(f"Failed to list devices: {response}")

        self.devices = {d["id"]: d for d in response.get("result", [])}
        return response.get("result", [])

    async def update_device(self, device_id: str, labels: List[str]) -> Dict[str, Any]:
        message = {
            "type": "config/device_registry/update",
            "device_id": device_id,
            "labels": labels,
        }

        msg_id = await self.ws._send_message(message)

        response = await self.ws._receive_message()
        while response.get("id") != msg_id:
            response = await self.ws._receive_message()

        if not response.get("success"):
            raise Exception(f"Failed to update device {device_id}: {response}")

        return response.get("result", {})

    def get_device_entities(self, device_id: str, entities: List[Dict]) -> List[Dict]:
        return [entity for entity in entities if entity.get("device_id") == device_id]

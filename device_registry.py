#!/usr/bin/env python3
"""
Device Registry - Verwaltet Geräte in Home Assistant
"""
import logging
from typing import Dict, Any, Optional
from ha_websocket import HomeAssistantWebSocket

logger = logging.getLogger(__name__)


class DeviceRegistry:
    def __init__(self, websocket: HomeAssistantWebSocket):
        self.ws = websocket

    async def rename_device(self, device_id: str, new_name: str) -> Dict[str, Any]:
        """Benennt ein Gerät um"""
        logger.info(f"Renaming device {device_id} to '{new_name}'")

        try:
            # Update device registry
            msg_id = await self.ws._send_message(
                {
                    "type": "config/device_registry/update",
                    "device_id": device_id,
                    "name_by_user": new_name,
                }
            )

            response = await self.ws._receive_message()
            while response.get("id") != msg_id:
                response = await self.ws._receive_message()

            if not response.get("success"):
                error_msg = response.get("error", {}).get("message", "Unknown error")
                logger.error(f"Failed to rename device: {error_msg}")
                raise Exception(f"Failed to rename device: {error_msg}")

            logger.info(f"Successfully renamed device {device_id}")
            return {"success": True, "device_id": device_id, "new_name": new_name}

        except Exception as e:
            logger.error(f"Error renaming device {device_id}: {str(e)}")
            raise

    async def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Holt Geräteinformationen"""
        try:
            msg_id = await self.ws._send_message(
                {"type": "config/device_registry/list"}
            )

            response = await self.ws._receive_message()
            while response.get("id") != msg_id:
                response = await self.ws._receive_message()

            if response.get("success"):
                devices = response.get("result", [])
                for device in devices:
                    if device.get("id") == device_id:
                        return device

            return None

        except Exception as e:
            logger.error(f"Error getting device {device_id}: {str(e)}")
            return None

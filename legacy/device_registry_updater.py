#!/usr/bin/env python3
"""
Device Registry Updater - Aktualisiert Gerätenamen in Home Assistant
"""
import logging
from typing import Dict, Any, Optional
from ha_websocket import HomeAssistantWebSocket

logger = logging.getLogger(__name__)


class DeviceRegistryUpdater:
    def __init__(self, ws: HomeAssistantWebSocket):
        self.ws = ws
        
    async def rename_device(self, device_id: str, new_name: str) -> bool:
        """
        Benennt ein Gerät in Home Assistant um
        
        Args:
            device_id: Die Device Registry ID
            new_name: Der neue Name für das Gerät
            
        Returns:
            True wenn erfolgreich, False sonst
        """
        try:
            # Sende Device Registry Update
            msg_id = await self.ws._send_message({
                "type": "config/device_registry/update",
                "device_id": device_id,
                "name_by_user": new_name
            })
            
            # Warte auf Antwort
            response = await self.ws._receive_message()
            while response.get("id") != msg_id:
                response = await self.ws._receive_message()
            
            if response.get("success"):
                logger.info(f"Gerät {device_id} erfolgreich umbenannt zu: {new_name}")
                return True
            else:
                logger.error(f"Fehler beim Umbenennen des Geräts {device_id}: {response.get('error', {}).get('message', 'Unbekannter Fehler')}")
                return False
                
        except Exception as e:
            logger.error(f"Exception beim Umbenennen des Geräts {device_id}: {e}")
            return False
    
    async def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Holt die aktuellen Informationen eines Geräts
        
        Args:
            device_id: Die Device Registry ID
            
        Returns:
            Device Dictionary oder None
        """
        try:
            msg_id = await self.ws._send_message({
                "type": "config/device_registry/list"
            })
            
            response = await self.ws._receive_message()
            while response.get("id") != msg_id:
                response = await self.ws._receive_message()
            
            if response.get("success"):
                devices = response.get("result", [])
                for device in devices:
                    if device.get("id") == device_id:
                        return device
                logger.warning(f"Gerät {device_id} nicht gefunden")
                return None
            else:
                logger.error(f"Fehler beim Abrufen der Geräteliste: {response.get('error', {}).get('message', 'Unbekannter Fehler')}")
                return None
                
        except Exception as e:
            logger.error(f"Exception beim Abrufen des Geräts {device_id}: {e}")
            return None
import logging
from typing import Dict, List, Optional, Any
from ha_websocket import HomeAssistantWebSocket

logger = logging.getLogger(__name__)


class LabelRegistry:
    def __init__(self, websocket: HomeAssistantWebSocket):
        self.ws = websocket
        self.labels: Dict[str, Dict] = {}
        
    async def list_labels(self) -> List[Dict[str, Any]]:
        """Liste alle Labels auf"""
        msg_id = await self.ws._send_message({"type": "config/label_registry/list"})
        
        response = await self.ws._receive_message()
        while response.get("id") != msg_id:
            response = await self.ws._receive_message()
            
        if not response.get("success"):
            logger.error(f"Failed to list labels: {response}")
            return []
            
        labels = response.get("result", [])
        self.labels = {label["label_id"]: label for label in labels}
        return labels
        
    async def create_label(self, label_id: str, name: Optional[str] = None, 
                          color: Optional[str] = None, icon: Optional[str] = None) -> Dict[str, Any]:
        """Erstelle ein neues Label"""
        message = {
            "type": "config/label_registry/create",
            "label_id": label_id
        }
        
        if name:
            message["name"] = name
        if color:
            message["color"] = color
        if icon:
            message["icon"] = icon
            
        msg_id = await self.ws._send_message(message)
        
        response = await self.ws._receive_message()
        while response.get("id") != msg_id:
            response = await self.ws._receive_message()
            
        if not response.get("success"):
            raise Exception(f"Failed to create label {label_id}: {response}")
            
        return response.get("result", {})
        
    async def ensure_label_exists(self, label_id: str, name: Optional[str] = None) -> bool:
        """Stelle sicher, dass ein Label existiert. Erstelle es wenn nötig."""
        # Lade aktuelle Labels
        labels = await self.list_labels()
        
        # Prüfe ob Label existiert
        label_exists = any(label.get("label_id") == label_id for label in labels)
        
        if not label_exists:
            logger.info(f"Label '{label_id}' existiert nicht, erstelle es...")
            try:
                # Erstelle das Label
                if not name:
                    # Kapitalisiere die label_id als Fallback für den Namen
                    name = label_id.capitalize()
                    
                await self.create_label(
                    label_id=label_id,
                    name=name,
                    color="primary"  # Standard-Farbe
                )
                logger.info(f"Label '{label_id}' erfolgreich erstellt")
                return True
            except Exception as e:
                logger.error(f"Fehler beim Erstellen des Labels '{label_id}': {e}")
                return False
        else:
            logger.debug(f"Label '{label_id}' existiert bereits")
            return True
            
    async def delete_label(self, label_id: str) -> None:
        """Lösche ein Label"""
        message = {
            "type": "config/label_registry/delete",
            "label_id": label_id
        }
        
        msg_id = await self.ws._send_message(message)
        
        response = await self.ws._receive_message()
        while response.get("id") != msg_id:
            response = await self.ws._receive_message()
            
        if not response.get("success"):
            raise Exception(f"Failed to delete label {label_id}: {response}")
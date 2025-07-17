import logging
import re
from typing import Dict, List, Set, Any
from ha_websocket import HomeAssistantWebSocket
import aiohttp
import json

logger = logging.getLogger(__name__)


class DependencyScanner:
    def __init__(self, websocket: HomeAssistantWebSocket):
        self.ws = websocket
        
    async def find_entity_references(self, entity_id: str) -> Dict[str, List[str]]:
        references = {
            "automations": [],
            "scripts": [],
            "scenes": [],
            "groups": [],
            "lovelace": []
        }
        
        automations = await self._get_automations()
        for automation in automations:
            if self._entity_in_automation(entity_id, automation):
                references["automations"].append(automation.get("entity_id", automation.get("id")))
                
        scripts = await self._get_scripts()
        for script_id, script_data in scripts.items():
            if self._entity_in_config(entity_id, script_data):
                references["scripts"].append(f"script.{script_id}")
                
        scenes = await self._get_scenes()
        for scene_id, scene_data in scenes.items():
            if self._entity_in_config(entity_id, scene_data):
                references["scenes"].append(f"scene.{scene_id}")
                
        return references
        
    async def _get_automations(self) -> List[Dict[str, Any]]:
        msg_id = await self.ws._send_message({"type": "config/automation/list"})
        
        response = await self.ws._receive_message()
        while response.get("id") != msg_id:
            response = await self.ws._receive_message()
            
        if not response.get("success"):
            logger.debug(f"Failed to get automations: {response}")
            return []
            
        return response.get("result", [])
        
    async def _get_scripts(self) -> Dict[str, Any]:
        msg_id = await self.ws._send_message({"type": "config/script/list"})
        
        response = await self.ws._receive_message()
        while response.get("id") != msg_id:
            response = await self.ws._receive_message()
            
        if not response.get("success"):
            logger.debug(f"Failed to get scripts: {response}")
            return {}
            
        return response.get("result", {})
        
    async def _get_scenes(self) -> Dict[str, Any]:
        msg_id = await self.ws._send_message({"type": "config/scene/list"})
        
        response = await self.ws._receive_message()
        while response.get("id") != msg_id:
            response = await self.ws._receive_message()
            
        if not response.get("success"):
            logger.debug(f"Failed to get scenes: {response}")
            return {}
            
        return response.get("result", {})
        
    def _entity_in_automation(self, entity_id: str, automation: Dict[str, Any]) -> bool:
        automation_str = str(automation)
        return entity_id in automation_str
        
    def _entity_in_config(self, entity_id: str, config: Any) -> bool:
        if isinstance(config, dict):
            for key, value in config.items():
                if key == "entity_id" and value == entity_id:
                    return True
                if key == "entity_id" and isinstance(value, list) and entity_id in value:
                    return True
                if self._entity_in_config(entity_id, value):
                    return True
        elif isinstance(config, list):
            for item in config:
                if self._entity_in_config(entity_id, item):
                    return True
        elif isinstance(config, str):
            return entity_id in config
            
        return False
        
    async def update_entity_references(self, old_entity_id: str, new_entity_id: str) -> Dict[str, int]:
        updates = {
            "automations": 0,
            "scripts": 0,
            "scenes": 0
        }
        
        references = await self.find_entity_references(old_entity_id)
        
        for automation_id in references["automations"]:
            try:
                await self._update_automation(automation_id, old_entity_id, new_entity_id)
                updates["automations"] += 1
            except Exception as e:
                logger.debug(f"Failed to update automation {automation_id}: {e}")
                
        logger.info(f"Updated {updates['automations']} automations")
        
        # Update Scripts
        updates["scripts"] = await self.update_scripts(old_entity_id, new_entity_id)
        logger.info(f"Updated {updates['scripts']} scripts")
        
        # Update Scenes  
        updates["scenes"] = await self.update_scenes(old_entity_id, new_entity_id)
        logger.info(f"Updated {updates['scenes']} scenes")
        
        return updates
        
    async def _update_automation(self, automation_id: str, old_entity_id: str, new_entity_id: str):
        """Update automation configuration with new entity ID"""
        # Hole aktuelle Automation Config
        msg_id = await self.ws._send_message({
            "type": "config/automation/config",
            "id": automation_id.replace("automation.", "")
        })
        
        response = await self.ws._receive_message()
        while response.get("id") != msg_id:
            response = await self.ws._receive_message()
            
        if not response.get("success"):
            raise Exception(f"Failed to get automation config: {response}")
            
        config = response.get("result", {})
        
        # Replace entity_id in the config
        updated_config = self._replace_entity_in_config(config, old_entity_id, new_entity_id)
        
        # Update the automation
        msg_id = await self.ws._send_message({
            "type": "config/automation/update",
            "id": automation_id.replace("automation.", ""),
            "config": updated_config
        })
        
        response = await self.ws._receive_message()
        while response.get("id") != msg_id:
            response = await self.ws._receive_message()
            
        if not response.get("success"):
            raise Exception(f"Failed to update automation: {response}")
            
        logger.info(f"Successfully updated automation {automation_id}")
        
    async def scan_all_dependencies(self, entity_ids: List[str]) -> Dict[str, Dict[str, List[str]]]:
        all_dependencies = {}
        
        for entity_id in entity_ids:
            logger.info(f"Scanning dependencies for {entity_id}")
            dependencies = await self.find_entity_references(entity_id)
            
            if any(dependencies.values()):
                all_dependencies[entity_id] = dependencies
                
        return all_dependencies
        
    def _replace_entity_in_config(self, config: Any, old_entity_id: str, new_entity_id: str) -> Any:
        """Recursively replace entity IDs in configuration"""
        if isinstance(config, dict):
            new_config = {}
            for key, value in config.items():
                if key == "entity_id":
                    if isinstance(value, str) and value == old_entity_id:
                        new_config[key] = new_entity_id
                    elif isinstance(value, list):
                        new_config[key] = [new_entity_id if e == old_entity_id else e for e in value]
                    else:
                        new_config[key] = value
                else:
                    new_config[key] = self._replace_entity_in_config(value, old_entity_id, new_entity_id)
            return new_config
        elif isinstance(config, list):
            return [self._replace_entity_in_config(item, old_entity_id, new_entity_id) for item in config]
        elif isinstance(config, str):
            # Be careful with string replacements in templates!
            if config == old_entity_id:
                return new_entity_id
            # Replace in templates with word boundaries
            import re
            pattern = r'\b' + re.escape(old_entity_id) + r'\b'
            return re.sub(pattern, new_entity_id, config)
        else:
            return config
            
    async def update_scripts(self, old_entity_id: str, new_entity_id: str) -> int:
        """Update all scripts that reference the entity"""
        references = await self.find_entity_references(old_entity_id)
        updated = 0
        
        for script_id in references["scripts"]:
            try:
                await self._update_script(script_id, old_entity_id, new_entity_id)
                updated += 1
            except Exception as e:
                logger.debug(f"Failed to update script {script_id}: {e}")
                
        return updated
        
    async def _update_script(self, script_id: str, old_entity_id: str, new_entity_id: str):
        """Update script configuration with new entity ID"""
        script_name = script_id.replace("script.", "")
        
        # Hole Scripts
        scripts = await self._get_scripts()
        if script_name not in scripts:
            raise Exception(f"Script {script_name} not found")
            
        # Update Config
        updated_config = self._replace_entity_in_config(scripts[script_name], old_entity_id, new_entity_id)
        
        # Speichere updated scripts
        msg_id = await self.ws._send_message({
            "type": "config/script/update",
            "id": script_name,
            "sequence": updated_config.get("sequence", updated_config)
        })
        
        response = await self.ws._receive_message()
        while response.get("id") != msg_id:
            response = await self.ws._receive_message()
            
        if not response.get("success"):
            raise Exception(f"Failed to update script: {response}")
            
        logger.info(f"Successfully updated script {script_id}")
        
    async def update_scenes(self, old_entity_id: str, new_entity_id: str) -> int:
        """Update all scenes that reference the entity"""
        references = await self.find_entity_references(old_entity_id)
        updated = 0
        
        for scene_id in references["scenes"]:
            try:
                await self._update_scene(scene_id, old_entity_id, new_entity_id)
                updated += 1
            except Exception as e:
                logger.debug(f"Failed to update scene {scene_id}: {e}")
                
        return updated
        
    async def _update_scene(self, scene_id: str, old_entity_id: str, new_entity_id: str):
        """Update scene configuration with new entity ID"""
        scene_name = scene_id.replace("scene.", "")
        
        # Hole Scenes
        scenes = await self._get_scenes()
        if scene_name not in scenes:
            raise Exception(f"Scene {scene_name} not found")
            
        # Update Config
        updated_config = self._replace_entity_in_config(scenes[scene_name], old_entity_id, new_entity_id)
        
        # Speichere updated scene
        msg_id = await self.ws._send_message({
            "type": "config/scene/update",
            "id": scene_name,
            "entities": updated_config.get("entities", updated_config)
        })
        
        response = await self.ws._receive_message()
        while response.get("id") != msg_id:
            response = await self.ws._receive_message()
            
        if not response.get("success"):
            raise Exception(f"Failed to update scene: {response}")
            
        logger.info(f"Successfully updated scene {scene_id}")
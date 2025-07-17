import re
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class MappingGenerator:
    def __init__(self):
        # No room mappings needed anymore - we keep the HA convention
        self.room_mapping = {
            # "buro": "buero",  # NOT anymore - HA uses "buro" for "Büro"
            # "kuche": "kueche",  # NOT anymore - HA uses "kuche" for "Küche"
        }
        
        self.standard_entity_types = {
            "light": ["licht"],
            "sensor": ["temperatur", "luftfeuchtigkeit", "helligkeit", "bewegung", "verbrauch", 
                      "spannung", "strom", "energie", "batterie", "signal", "co2", "druck",
                      "soll_temperatur", "ventil"],
            "switch": ["zustand", "kindersicherung", "ueberlast"],
            "binary_sensor": ["bewegung", "erreichbar", "kontakt", "rauch", "wasser"],
            "climate": ["heizung", "kuehlung"],
            "cover": ["rollo", "jalousie"],
            "media_player": ["wiedergabe", "lautstaerke", "quelle", "titel", "kuenstler"]
        }
        
        # Home Assistant Standard: Umlauts are simply omitted
        self.umlaut_mapping = {
            "ä": "a", "ö": "o", "ü": "u", "ß": "ss",
            "Ä": "A", "Ö": "O", "Ü": "U"
        }
        
    def normalize_string(self, text: str) -> str:
        for umlaut, replacement in self.umlaut_mapping.items():
            text = text.replace(umlaut, replacement)
        
        text = re.sub(r'[^a-zA-Z0-9_]', '_', text)
        text = re.sub(r'_+', '_', text)
        text = text.strip('_').lower()
        
        return text
        
    def extract_components(self, entity_id: str) -> Dict[str, str]:
        parts = entity_id.split('.')
        if len(parts) != 2:
            return {}
            
        domain = parts[0]
        name_parts = parts[1].split('_')
        
        components = {
            "domain": domain,
            "room": None,
            "device": None,
            "entity": None,
            "full_name": parts[1]
        }
        
        # Bekannte Räume (HA-Konvention)
        known_rooms = ["wohnzimmer", "buro", "kuche", "schlafzimmer", "badezimmer", 
                      "kinderzimmer", "eingang", "diele", "balkon", "kammer", "dusche", "keller"]
        
        for i, part in enumerate(name_parts):
            if part in known_rooms or part in self.room_mapping or part in self.room_mapping.values():
                components["room"] = part
                remaining_parts = name_parts[i+1:]
                
                if remaining_parts:
                    entity_type_found = False
                    for j in range(len(remaining_parts)-1, -1, -1):
                        if remaining_parts[j] in sum(self.standard_entity_types.values(), []):
                            components["entity"] = "_".join(remaining_parts[j:])
                            components["device"] = "_".join(remaining_parts[:j]) if j > 0 else None
                            entity_type_found = True
                            break
                    
                    if not entity_type_found:
                        components["device"] = "_".join(remaining_parts)
                        
                        if domain in self.standard_entity_types:
                            default_types = self.standard_entity_types[domain]
                            if default_types:
                                components["entity"] = default_types[0]
                break
                
        return components
        
    def generate_new_entity_id(self, entity_id: str, components: Optional[Dict] = None) -> str:
        if not components:
            components = self.extract_components(entity_id)
            
        if not components or not components.get("room"):
            logger.warning(f"Could not extract components from {entity_id}")
            return entity_id
            
        domain = components["domain"]
        room = components["room"]
        
        if room in self.room_mapping:
            room = self.room_mapping[room]
            
        room = self.normalize_string(room)
        
        parts = [room]
        
        if components.get("device"):
            device = self.normalize_string(components["device"])
            parts.append(device)
            
        if components.get("entity"):
            entity = self.normalize_string(components["entity"])
        else:
            if domain in self.standard_entity_types and self.standard_entity_types[domain]:
                entity = self.standard_entity_types[domain][0]
            else:
                entity = None
                
        if entity:
            parts.append(entity)
            
        new_name = "_".join(parts)
        return f"{domain}.{new_name}"
        
    def generate_friendly_name(self, entity_id: str, components: Optional[Dict] = None) -> str:
        if not components:
            components = self.extract_components(entity_id)
            
        if not components:
            return entity_id.split('.')[-1].replace('_', ' ').title()
            
        parts = []
        
        if components.get("room"):
            room = components["room"]
            # Home Assistant Konvention: buro = Büro, kuche = Küche
            if room == "buro":
                room = "Büro"
            elif room == "kuche":
                room = "Küche"
            else:
                room = room.title()
            parts.append(room)
            
        if components.get("device"):
            device = components["device"].replace('_', ' ')
            # Keep original names, unless there are already umlauts
            # For the friendly name we use the original text from the current entity
            parts.append(device.title())
            
        if components.get("entity"):
            entity = components["entity"].replace('_', ' ')
            parts.append(entity.title())
            
        return " ".join(parts)
        
    def generate_mapping(self, entity_ids: List[str]) -> Dict[str, Tuple[str, str]]:
        mapping = {}
        
        for entity_id in entity_ids:
            components = self.extract_components(entity_id)
            new_entity_id = self.generate_new_entity_id(entity_id, components)
            friendly_name = self.generate_friendly_name(new_entity_id, components)
            
            if entity_id != new_entity_id:
                mapping[entity_id] = (new_entity_id, friendly_name)
                logger.info(f"Mapping: {entity_id} -> {new_entity_id} ({friendly_name})")
                
        return mapping
        
    def needs_renaming(self, entity_id: str) -> bool:
        new_entity_id = self.generate_new_entity_id(entity_id)
        return entity_id != new_entity_id
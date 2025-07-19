#!/usr/bin/env python3
"""
Naming Override System - Speichert benutzerdefinierte Namen basierend auf Registry IDs
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class NamingOverrides:
    def __init__(self, storage_path: str = "naming_overrides.json"):
        self.storage_path = Path(storage_path)
        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """Lade gespeicherte Overrides"""
        default_data = {"entities": {}, "devices": {}, "areas": {}}

        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    # Ensure all required keys exist
                    for key in default_data:
                        if key not in existing_data:
                            existing_data[key] = default_data[key]
                    return existing_data
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Fehler beim Laden der Overrides: {e}")

        return default_data

    def _save_data(self) -> None:
        """Speichere Overrides"""
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.info(
                f"Overrides gespeichert: {len(self.data['entities'])} entities, {len(self.data['devices'])} devices"
            )
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Overrides: {e}")

    # === Entity Overrides ===

    def set_entity_override(self, registry_id: str, name: str, type_override: Optional[str] = None) -> None:
        """Setze Entity Name Override"""
        if "entities" not in self.data:
            self.data["entities"] = {}
        self.data["entities"][registry_id] = {"name": name}
        if type_override:
            self.data["entities"][registry_id]["type"] = type_override
        self._save_data()
        logger.info(f"Entity override gesetzt: {registry_id} -> {name}")

    def get_entity_override(self, registry_id: str) -> Optional[Dict[str, str]]:
        """Hole Entity Override"""
        return self.data.get("entities", {}).get(registry_id)

    def remove_entity_override(self, registry_id: str) -> None:
        """Entferne Entity Override"""
        if "entities" in self.data and registry_id in self.data["entities"]:
            del self.data["entities"][registry_id]
            self._save_data()
            logger.info(f"Entity override entfernt: {registry_id}")

    # === Device Overrides ===

    def set_device_override(self, device_id: str, name: str) -> None:
        """Setze Device Name Override"""
        if "devices" not in self.data:
            self.data["devices"] = {}
        self.data["devices"][device_id] = {"name": name}
        self._save_data()
        logger.info(f"Device override gesetzt: {device_id} -> {name}")

    def get_device_override(self, device_id: str) -> Optional[Dict[str, str]]:
        """Hole Device Override"""
        return self.data.get("devices", {}).get(device_id)

    def remove_device_override(self, device_id: str) -> None:
        """Entferne Device Override"""
        if "devices" in self.data and device_id in self.data["devices"]:
            del self.data["devices"][device_id]
            self._save_data()
            logger.info(f"Device override entfernt: {device_id}")

    # === Area Overrides ===

    def set_area_override(self, area_id: str, name: str) -> None:
        """Setze Area Name Override"""
        if "areas" not in self.data:
            self.data["areas"] = {}
        self.data["areas"][area_id] = {"name": name}
        self._save_data()
        logger.info(f"Area override gesetzt: {area_id} -> {name}")

    def get_area_override(self, area_id: str) -> Optional[Dict[str, str]]:
        """Hole Area Override"""
        return self.data.get("areas", {}).get(area_id)

    def remove_area_override(self, area_id: str) -> None:
        """Entferne Area Override"""
        if "areas" in self.data and area_id in self.data["areas"]:
            del self.data["areas"][area_id]
            self._save_data()
            logger.info(f"Area override entfernt: {area_id}")

    # === Bulk Operations ===

    def get_all_entity_overrides(self) -> Dict[str, Dict[str, str]]:
        """Hole alle Entity Overrides"""
        return self.data.get("entities", {}).copy()

    def get_all_device_overrides(self) -> Dict[str, Dict[str, str]]:
        """Hole alle Device Overrides"""
        return self.data.get("devices", {}).copy()

    def get_all_area_overrides(self) -> Dict[str, Dict[str, str]]:
        """Hole alle Area Overrides"""
        return self.data.get("areas", {}).copy()

    def clear_all(self) -> None:
        """Lösche alle Overrides"""
        self.data = {"entities": {}, "devices": {}, "areas": {}}
        self._save_data()
        logger.info("Alle Overrides gelöscht")

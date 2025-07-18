#!/usr/bin/env python3
"""
Naming Override System - Speichert benutzerdefinierte Namen basierend auf Registry IDs
"""
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class NamingOverrides:
    def __init__(self, storage_path: str = "naming_overrides.json"):
        self.storage_path = Path(storage_path)
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """Lade gespeicherte Overrides"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Fehler beim Laden der Overrides: {e}")

        # Default-Struktur
        data: Dict[str, Any] = {"entities": {}, "devices": {}, "areas": {}}
        # Ensure areas key exists in existing data
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    if "areas" not in existing_data:
                        existing_data["areas"] = {}
                    return existing_data
            except Exception:
                pass
        return data

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

    def set_entity_override(
        self, registry_id: str, name: str, type_override: Optional[str] = None
    ) -> None:
        """Setze Entity Name Override"""
        self.data["entities"][registry_id] = {"name": name}
        if type_override:
            self.data["entities"][registry_id]["type"] = type_override
        self._save_data()
        logger.info(f"Entity override gesetzt: {registry_id} -> {name}")

    def get_entity_override(self, registry_id: str) -> Optional[Dict[str, str]]:
        """Hole Entity Override"""
        return self.data["entities"].get(registry_id)

    def remove_entity_override(self, registry_id: str) -> None:
        """Entferne Entity Override"""
        if registry_id in self.data["entities"]:
            del self.data["entities"][registry_id]
            self._save_data()
            logger.info(f"Entity override entfernt: {registry_id}")

    # === Device Overrides ===

    def set_device_override(self, device_id: str, name: str) -> None:
        """Setze Device Name Override"""
        self.data["devices"][device_id] = {"name": name}
        self._save_data()
        logger.info(f"Device override gesetzt: {device_id} -> {name}")

    def get_device_override(self, device_id: str) -> Optional[Dict[str, str]]:
        """Hole Device Override"""
        return self.data["devices"].get(device_id)

    def remove_device_override(self, device_id: str) -> None:
        """Entferne Device Override"""
        if device_id in self.data["devices"]:
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
        return self.data["entities"].copy()

    def get_all_device_overrides(self) -> Dict[str, Dict[str, str]]:
        """Hole alle Device Overrides"""
        return self.data["devices"].copy()

    def get_all_area_overrides(self) -> Dict[str, Dict[str, str]]:
        """Hole alle Area Overrides"""
        return self.data.get("areas", {}).copy()

    def clear_all(self) -> None:
        """Lösche alle Overrides"""
        self.data = {"entities": {}, "devices": {}, "areas": {}}
        self._save_data()
        logger.info("Alle Overrides gelöscht")

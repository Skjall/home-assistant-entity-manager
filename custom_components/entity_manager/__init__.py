"""The Entity Manager integration."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.components import frontend
from homeassistant.components import websocket_api

from .const import (
    DOMAIN,
    LABEL_MAINTAINED,
    SERVICE_ANALYZE_ENTITIES,
    SERVICE_RENAME_ENTITY,
    SERVICE_RENAME_BULK,
    DEFAULT_LIMIT,
    CONF_LIMIT,
    CONF_SKIP_REVIEWED,
    CONF_SHOW_REVIEWED,
    CONF_DRY_RUN,
)
from .entity_restructurer import EntityRestructurer
from .naming_overrides import NamingOverrides

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.FRONTEND]

# Service schemas
ANALYZE_ENTITIES_SCHEMA = vol.Schema({
    vol.Optional(CONF_LIMIT, default=DEFAULT_LIMIT): cv.positive_int,
    vol.Optional(CONF_SKIP_REVIEWED, default=False): cv.boolean,
    vol.Optional(CONF_SHOW_REVIEWED, default=False): cv.boolean,
})

RENAME_ENTITY_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
})

RENAME_BULK_SCHEMA = vol.Schema({
    vol.Optional("entity_ids"): [cv.entity_id],
    vol.Optional(CONF_LIMIT, default=DEFAULT_LIMIT): cv.positive_int,
    vol.Optional(CONF_SKIP_REVIEWED, default=True): cv.boolean,
    vol.Optional(CONF_DRY_RUN, default=True): cv.boolean,
})


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Entity Manager component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Entity Manager from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    try:
        # Initialize the naming overrides
        naming_overrides = NamingOverrides()
        
        # Store in hass data
        hass.data[DOMAIN][entry.entry_id] = {
            "naming_overrides": naming_overrides,
        }
        
        # Register services only once
        if len(hass.data[DOMAIN]) == 1:
            await async_setup_services(hass)
            
        # Register panel
        hass.http.register_static_path(
            f"/api/{DOMAIN}",
            hass.config.path(f"custom_components/{DOMAIN}/panel"),
            cache_headers=False,
        )
        
        await hass.config_entries.async_forward_entry_setup(entry, "frontend")
        
        # Setup websocket commands
        await async_setup_websocket_commands(hass)
        
        return True
        
    except Exception as err:
        _LOGGER.error("Failed to set up Entity Manager: %s", err)
        raise


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    try:
        # Unload frontend
        unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "frontend")
        if not unload_ok:
            return False
            
        # Only unregister services if this is the last instance
        if len(hass.data[DOMAIN]) == 1:
            hass.services.async_remove(DOMAIN, SERVICE_ANALYZE_ENTITIES)
            hass.services.async_remove(DOMAIN, SERVICE_RENAME_ENTITY)
            hass.services.async_remove(DOMAIN, SERVICE_RENAME_BULK)
        
        hass.data[DOMAIN].pop(entry.entry_id)
        
        return True
        
    except Exception as err:
        _LOGGER.error("Failed to unload Entity Manager: %s", err)
        return False


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the Entity Manager integration."""
    
    async def analyze_entities(call: ServiceCall) -> ServiceResponse:
        """Analyze entities and preview renaming."""
        try:
            # Get parameters
            limit: int = call.data.get(CONF_LIMIT, DEFAULT_LIMIT)
            skip_reviewed: bool = call.data.get(CONF_SKIP_REVIEWED, False)
            show_reviewed: bool = call.data.get(CONF_SHOW_REVIEWED, False)
            
            if skip_reviewed and show_reviewed:
                raise ServiceValidationError(
                    "Cannot use both skip_reviewed and show_reviewed"
                )
            
            # Get registries
            entity_reg = er.async_get(hass)
            device_reg = dr.async_get(hass)
            area_reg = ar.async_get(hass)
            
            # Get naming overrides
            naming_overrides = _get_naming_overrides(hass)
            
            # Create restructurer
            restructurer = _create_restructurer(
                hass, naming_overrides, entity_reg, device_reg, area_reg
            )
            
            # Get entities to analyze
            entities_to_analyze = _get_entities_to_analyze(
                entity_reg, skip_reviewed, show_reviewed, limit
            )
            
            # Analyze entities
            results = []
            for entity in entities_to_analyze:
                try:
                    state_info = {"attributes": {}}
                    new_id, friendly_name = restructurer.generate_new_entity_id(
                        entity.entity_id, state_info
                    )
                    
                    results.append({
                        "current_id": entity.entity_id,
                        "new_id": new_id,
                        "friendly_name": friendly_name,
                        "has_maintained_label": LABEL_MAINTAINED in (entity.labels or set()),
                        "would_change": entity.entity_id != new_id,
                    })
                    
                except Exception as err:
                    _LOGGER.warning(
                        "Failed to analyze entity %s: %s", entity.entity_id, err
                    )
                    results.append({
                        "current_id": entity.entity_id,
                        "error": str(err),
                    })
            
            return {
                "entities": results,
                "total_analyzed": len(results),
                "total_entities": len(entity_reg.entities),
            }
            
        except ServiceValidationError:
            raise
        except Exception as err:
            _LOGGER.error("Failed to analyze entities: %s", err)
            raise HomeAssistantError(f"Failed to analyze entities: {err}")
    
    async def rename_entity(call: ServiceCall) -> ServiceResponse:
        """Rename a single entity."""
        try:
            entity_id: str = call.data["entity_id"]
            
            # Get registries
            entity_reg = er.async_get(hass)
            device_reg = dr.async_get(hass)
            area_reg = ar.async_get(hass)
            
            # Validate entity exists
            entity = entity_reg.async_get(entity_id)
            if not entity:
                raise ServiceValidationError(
                    f"Entity {entity_id} not found"
                )
            
            # Get naming overrides
            naming_overrides = _get_naming_overrides(hass)
            
            # Create restructurer
            restructurer = _create_restructurer(
                hass, naming_overrides, entity_reg, device_reg, area_reg
            )
            
            # Generate new ID
            state_info = {"attributes": {}}
            new_id, friendly_name = restructurer.generate_new_entity_id(
                entity_id, state_info
            )
            
            # Check if actually needs renaming
            if entity_id == new_id:
                return {
                    "success": True,
                    "old_id": entity_id,
                    "new_id": new_id,
                    "friendly_name": friendly_name,
                    "changed": False,
                    "message": "Entity already has correct name",
                }
            
            # Update entity
            try:
                entity_reg.async_update_entity(
                    entity_id,
                    new_entity_id=new_id,
                    name=friendly_name
                )
                
                # Add maintained label
                labels = set(entity.labels or set())
                labels.add(LABEL_MAINTAINED)
                entity_reg.async_update_entity(
                    new_id,
                    labels=labels
                )
                
                _LOGGER.info(
                    "Successfully renamed entity %s to %s", entity_id, new_id
                )
                
                return {
                    "success": True,
                    "old_id": entity_id,
                    "new_id": new_id,
                    "friendly_name": friendly_name,
                    "changed": True,
                }
                
            except Exception as err:
                _LOGGER.error(
                    "Failed to rename entity %s: %s", entity_id, err
                )
                raise HomeAssistantError(
                    f"Failed to rename entity: {err}"
                )
                
        except ServiceValidationError:
            raise
        except Exception as err:
            _LOGGER.error("Rename entity service failed: %s", err)
            raise HomeAssistantError(f"Rename entity service failed: {err}")
    
    async def rename_bulk(call: ServiceCall) -> ServiceResponse:
        """Rename multiple entities in bulk."""
        try:
            # Get parameters
            entity_ids: Optional[List[str]] = call.data.get("entity_ids")
            limit: int = call.data.get(CONF_LIMIT, DEFAULT_LIMIT)
            skip_reviewed: bool = call.data.get(CONF_SKIP_REVIEWED, True)
            dry_run: bool = call.data.get(CONF_DRY_RUN, True)
            
            # Get registries
            entity_reg = er.async_get(hass)
            device_reg = dr.async_get(hass)
            area_reg = ar.async_get(hass)
            
            # Get naming overrides
            naming_overrides = _get_naming_overrides(hass)
            
            # Create restructurer
            restructurer = _create_restructurer(
                hass, naming_overrides, entity_reg, device_reg, area_reg
            )
            
            # Get entities to rename
            if entity_ids:
                entities_to_rename = [
                    entity_reg.async_get(eid) for eid in entity_ids
                    if entity_reg.async_get(eid) is not None
                ]
            else:
                entities_to_rename = _get_entities_to_analyze(
                    entity_reg, skip_reviewed, False, limit
                )
            
            # Process entities
            results = {
                "processed": [],
                "errors": [],
                "skipped": [],
                "total": len(entities_to_rename),
                "dry_run": dry_run,
            }
            
            for entity in entities_to_rename:
                try:
                    # Skip if has maintained label and skip_reviewed is True
                    if skip_reviewed and LABEL_MAINTAINED in (entity.labels or set()):
                        results["skipped"].append({
                            "entity_id": entity.entity_id,
                            "reason": "Has maintained label",
                        })
                        continue
                    
                    # Generate new ID
                    state_info = {"attributes": {}}
                    new_id, friendly_name = restructurer.generate_new_entity_id(
                        entity.entity_id, state_info
                    )
                    
                    # Check if needs renaming
                    if entity.entity_id == new_id:
                        results["skipped"].append({
                            "entity_id": entity.entity_id,
                            "reason": "Already has correct name",
                        })
                        continue
                    
                    if not dry_run:
                        # Actually rename
                        entity_reg.async_update_entity(
                            entity.entity_id,
                            new_entity_id=new_id,
                            name=friendly_name
                        )
                        
                        # Add maintained label
                        labels = set(entity.labels or set())
                        labels.add(LABEL_MAINTAINED)
                        entity_reg.async_update_entity(
                            new_id,
                            labels=labels
                        )
                    
                    results["processed"].append({
                        "old_id": entity.entity_id,
                        "new_id": new_id,
                        "friendly_name": friendly_name,
                    })
                    
                except Exception as err:
                    _LOGGER.warning(
                        "Failed to process entity %s: %s", entity.entity_id, err
                    )
                    results["errors"].append({
                        "entity_id": entity.entity_id,
                        "error": str(err),
                    })
            
            return results
            
        except Exception as err:
            _LOGGER.error("Bulk rename service failed: %s", err)
            raise HomeAssistantError(f"Bulk rename service failed: {err}")
    
    # Register services
    hass.services.async_register(
        DOMAIN,
        SERVICE_ANALYZE_ENTITIES,
        analyze_entities,
        schema=ANALYZE_ENTITIES_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_RENAME_ENTITY,
        rename_entity,
        schema=RENAME_ENTITY_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_RENAME_BULK,
        rename_bulk,
        schema=RENAME_BULK_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )


def _get_naming_overrides(hass: HomeAssistant) -> NamingOverrides:
    """Get naming overrides from the first config entry."""
    for entry_data in hass.data[DOMAIN].values():
        return entry_data["naming_overrides"]
    return NamingOverrides()


def _create_restructurer(
    hass: HomeAssistant,
    naming_overrides: NamingOverrides,
    entity_reg: er.EntityRegistry,
    device_reg: dr.DeviceRegistry,
    area_reg: ar.AreaRegistry,
) -> EntityRestructurer:
    """Create and configure an EntityRestructurer instance."""
    restructurer = EntityRestructurer(None, naming_overrides)
    
    # Load areas
    restructurer.areas = {
        area.id: {"area_id": area.id, "name": area.name}
        for area in area_reg.areas.values()
    }
    
    # Load devices
    restructurer.devices = {
        device.id: {
            "id": device.id,
            "name": device.name,
            "name_by_user": device.name_by_user,
            "model": device.model,
            "area_id": device.area_id,
        }
        for device in device_reg.devices.values()
    }
    
    # Load entities
    restructurer.entities = {
        entity.entity_id: {
            "entity_id": entity.entity_id,
            "id": entity.id,
            "device_id": entity.device_id,
            "area_id": entity.area_id,
            "labels": entity.labels,
        }
        for entity in entity_reg.entities.values()
    }
    
    return restructurer


def _get_entities_to_analyze(
    entity_reg: er.EntityRegistry,
    skip_reviewed: bool,
    show_reviewed: bool,
    limit: int,
) -> List[er.RegistryEntry]:
    """Get entities to analyze based on filters."""
    entities = []
    
    for entity in entity_reg.entities.values():
        has_maintained = LABEL_MAINTAINED in (entity.labels or set())
        
        if skip_reviewed and has_maintained:
            continue
        elif show_reviewed and not has_maintained:
            continue
            
        entities.append(entity)
        
        if len(entities) >= limit:
            break
    
    return entities


async def async_setup_websocket_commands(hass: HomeAssistant) -> None:
    """Set up websocket commands for the Entity Manager integration."""
    
    @websocket_api.websocket_command({
        vol.Required("type"): "entity_manager/get_areas",
    })
    @websocket_api.async_response
    async def websocket_get_areas(hass, connection, msg):
        """Get all areas with entity counts."""
        entity_reg = er.async_get(hass)
        area_reg = ar.async_get(hass)
        
        areas = []
        for area in area_reg.areas.values():
            entity_count = sum(
                1 for entity in entity_reg.entities.values()
                if entity.area_id == area.id or (
                    entity.device_id and 
                    dr.async_get(hass).async_get(entity.device_id) and
                    dr.async_get(hass).async_get(entity.device_id).area_id == area.id
                )
            )
            areas.append({
                "area_id": area.id,
                "name": area.name,
                "entity_count": entity_count
            })
        
        connection.send_result(msg["id"], {"areas": areas})
    
    @websocket_api.websocket_command({
        vol.Required("type"): "entity_manager/get_entities_by_area",
        vol.Required("area_name"): str,
        vol.Optional("domain"): str,
        vol.Optional("skip_maintained"): bool,
    })
    @websocket_api.async_response
    async def websocket_get_entities_by_area(hass, connection, msg):
        """Get entities for a specific area."""
        area_name = msg["area_name"]
        domain_filter = msg.get("domain")
        skip_maintained = msg.get("skip_maintained", False)
        
        entity_reg = er.async_get(hass)
        area_reg = ar.async_get(hass)
        device_reg = dr.async_get(hass)
        
        # Find area by name
        area = None
        for a in area_reg.areas.values():
            if a.name == area_name:
                area = a
                break
        
        if not area:
            connection.send_error(msg["id"], "area_not_found", f"Area {area_name} not found")
            return
        
        # Get naming overrides
        naming_overrides = _get_naming_overrides(hass)
        
        # Create restructurer
        restructurer = _create_restructurer(
            hass, naming_overrides, entity_reg, device_reg, area_reg
        )
        
        entities = []
        for entity in entity_reg.entities.values():
            # Check if entity belongs to area
            entity_area_id = entity.area_id
            if not entity_area_id and entity.device_id:
                device = device_reg.async_get(entity.device_id)
                if device:
                    entity_area_id = device.area_id
            
            if entity_area_id != area.id:
                continue
            
            # Apply domain filter
            if domain_filter and not entity.entity_id.startswith(f"{domain_filter}."):
                continue
            
            # Skip maintained if requested
            if skip_maintained and LABEL_MAINTAINED in (entity.labels or set()):
                continue
            
            # Generate new ID
            try:
                state_info = {"attributes": {}}
                new_id, friendly_name = restructurer.generate_new_entity_id(
                    entity.entity_id, state_info
                )
                
                entities.append({
                    "entity_id": entity.entity_id,
                    "new_entity_id": new_id,
                    "friendly_name": friendly_name,
                    "needs_rename": entity.entity_id != new_id,
                    "has_maintained_label": LABEL_MAINTAINED in (entity.labels or set()),
                })
            except Exception as err:
                _LOGGER.warning(f"Failed to process entity {entity.entity_id}: {err}")
        
        connection.send_result(msg["id"], {"entities": entities})
    
    @websocket_api.websocket_command({
        vol.Required("type"): "entity_manager/rename_entities",
        vol.Required("entity_ids"): [str],
    })
    @websocket_api.async_response
    async def websocket_rename_entities(hass, connection, msg):
        """Rename multiple entities."""
        entity_ids = msg["entity_ids"]
        
        results = []
        for entity_id in entity_ids:
            try:
                # Call the rename service
                result = await hass.services.async_call(
                    DOMAIN,
                    SERVICE_RENAME_ENTITY,
                    {"entity_id": entity_id},
                    blocking=True,
                    return_response=True
                )
                results.append(result)
            except Exception as err:
                results.append({
                    "success": False,
                    "entity_id": entity_id,
                    "error": str(err)
                })
        
        connection.send_result(msg["id"], {"results": results})
    
    # Register commands
    websocket_api.async_register_command(hass, websocket_get_areas)
    websocket_api.async_register_command(hass, websocket_get_entities_by_area)
    websocket_api.async_register_command(hass, websocket_rename_entities)
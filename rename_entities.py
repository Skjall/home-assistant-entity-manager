#!/usr/bin/env python3
"""
Home Assistant Entity Renamer - Komplettes Tool
Kann Entitäten umbenennen UND alle Abhängigkeiten (Automationen, Scripts, Szenen) aktualisieren
"""
import asyncio
import argparse
import logging
import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from colorama import init, Fore, Style
from tabulate import tabulate
from dotenv import load_dotenv

from ha_websocket import HomeAssistantWebSocket
from entity_registry import EntityRegistry, DeviceRegistry
from dependency_scanner import DependencyScanner
from ha_client import HomeAssistantClient
from entity_restructurer import EntityRestructurer

init()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EntityRenamer:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self.ws_url = base_url.replace("https://", "wss://").replace("http://", "ws://") + "/api/websocket"
        self.client = HomeAssistantClient(base_url, token)
        self.entity_restructurer = EntityRestructurer(self.client)
        self.ws = None
        self.entity_registry = None
        self.device_registry = None
        self.dependency_scanner = None
        self.stats = {
            "total": 0,
            "renamed": 0,
            "failed": 0,
            "skipped": 0,
            "dependencies_updated": 0,
            "labels_added": 0
        }
        
    async def connect_websocket(self):
        """Verbinde WebSocket für Registry-Updates"""
        self.ws = HomeAssistantWebSocket(self.ws_url, self.token)
        await self.ws.connect()
        self.entity_registry = EntityRegistry(self.ws)
        self.device_registry = DeviceRegistry(self.ws)
        self.dependency_scanner = DependencyScanner(self.ws)
        
    async def disconnect_websocket(self):
        if self.ws:
            await self.ws.disconnect()
            
    async def test_connection(self):
        """Teste Verbindung zu Home Assistant"""
        print(f"\n{Fore.CYAN}=== Teste Verbindung ==={Style.RESET_ALL}")
        
        async with self.client:
            try:
                config = await self.client.get_config()
                print(f"{Fore.GREEN}✓ Verbindung erfolgreich{Style.RESET_ALL}")
                print(f"  Home Assistant Version: {config.get('version', 'unbekannt')}")
                print(f"  Standort: {config.get('location_name', 'unbekannt')}")
                
                states = await self.client.get_states()
                print(f"  Anzahl Entitäten: {len(states)}")
                
                # Zähle Domains
                domains = {}
                for state in states:
                    domain = state["entity_id"].split(".")[0]
                    domains[domain] = domains.get(domain, 0) + 1
                    
                print(f"\n  Top Domains:")
                for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"    - {domain}: {count}")
                    
                return True
                
            except Exception as e:
                print(f"{Fore.RED}✗ Verbindungsfehler: {str(e)}{Style.RESET_ALL}")
                return False
            
    async def analyze_entities(self, domain: str = None, room: str = None, limit: int = None):
        """Analysiere Entitäten über REST API"""
        print(f"\n{Fore.CYAN}=== Analysiere Entitäten ==={Style.RESET_ALL}")
        
        async with self.client:
            if not await self.client.check_api_access():
                raise Exception("Kann nicht auf Home Assistant API zugreifen")
                
            states = await self.client.get_states()
            
            entities = []
            for state in states:
                entity_id = state.get("entity_id", "")
                if domain and not entity_id.startswith(f"{domain}."):
                    continue
                if room and f".{room}_" not in entity_id:
                    continue
                entities.append({
                    "entity_id": entity_id,
                    "state": state.get("state"),
                    "attributes": state.get("attributes", {})
                })
                
            if limit:
                entities = entities[:limit]
                
            print(f"\nGefundene Entitäten: {len(entities)}")
            
            # Always use the new Restructurer for better Entity IDs
            # Only pass the filtered entities
            filtered_states = []
            for e in entities:
                # Finde den passenden State
                for state in states:
                    if state["entity_id"] == e["entity_id"]:
                        filtered_states.append(state)
                        break
                        
            # Übergebe Filter-Optionen
            skip_reviewed = getattr(self, 'skip_reviewed', False)
            show_reviewed = getattr(self, 'show_reviewed', False)
            mapping = await self.entity_restructurer.analyze_entities(
                filtered_states, 
                skip_reviewed=skip_reviewed,
                show_reviewed=show_reviewed
            )
            
            print(f"Umbenennungen nötig: {len(mapping)}")
            
            if mapping:
                table_data = []
                for old_id, (new_id, friendly_name) in list(mapping.items())[:20]:
                    current_friendly = ""
                    for e in entities:
                        if e["entity_id"] == old_id:
                            current_friendly = e["attributes"].get("friendly_name", "")
                            break
                            
                    table_data.append([
                        old_id, 
                        new_id, 
                        current_friendly,
                        friendly_name  # friendly_name is already the current name
                    ])
                    
                print(f"\n{Fore.YELLOW}Vorschau der Umbenennungen:{Style.RESET_ALL}")
                print(tabulate(table_data, 
                             headers=["Alte Entity ID", "Neue Entity ID", "Aktueller Name", "Neuer Name"],
                             tablefmt="grid"))
                
                if len(mapping) > 20:
                    print(f"\n... und {len(mapping) - 20} weitere Entitäten")
                    
        return mapping
        
    async def check_dependencies(self, entity_ids: List[str]):
        """Prüfe Abhängigkeiten über WebSocket"""
        print(f"\n{Fore.CYAN}=== Prüfe Abhängigkeiten ==={Style.RESET_ALL}")
        
        await self.connect_websocket()
        try:
            # Check only the first 10 for the preview
            sample_ids = entity_ids[:10]
            dependencies = await self.dependency_scanner.scan_all_dependencies(sample_ids)
            
            total_deps = 0
            if dependencies:
                print(f"\n{Fore.YELLOW}Gefundene Abhängigkeiten:{Style.RESET_ALL}")
                for entity_id, refs in dependencies.items():
                    entity_total = sum(len(r) for r in refs.values())
                    if entity_total > 0:
                        total_deps += entity_total
                        print(f"\n{entity_id}:")
                        for ref_type, ref_list in refs.items():
                            if ref_list:
                                print(f"  - {ref_type}: {len(ref_list)} Referenzen")
                                for ref in ref_list[:3]:  # Zeige max 3 Beispiele
                                    print(f"    • {ref}")
                                if len(ref_list) > 3:
                                    print(f"    ... und {len(ref_list) - 3} weitere")
                                    
            print(f"\n{Fore.CYAN}Gesamt: {total_deps} Abhängigkeiten gefunden{Style.RESET_ALL}")
            
            if len(entity_ids) > 10:
                print(f"\n{Fore.YELLOW}Hinweis: Nur die ersten 10 Entitäten wurden geprüft. "
                      f"Bei der Ausführung werden alle {len(entity_ids)} Entitäten berücksichtigt.{Style.RESET_ALL}")
                      
            return dependencies
            
        except Exception as e:
            print(f"{Fore.YELLOW}Warnung: Dependency-Check fehlgeschlagen: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Die WebSocket API unterstützt möglicherweise nicht alle Commands.{Style.RESET_ALL}")
            return {}
        finally:
            await self.disconnect_websocket()
            
    async def rename_entities_with_dependencies(self, mapping: Dict[str, Tuple[str, str]], 
                                               dry_run: bool = True, update_deps: bool = True):
        """Benenne Entitäten um und aktualisiere Abhängigkeiten"""
        if dry_run:
            print(f"\n{Fore.CYAN}=== DRY RUN - Keine echten Änderungen ==={Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}=== LIVE RUN - Führe Umbenennungen durch ==={Style.RESET_ALL}")
            
        self.stats["total"] = len(mapping)
        
        await self.connect_websocket()
        try:
            for old_id, (new_id, friendly_name) in mapping.items():
                try:
                    if dry_run:
                        if old_id != new_id:
                            print(f"\n{Fore.GREEN}✓{Style.RESET_ALL} Würde umbenennen: {old_id} → {new_id}")
                        else:
                            print(f"\n{Fore.BLUE}✓{Style.RESET_ALL} Bereits korrekt: {old_id} (würde maintained Label setzen)")
                        
                        if update_deps and old_id != new_id:
                            try:
                                # Zeige welche Dependencies betroffen wären
                                deps = await self.dependency_scanner.find_entity_references(old_id)
                                total_deps = sum(len(d) for d in deps.values())
                                if total_deps > 0:
                                    print(f"  {Fore.YELLOW}→ Würde {total_deps} Abhängigkeiten aktualisieren{Style.RESET_ALL}")
                            except:
                                pass  # Ignoriere Dependency-Fehler im Dry-Run
                        
                        self.stats["renamed"] += 1
                    else:
                        # Echte Umbenennung
                        if old_id != new_id:
                            print(f"\n{Fore.GREEN}Benenne um:{Style.RESET_ALL} {old_id} → {new_id}")
                            
                            # 1. Entity umbenennen
                            result = await self.entity_registry.rename_entity(old_id, new_id, friendly_name)
                            await self.entity_registry.add_labels(new_id, ["maintained"])
                            self.stats["labels_added"] += 1
                        else:
                            # Entity ID is already correct, only set label
                            print(f"\n{Fore.BLUE}Bereits korrekt:{Style.RESET_ALL} {old_id} (setze maintained Label)")
                            await self.entity_registry.add_labels(old_id, ["maintained"])
                            self.stats["labels_added"] += 1
                            self.stats["skipped"] += 1
                        
                        # 2. Dependencies aktualisieren
                        if update_deps and old_id != new_id:
                            try:
                                print(f"  Aktualisiere Abhängigkeiten...")
                                dep_updates = await self.dependency_scanner.update_entity_references(old_id, new_id)
                                
                                for dep_type, count in dep_updates.items():
                                    if count > 0:
                                        print(f"    ✓ {count} {dep_type} aktualisiert")
                                        self.stats["dependencies_updated"] += count
                            except Exception as e:
                                print(f"  {Fore.YELLOW}Warnung: Konnte Dependencies nicht aktualisieren: {str(e)}{Style.RESET_ALL}")
                        
                        if old_id != new_id:
                            print(f"  {Fore.GREEN}✓ Erfolgreich umbenannt{Style.RESET_ALL}")
                            self.stats["renamed"] += 1
                        else:
                            print(f"  {Fore.GREEN}✓ Label hinzugefügt{Style.RESET_ALL}")
                        
                except Exception as e:
                    print(f"{Fore.RED}✗{Style.RESET_ALL} Fehler bei {old_id}: {str(e)}")
                    self.stats["failed"] += 1
                    
        finally:
            await self.disconnect_websocket()
            
    def print_summary(self):
        print(f"\n{Fore.CYAN}=== Zusammenfassung ==={Style.RESET_ALL}")
        print(f"Gesamt: {self.stats['total']}")
        print(f"{Fore.GREEN}Erfolgreich: {self.stats['renamed']}{Style.RESET_ALL}")
        print(f"{Fore.RED}Fehlgeschlagen: {self.stats['failed']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Übersprungen: {self.stats['skipped']}{Style.RESET_ALL}")
        if self.stats['labels_added'] > 0:
            print(f"Labels hinzugefügt: {self.stats['labels_added']}")
        if self.stats['dependencies_updated'] > 0:
            print(f"{Fore.BLUE}Dependencies aktualisiert: {self.stats['dependencies_updated']}{Style.RESET_ALL}")
            
    async def save_mapping(self, mapping: Dict[str, Tuple[str, str]], filename: str = None):
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"entity_mapping_{timestamp}.json"
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
            
        print(f"\n{Fore.GREEN}Mapping gespeichert in: {filename}{Style.RESET_ALL}")
        
    async def load_mapping(self, filename: str) -> Dict[str, Tuple[str, str]]:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)


async def main():
    parser = argparse.ArgumentParser(description='Home Assistant Entity Renamer - Vollständiges Tool')
    parser.add_argument('--test', action='store_true', help='Teste Verbindung')
    parser.add_argument('--domain', help='Domain filter (z.B. light, sensor)')
    parser.add_argument('--room', help='Raum filter (z.B. wohnzimmer, buro)')
    parser.add_argument('--limit', type=int, help='Maximale Anzahl Entitäten')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Nur Preview, keine Änderungen')
    parser.add_argument('--execute', action='store_true', help='Führe Umbenennungen durch')
    parser.add_argument('--no-update-deps', action='store_true', help='Aktualisiere keine Abhängigkeiten')
    parser.add_argument('--check-deps', action='store_true', help='Prüfe Abhängigkeiten vorab')
    parser.add_argument('--save-mapping', help='Speichere Mapping in Datei')
    parser.add_argument('--load-mapping', help='Lade Mapping aus Datei')
    parser.add_argument('--skip-reviewed', action='store_true', help='Überspringe Entities mit maintained Label')
    parser.add_argument('--show-reviewed', action='store_true', help='Zeige nur bereits bearbeitete Entities (mit maintained Label)')
    
    args = parser.parse_args()
    
    load_dotenv()
    
    base_url = os.getenv('HA_URL')
    token = os.getenv('HA_TOKEN')
    
    if not base_url or not token:
        print(f"{Fore.RED}Fehler: HA_URL und HA_TOKEN müssen in .env definiert sein{Style.RESET_ALL}")
        sys.exit(1)
        
    renamer = EntityRenamer(base_url, token)
    renamer.skip_reviewed = args.skip_reviewed
    renamer.show_reviewed = args.show_reviewed
    
    try:
        # Verbindungstest
        if args.test:
            success = await renamer.test_connection()
            sys.exit(0 if success else 1)
            
        # Mapping laden oder analysieren
        if args.load_mapping:
            mapping = await renamer.load_mapping(args.load_mapping)
            print(f"Mapping geladen: {len(mapping)} Entitäten")
        else:
            mapping = await renamer.analyze_entities(
                domain=args.domain,
                room=args.room,
                limit=args.limit
            )
            
        if not mapping:
            print(f"\n{Fore.YELLOW}Keine Entitäten zum Umbenennen gefunden{Style.RESET_ALL}")
            sys.exit(0)
            
        # Save mapping if desired
        if args.save_mapping:
            await renamer.save_mapping(mapping, args.save_mapping)
            
        # Check dependencies if desired
        if args.check_deps:
            await renamer.check_dependencies(list(mapping.keys()))
            
        # Execute renaming
        if args.execute:
            confirm = input(f"\n{Fore.YELLOW}Wirklich {len(mapping)} Entitäten umbenennen "
                          f"{'und Dependencies aktualisieren' if not args.no_update_deps else ''}? (y/N): {Style.RESET_ALL}")
            if confirm.lower() == 'y':
                await renamer.rename_entities_with_dependencies(
                    mapping, 
                    dry_run=False,
                    update_deps=not args.no_update_deps
                )
            else:
                print("Abgebrochen.")
        else:
            await renamer.rename_entities_with_dependencies(
                mapping, 
                dry_run=True,
                update_deps=not args.no_update_deps
            )
            if not args.load_mapping:  # Show hint only if not loaded from file
                print(f"\n{Fore.YELLOW}Nutze --execute um die Änderungen durchzuführen{Style.RESET_ALL}")
            
        renamer.print_summary()
        
    except Exception as e:
        print(f"{Fore.RED}Fehler: {str(e)}{Style.RESET_ALL}")
        logger.exception("Unerwarteter Fehler")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
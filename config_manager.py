"""
Config Manager Module

This module handles the loading and saving of service provider settings
to a local JSON configuration file.
"""

import json
import os
import sys
from typing import Dict, Any, Optional


def _get_config_path(filename: str = "config.json") -> str:
    """
    Gibt einen stabilen, absoluten Pfad zur config.json zurück.
    Funktioniert sowohl normal als auch als PyInstaller-.exe.
    
    Speicherort:
      - Normal:      neben der config_manager.py
      - Als .exe:    %USERPROFILE%/InvoiceMaster/config.json
                     (da _MEIPASS ein temporäres Verzeichnis ist)
    """
    if hasattr(sys, "_MEIPASS"):
        # Als gebündelte .exe → AppData-ähnlicher Ordner im Benutzerverzeichnis
        base = os.path.join(os.path.expanduser("~"), "InvoiceMaster")
    else:
        # Normaler Betrieb → neben dieser Datei
        base = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(base, exist_ok=True)
    return os.path.join(base, filename)


class ConfigManager:
    """Manages configuration settings for the service provider profile."""

    def __init__(self, config_file: str = None):
        """
        Initialize the ConfigManager.

        Args:
            config_file: Optionaler absoluter Pfad zur config.json.
                         Wird keiner übergeben, wird automatisch ein
                         stabiler Pfad ermittelt.
        """
        self.config_file = config_file if config_file else _get_config_path()
        self.default_config = {
            "service_provider": {
                "company_name": "",
                "owner": "",
                "contact_person": "",
                "phone": "",
                "email": "",
                "address": "",
                "tax_id": "",
                "tax_number": "",
                "creditor_reference": "",
                "bank": "",
                "bank_account": "",
                "bank_bic": "",
                "logo_path": "",
            }
        }
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from the JSON file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                return self._merge_with_defaults(loaded_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ConfigManager] Fehler beim Laden: {e}")
        return self.default_config.copy()

    def _merge_with_defaults(self, loaded_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults so all keys always exist."""
        import copy
        merged = copy.deepcopy(self.default_config)
        for key, value in loaded_config.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key].update(value)
            else:
                merged[key] = value
        return merged

    def get_service_provider(self) -> Dict[str, str]:
        """Get service provider settings."""
        return self.config.get("service_provider", {})

    def set_service_provider(self, data: Dict[str, str]) -> None:
        """Update and persist service provider settings."""
        if "service_provider" not in self.config:
            self.config["service_provider"] = {}
        for key, value in data.items():
            self.config["service_provider"][key] = value
        self._save_config()

    def _save_config(self) -> None:
        """Save the current configuration to the JSON file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"[ConfigManager] Fehler beim Speichern: {e}")

    def get_logo_path(self) -> str:
        """Get the path to the service provider logo."""
        return self.config.get("service_provider", {}).get("logo_path", "")

    def set_logo_path(self, path: str) -> None:
        """Set the path to the service provider logo."""
        self.config.setdefault("service_provider", {})["logo_path"] = path
        self._save_config()

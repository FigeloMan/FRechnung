import json
import os
import sys
import keyring
from typing import Dict, Any
from cryptography.fernet import Fernet

def _get_config_path(filename: str = "user_profile.dat") -> str:
    """Nutzt eine unscheinbare Dateiendung wie .dat statt .json"""
    if hasattr(sys, "_MEIPASS"):
        base = os.path.join(os.path.expanduser("~"), "FRechnung")
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(base, exist_ok=True)
    return os.path.join(base, filename)

class ConfigManager:
    def __init__(self, config_file: str = None):
        self.config_file = config_file if config_file else _get_config_path()
        self.service_name = "FRechnung_App"
        self.key_name = "encryption_key"
        
        # Fernet Instanz mit Key aus dem Windows Tresor
        self.fernet = Fernet(self._get_or_create_key())
        
        self.default_config = {
            "service_provider": {
                "company_name": "", "owner": "", "contact_person": "",
                "phone": "", "email": "", "address": "", "tax_id": "",
                "tax_number": "", "creditor_reference": "", "bank": "",
                "bank_account": "", "bank_bic": "", "logo_path": "",
            }
        }
        self.config = self._load_config()

    def _get_or_create_key(self) -> bytes:
        stored_key = keyring.get_password(self.service_name, self.key_name)
        if stored_key is None:
            new_key = Fernet.generate_key().decode('utf-8')
            keyring.set_password(self.service_name, self.key_name, new_key)
            return new_key.encode('utf-8')
        return stored_key.encode('utf-8')

    def _load_config(self) -> Dict[str, Any]:
        """Lädt die unkenntliche .dat Datei und entschlüsselt sie."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "rb") as f:
                    # Wir lesen die kryptischen Binärdaten
                    encrypted_data = f.read()
                
                if not encrypted_data:
                    return self.default_config.copy()

                # Entschlüsseln und von Byte zu String (JSON) umwandeln
                decrypted_data = self.fernet.decrypt(encrypted_data)
                return self._merge_with_defaults(json.loads(decrypted_data.decode("utf-8")))
            except Exception:
                # Falls Datei beschädigt oder Key falsch
                return self.default_config.copy()
        return self.default_config.copy()

    def _save_config(self) -> None:
        """Verwandelt JSON in verschlüsselten Binärcode und speichert als .dat"""
        try:
            # Kompakter JSON-String ohne Einrückungen (spart Platz und verschleiert Struktur)
            json_str = json.dumps(self.config, ensure_ascii=False)
            encrypted_data = self.fernet.encrypt(json_str.encode("utf-8"))
            
            with open(self.config_file, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"Fehler: {e}")

    def _merge_with_defaults(self, loaded_config: Dict[str, Any]) -> Dict[str, Any]:
        import copy
        merged = copy.deepcopy(self.default_config)
        for key, value in loaded_config.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key].update(value)
            else:
                merged[key] = value
        return merged

    # --- Die gewohnten Getter/Setter ---
    def get_service_provider(self) -> Dict[str, str]:
        return self.config.get("service_provider", {})

    def set_service_provider(self, data: Dict[str, str]) -> None:
        if "service_provider" not in self.config:
            self.config["service_provider"] = {}
        self.config["service_provider"].update(data)
        self._save_config()
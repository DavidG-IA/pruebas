"""Cargador de configuración"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
import logging


class ConfigLoader:
    """
    Cargador de configuración desde múltiples fuentes.

    Orden de prioridad (mayor a menor):
    1. Variables de entorno
    2. Archivo de configuración
    3. Valores por defecto
    """

    DEFAULT_CONFIG = {
        # General
        "log_level": "INFO",
        "cache_enabled": True,
        "cache_dir": ".cache/marketplace_checker",

        # Rate limiting
        "rate_limit_delay": 1.0,

        # Amazon
        "amazon_region": "amazon",
        "amazon_api_key": None,
        "amazon_affiliate_tag": None,

        # MercadoLibre
        "mercadolibre_country": "MLM",
        "mercadolibre_token": None,

        # eBay
        "ebay_site": "US",
        "ebay_app_id": None,
        "ebay_cert_id": None,

        # Alertas
        "alerts_storage_path": ".data/alerts",

        # Email
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "email_from": None,
        "email_password": None,
        "email_to": [],

        # Telegram
        "telegram_token": None,
        "telegram_chat_id": None,

        # Productos a monitorear (ruta al archivo)
        "products_file": "products.json",
    }

    ENV_PREFIX = "MPC_"

    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa el cargador.

        Args:
            config_path: Ruta al archivo de configuración JSON
        """
        self.logger = logging.getLogger("config_loader")
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()

        # Cargar desde archivo si existe
        if config_path:
            self._load_from_file(config_path)
        else:
            # Buscar archivo por defecto
            default_paths = [
                "config.json",
                "marketplace_checker.json",
                os.path.expanduser("~/.config/marketplace_checker/config.json"),
            ]
            for path in default_paths:
                if os.path.exists(path):
                    self._load_from_file(path)
                    break

        # Sobrescribir con variables de entorno
        self._load_from_env()

    def _load_from_file(self, path: str):
        """Carga configuración desde archivo JSON"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)

            self.config.update(file_config)
            self.logger.info(f"Configuración cargada desde: {path}")

        except FileNotFoundError:
            self.logger.warning(f"Archivo de configuración no encontrado: {path}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parseando configuración JSON: {e}")
        except Exception as e:
            self.logger.error(f"Error cargando configuración: {e}")

    def _load_from_env(self):
        """Carga configuración desde variables de entorno"""
        for key in self.DEFAULT_CONFIG.keys():
            env_key = f"{self.ENV_PREFIX}{key.upper()}"
            env_value = os.environ.get(env_key)

            if env_value is not None:
                # Convertir tipos
                default_value = self.DEFAULT_CONFIG[key]

                if isinstance(default_value, bool):
                    self.config[key] = env_value.lower() in ('true', '1', 'yes')
                elif isinstance(default_value, int):
                    self.config[key] = int(env_value)
                elif isinstance(default_value, float):
                    self.config[key] = float(env_value)
                elif isinstance(default_value, list):
                    self.config[key] = env_value.split(',')
                else:
                    self.config[key] = env_value

                self.logger.debug(f"Configuración desde env: {key}")

    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Establece un valor de configuración"""
        self.config[key] = value

    def get_all(self) -> Dict[str, Any]:
        """Obtiene toda la configuración"""
        return self.config.copy()

    def save(self, path: str):
        """Guarda la configuración a un archivo"""
        # No guardar valores None o sensibles
        save_config = {
            k: v for k, v in self.config.items()
            if v is not None and 'password' not in k.lower() and 'token' not in k.lower()
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(save_config, f, indent=2)

        self.logger.info(f"Configuración guardada en: {path}")

    def get_checker_config(self) -> Dict[str, Any]:
        """Obtiene configuración específica para los checkers"""
        return {
            "amazon_api_key": self.get("amazon_api_key"),
            "affiliate_tag": self.get("amazon_affiliate_tag"),
            "mercadolibre_token": self.get("mercadolibre_token"),
            "ebay_app_id": self.get("ebay_app_id"),
            "ebay_cert_id": self.get("ebay_cert_id"),
            "rate_limit_delay": self.get("rate_limit_delay"),
        }

    def get_alert_config(self) -> Dict[str, Any]:
        """Obtiene configuración específica para alertas"""
        return {
            "smtp_server": self.get("smtp_server"),
            "smtp_port": self.get("smtp_port"),
            "email_from": self.get("email_from"),
            "email_password": self.get("email_password"),
            "email_to": self.get("email_to"),
            "telegram_token": self.get("telegram_token"),
            "telegram_chat_id": self.get("telegram_chat_id"),
        }

    @staticmethod
    def create_sample_config(path: str = "config.sample.json"):
        """Crea un archivo de configuración de ejemplo"""
        sample = {
            "log_level": "INFO",
            "cache_enabled": True,
            "rate_limit_delay": 1.0,

            "amazon_region": "amazon",
            "amazon_api_key": "YOUR_AMAZON_API_KEY",
            "amazon_affiliate_tag": "your-affiliate-tag",

            "mercadolibre_country": "MLM",
            "mercadolibre_token": "YOUR_MERCADOLIBRE_TOKEN",

            "ebay_site": "US",
            "ebay_app_id": "YOUR_EBAY_APP_ID",

            "email_from": "your-email@gmail.com",
            "email_to": ["recipient@example.com"],

            "telegram_token": "YOUR_TELEGRAM_BOT_TOKEN",
            "telegram_chat_id": "YOUR_CHAT_ID",

            "products_file": "products.json"
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(sample, f, indent=2)

        return path

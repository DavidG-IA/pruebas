"""Checker de precios para MercadoLibre"""

from typing import List, Optional
import random
from datetime import datetime

from .base_checker import BasePriceChecker
from ..models.product import Product
from ..models.criteria import PriceCriteria
from ..models.price_result import MarketplacePrice, Marketplace


class MercadoLibrePriceChecker(BasePriceChecker):
    """
    Verificador de precios para MercadoLibre.

    Soporta múltiples países de MercadoLibre.

    Nota: Esta implementación incluye datos simulados para demostración.
    Para uso en producción, se debe integrar con:
    - MercadoLibre API (https://developers.mercadolibre.com/)
    """

    COUNTRY_SITES = {
        "MLA": {"domain": "mercadolibre.com.ar", "currency": "ARS", "name": "Argentina"},
        "MLB": {"domain": "mercadolibre.com.br", "currency": "BRL", "name": "Brasil"},
        "MLC": {"domain": "mercadolibre.cl", "currency": "CLP", "name": "Chile"},
        "MCO": {"domain": "mercadolibre.com.co", "currency": "COP", "name": "Colombia"},
        "MLM": {"domain": "mercadolibre.com.mx", "currency": "MXN", "name": "México"},
        "MLU": {"domain": "mercadolibre.com.uy", "currency": "UYU", "name": "Uruguay"},
        "MPE": {"domain": "mercadolibre.com.pe", "currency": "PEN", "name": "Perú"},
        "MLV": {"domain": "mercadolibre.com.ve", "currency": "VES", "name": "Venezuela"},
    }

    def __init__(self, country_code: str = "MLM", config: Optional[dict] = None):
        """
        Inicializa el checker de MercadoLibre.

        Args:
            country_code: Código del país (MLA, MLB, MLC, MCO, MLM, etc.)
            config: Configuración con API keys si disponibles
        """
        super().__init__(Marketplace.MERCADOLIBRE, config)

        self.country_code = country_code
        site_info = self.COUNTRY_SITES.get(country_code, self.COUNTRY_SITES["MLM"])
        self.domain = site_info["domain"]
        self.currency = site_info["currency"]
        self.country_name = site_info["name"]

        self.access_token = self.config.get("mercadolibre_token")
        self.api_base = f"https://api.mercadolibre.com/sites/{country_code}"

    def search(self, product: Product, criteria: Optional[PriceCriteria] = None) -> List[MarketplacePrice]:
        """
        Busca un producto en MercadoLibre.

        Args:
            product: Producto a buscar
            criteria: Criterios de filtrado

        Returns:
            Lista de precios encontrados
        """
        self._apply_rate_limit()
        self.logger.info(f"Buscando '{product.name}' en MercadoLibre ({self.country_name})")

        query = product.get_search_query()

        # En producción: llamar a API de MercadoLibre
        # Demo: datos simulados
        results = self._simulate_search(query, product)

        return self._filter_results(results, criteria)

    def get_product_details(self, url: str) -> Optional[MarketplacePrice]:
        """
        Obtiene detalles de un producto por URL.

        Args:
            url: URL del producto en MercadoLibre

        Returns:
            MarketplacePrice con detalles
        """
        self._apply_rate_limit()
        self.logger.info(f"Obteniendo detalles de: {url}")

        item_id = self._extract_item_id(url)
        if item_id:
            return self._get_by_item_id(item_id)

        return None

    def _get_by_item_id(self, item_id: str) -> Optional[MarketplacePrice]:
        """Obtiene producto por ID de MercadoLibre"""
        # En producción: GET https://api.mercadolibre.com/items/{item_id}
        # Demo: datos simulados

        has_free_shipping = random.random() > 0.4
        is_full = random.random() > 0.6  # Mercado Libre Full

        return MarketplacePrice(
            marketplace=self.marketplace,
            price=round(random.uniform(100, 5000), 2),
            currency=self.currency,
            shipping_cost=0 if has_free_shipping else round(random.uniform(50, 300), 2),
            url=f"https://{self.domain}/item/{item_id}",
            seller_name=f"Vendedor_{random.randint(1000, 9999)}",
            seller_rating=round(random.uniform(4.0, 5.0), 1),
            seller_reviews=random.randint(50, 2000),
            is_prime=is_full,  # Usando is_prime para Full
            is_official_store=random.random() > 0.8,
            condition="new",
            stock_status="in_stock",
            timestamp=datetime.now(),
            title=f"Producto {item_id}",
        )

    def _simulate_search(self, query: str, product: Product) -> List[MarketplacePrice]:
        """
        Simula resultados de búsqueda para demostración.
        """
        results = []
        num_results = random.randint(5, 12)

        # Ajustar precio base según moneda
        currency_multipliers = {
            "ARS": 1000,
            "BRL": 5,
            "CLP": 800,
            "COP": 4000,
            "MXN": 20,
            "PEN": 4,
            "UYU": 40,
        }

        multiplier = currency_multipliers.get(self.currency, 1)
        base_price = (product.max_price or random.uniform(50, 200)) * multiplier

        for i in range(num_results):
            price_variation = random.uniform(0.6, 1.4)
            price = round(base_price * price_variation, 2)

            has_free_shipping = random.random() > 0.4
            is_full = has_free_shipping and random.random() > 0.5
            is_official = random.random() > 0.85

            # Generar ID estilo MercadoLibre
            item_id = f"{self.country_code}{random.randint(100000000, 999999999)}"

            result = MarketplacePrice(
                marketplace=self.marketplace,
                price=price,
                currency=self.currency,
                shipping_cost=0 if has_free_shipping else round(random.uniform(50, 200) * (multiplier / 20), 2),
                url=f"https://{self.domain}/{item_id}",
                seller_name="Tienda Oficial" if is_official else f"Vendedor_{random.randint(1000, 9999)}",
                seller_rating=round(random.uniform(4.0, 5.0), 1) if random.random() > 0.1 else None,
                seller_reviews=random.randint(10, 3000),
                is_prime=is_full,
                is_official_store=is_official,
                condition="new" if random.random() > 0.15 else "used",
                stock_status="in_stock" if random.random() > 0.05 else "last_units",
                timestamp=datetime.now(),
                title=f"{product.brand or ''} {product.name} - Opción {i+1}".strip(),
            )
            results.append(result)

        return results

    def _extract_item_id(self, url: str) -> Optional[str]:
        """Extrae ID del item de una URL de MercadoLibre"""
        import re

        # Patrones de URL de MercadoLibre
        patterns = [
            r'/(ML[A-Z])-?(\d+)',  # MLA123456789 o MLA-123456789
            r'/p/(ML[A-Z]\d+)',     # /p/MLA123456789
            r'item_id=(ML[A-Z]\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1)}{match.group(2)}"
                return match.group(1).upper()

        return None

    def _build_search_url(self, query: str) -> str:
        """Construye URL de búsqueda en MercadoLibre"""
        from urllib.parse import quote_plus
        return f"https://{self.domain}/search?q={quote_plus(query)}"

    def get_categories(self) -> List[dict]:
        """Obtiene categorías disponibles (demo)"""
        return [
            {"id": "MLA1051", "name": "Celulares y Teléfonos"},
            {"id": "MLA1648", "name": "Computación"},
            {"id": "MLA1144", "name": "Consolas y Videojuegos"},
            {"id": "MLA1000", "name": "Electrónica, Audio y Video"},
            {"id": "MLA1574", "name": "Hogar, Muebles y Jardín"},
        ]

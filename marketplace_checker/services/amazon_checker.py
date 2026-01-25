"""Checker de precios para Amazon"""

from typing import List, Optional
import random
from datetime import datetime

from .base_checker import BasePriceChecker
from ..models.product import Product
from ..models.criteria import PriceCriteria
from ..models.price_result import MarketplacePrice, Marketplace


class AmazonPriceChecker(BasePriceChecker):
    """
    Verificador de precios para Amazon.

    Soporta múltiples regiones de Amazon (US, ES, MX, etc.)

    Nota: Esta implementación incluye datos simulados para demostración.
    Para uso en producción, se debe integrar con:
    - Amazon Product Advertising API
    - Keepa API
    - O implementar web scraping (respetando ToS)
    """

    AMAZON_DOMAINS = {
        "amazon": "amazon.com",
        "amazon_es": "amazon.es",
        "amazon_mx": "amazon.com.mx",
        "amazon_de": "amazon.de",
        "amazon_uk": "amazon.co.uk",
        "amazon_fr": "amazon.fr",
        "amazon_it": "amazon.it",
    }

    CURRENCY_MAP = {
        "amazon": "USD",
        "amazon_es": "EUR",
        "amazon_mx": "MXN",
        "amazon_de": "EUR",
        "amazon_uk": "GBP",
        "amazon_fr": "EUR",
        "amazon_it": "EUR",
    }

    def __init__(self, region: str = "amazon", config: Optional[dict] = None):
        """
        Inicializa el checker de Amazon.

        Args:
            region: Región de Amazon (amazon, amazon_es, amazon_mx, etc.)
            config: Configuración con API keys si disponibles
        """
        marketplace = Marketplace(region) if region in [m.value for m in Marketplace] else Marketplace.AMAZON
        super().__init__(marketplace, config)

        self.region = region
        self.domain = self.AMAZON_DOMAINS.get(region, "amazon.com")
        self.currency = self.CURRENCY_MAP.get(region, "USD")
        self.api_key = self.config.get("amazon_api_key")
        self.affiliate_tag = self.config.get("affiliate_tag")

    def search(self, product: Product, criteria: Optional[PriceCriteria] = None) -> List[MarketplacePrice]:
        """
        Busca un producto en Amazon.

        Args:
            product: Producto a buscar
            criteria: Criterios de filtrado

        Returns:
            Lista de precios encontrados
        """
        self._apply_rate_limit()
        self.logger.info(f"Buscando '{product.name}' en Amazon ({self.region})")

        query = product.get_search_query()

        # Si hay ASIN, búsqueda directa
        if product.asin:
            result = self._get_by_asin(product.asin)
            if result:
                results = [result]
            else:
                results = self._simulate_search(query, product)
        else:
            # Búsqueda por keywords (simulada para demo)
            results = self._simulate_search(query, product)

        # Aplicar filtros
        return self._filter_results(results, criteria)

    def get_product_details(self, url: str) -> Optional[MarketplacePrice]:
        """
        Obtiene detalles de un producto por URL.

        Args:
            url: URL del producto en Amazon

        Returns:
            MarketplacePrice con detalles
        """
        self._apply_rate_limit()
        self.logger.info(f"Obteniendo detalles de: {url}")

        # Extraer ASIN de la URL
        asin = self._extract_asin(url)
        if asin:
            return self._get_by_asin(asin)

        return None

    def _get_by_asin(self, asin: str) -> Optional[MarketplacePrice]:
        """Obtiene producto por ASIN"""
        # En producción: llamar a Amazon PA API o scraping
        # Demo: retornar datos simulados
        return MarketplacePrice(
            marketplace=self.marketplace,
            price=round(random.uniform(20, 500), 2),
            currency=self.currency,
            shipping_cost=0 if random.random() > 0.3 else round(random.uniform(3, 15), 2),
            url=f"https://{self.domain}/dp/{asin}",
            seller_name="Amazon" if random.random() > 0.5 else "Third Party Seller",
            seller_rating=round(random.uniform(4.0, 5.0), 1),
            seller_reviews=random.randint(100, 10000),
            is_prime=random.random() > 0.3,
            is_official_store=random.random() > 0.7,
            condition="new",
            stock_status="in_stock" if random.random() > 0.1 else "low_stock",
            timestamp=datetime.now(),
            title=f"Product {asin}",
        )

    def _simulate_search(self, query: str, product: Product) -> List[MarketplacePrice]:
        """
        Simula resultados de búsqueda para demostración.

        En producción, esto sería reemplazado por llamadas a API o scraping.
        """
        results = []
        num_results = random.randint(3, 8)

        base_price = product.max_price if product.max_price else random.uniform(50, 300)

        for i in range(num_results):
            # Variar precio alrededor del base
            price_variation = random.uniform(0.7, 1.3)
            price = round(base_price * price_variation, 2)

            is_prime = random.random() > 0.4
            is_amazon_seller = random.random() > 0.6

            result = MarketplacePrice(
                marketplace=self.marketplace,
                price=price,
                currency=self.currency,
                shipping_cost=0 if is_prime else round(random.uniform(3, 15), 2),
                url=f"https://{self.domain}/dp/B0{random.randint(10000000, 99999999)}",
                seller_name="Amazon" if is_amazon_seller else f"Seller_{random.randint(1000, 9999)}",
                seller_rating=round(random.uniform(3.5, 5.0), 1),
                seller_reviews=random.randint(50, 5000),
                is_prime=is_prime,
                is_official_store=is_amazon_seller and random.random() > 0.5,
                condition="new" if random.random() > 0.2 else random.choice(["used", "refurbished"]),
                stock_status="in_stock",
                timestamp=datetime.now(),
                title=f"{product.brand or ''} {product.name} {product.model or ''} - Variant {i+1}".strip(),
            )
            results.append(result)

        return results

    def _extract_asin(self, url: str) -> Optional[str]:
        """Extrae ASIN de una URL de Amazon"""
        import re

        # Patrones comunes de URL de Amazon
        patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
            r'/product/([A-Z0-9]{10})',
            r'asin=([A-Z0-9]{10})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1).upper()

        return None

    def _build_search_url(self, query: str) -> str:
        """Construye URL de búsqueda en Amazon"""
        from urllib.parse import quote_plus
        return f"https://{self.domain}/s?k={quote_plus(query)}"

    def is_available(self) -> bool:
        """Verifica si el checker está disponible"""
        # Para demo siempre disponible
        # En producción verificar API keys, conexión, etc.
        return True

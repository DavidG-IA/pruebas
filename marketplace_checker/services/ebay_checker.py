"""Checker de precios para eBay"""

from typing import List, Optional
import random
from datetime import datetime

from .base_checker import BasePriceChecker
from ..models.product import Product
from ..models.criteria import PriceCriteria
from ..models.price_result import MarketplacePrice, Marketplace


class EbayPriceChecker(BasePriceChecker):
    """
    Verificador de precios para eBay.

    Nota: Esta implementación incluye datos simulados para demostración.
    Para uso en producción, se debe integrar con:
    - eBay Browse API
    - eBay Finding API
    """

    EBAY_SITES = {
        "US": {"domain": "ebay.com", "currency": "USD"},
        "UK": {"domain": "ebay.co.uk", "currency": "GBP"},
        "DE": {"domain": "ebay.de", "currency": "EUR"},
        "ES": {"domain": "ebay.es", "currency": "EUR"},
        "FR": {"domain": "ebay.fr", "currency": "EUR"},
        "IT": {"domain": "ebay.it", "currency": "EUR"},
        "AU": {"domain": "ebay.com.au", "currency": "AUD"},
    }

    def __init__(self, site: str = "US", config: Optional[dict] = None):
        """
        Inicializa el checker de eBay.

        Args:
            site: Código del sitio (US, UK, DE, ES, etc.)
            config: Configuración con API keys
        """
        super().__init__(Marketplace.EBAY, config)

        self.site = site
        site_info = self.EBAY_SITES.get(site, self.EBAY_SITES["US"])
        self.domain = site_info["domain"]
        self.currency = site_info["currency"]

        self.app_id = self.config.get("ebay_app_id")
        self.cert_id = self.config.get("ebay_cert_id")

    def search(self, product: Product, criteria: Optional[PriceCriteria] = None) -> List[MarketplacePrice]:
        """
        Busca un producto en eBay.

        Args:
            product: Producto a buscar
            criteria: Criterios de filtrado

        Returns:
            Lista de precios encontrados
        """
        self._apply_rate_limit()
        self.logger.info(f"Buscando '{product.name}' en eBay ({self.site})")

        query = product.get_search_query()

        # Si hay EAN/UPC, búsqueda por código
        if product.ean:
            results = self._search_by_upc(product.ean)
        else:
            results = self._simulate_search(query, product)

        return self._filter_results(results, criteria)

    def get_product_details(self, url: str) -> Optional[MarketplacePrice]:
        """
        Obtiene detalles de un producto por URL.

        Args:
            url: URL del producto en eBay

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
        """Obtiene producto por ID de eBay"""
        # En producción: llamar a eBay API
        # Demo: datos simulados

        is_auction = random.random() > 0.7
        has_free_shipping = random.random() > 0.5

        return MarketplacePrice(
            marketplace=self.marketplace,
            price=round(random.uniform(20, 400), 2),
            currency=self.currency,
            shipping_cost=0 if has_free_shipping else round(random.uniform(5, 25), 2),
            url=f"https://{self.domain}/itm/{item_id}",
            seller_name=f"ebay_seller_{random.randint(100, 999)}",
            seller_rating=round(random.uniform(95, 100), 1),  # eBay usa porcentaje
            seller_reviews=random.randint(100, 10000),
            is_prime=False,
            is_official_store=random.random() > 0.9,
            condition=random.choice(["new", "used", "refurbished"]),
            stock_status="auction" if is_auction else "in_stock",
            timestamp=datetime.now(),
            title=f"eBay Item {item_id}",
        )

    def _search_by_upc(self, upc: str) -> List[MarketplacePrice]:
        """Busca por código UPC/EAN"""
        # En producción: usar parámetro productId.type=UPC en API
        return self._simulate_search(upc, Product(name=upc))

    def _simulate_search(self, query: str, product: Product) -> List[MarketplacePrice]:
        """
        Simula resultados de búsqueda para demostración.
        """
        results = []
        num_results = random.randint(4, 10)

        base_price = product.max_price if product.max_price else random.uniform(30, 250)

        for i in range(num_results):
            price_variation = random.uniform(0.5, 1.5)
            price = round(base_price * price_variation, 2)

            is_auction = random.random() > 0.75
            has_free_shipping = random.random() > 0.4
            condition = random.choices(
                ["new", "used", "refurbished"],
                weights=[0.5, 0.35, 0.15]
            )[0]

            item_id = random.randint(100000000000, 999999999999)

            result = MarketplacePrice(
                marketplace=self.marketplace,
                price=price,
                currency=self.currency,
                shipping_cost=0 if has_free_shipping else round(random.uniform(5, 30), 2),
                url=f"https://{self.domain}/itm/{item_id}",
                seller_name=f"seller_{random.randint(100, 9999)}",
                seller_rating=round(random.uniform(90, 100), 1),
                seller_reviews=random.randint(10, 5000),
                is_prime=False,
                is_official_store=random.random() > 0.92,
                condition=condition,
                stock_status="auction" if is_auction else "in_stock",
                timestamp=datetime.now(),
                title=f"{product.brand or ''} {product.name} - {condition.title()}".strip(),
            )
            results.append(result)

        return results

    def _extract_item_id(self, url: str) -> Optional[str]:
        """Extrae ID del item de una URL de eBay"""
        import re

        patterns = [
            r'/itm/(\d+)',
            r'/itm/[^/]+/(\d+)',
            r'item=(\d+)',
            r'ViewItem[^?]*\?.*item=(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _build_search_url(self, query: str) -> str:
        """Construye URL de búsqueda en eBay"""
        from urllib.parse import quote_plus
        return f"https://{self.domain}/sch/i.html?_nkw={quote_plus(query)}"

    def get_trending_deals(self) -> List[MarketplacePrice]:
        """Obtiene ofertas trending (demo)"""
        results = []
        for i in range(5):
            results.append(MarketplacePrice(
                marketplace=self.marketplace,
                price=round(random.uniform(10, 100), 2),
                currency=self.currency,
                shipping_cost=0,
                url=f"https://{self.domain}/itm/{random.randint(100000000000, 999999999999)}",
                seller_name="Top Rated Seller",
                seller_rating=99.5,
                seller_reviews=random.randint(1000, 50000),
                is_prime=False,
                is_official_store=True,
                condition="new",
                stock_status="in_stock",
                timestamp=datetime.now(),
                title=f"Trending Deal #{i+1}",
            ))
        return results

"""Clase base abstracta para checkers de precio"""

from abc import ABC, abstractmethod
from typing import List, Optional
import logging
import time
import random

from ..models.product import Product
from ..models.criteria import PriceCriteria
from ..models.price_result import MarketplacePrice, Marketplace


class BasePriceChecker(ABC):
    """
    Clase base abstracta para implementar checkers de precio de diferentes marketplaces.

    Subclases deben implementar:
    - search(): Busca productos y retorna precios
    - get_product_details(): Obtiene detalles de un producto específico
    """

    def __init__(self, marketplace: Marketplace, config: Optional[dict] = None):
        """
        Inicializa el checker.

        Args:
            marketplace: Marketplace que maneja este checker
            config: Configuración específica (API keys, etc.)
        """
        self.marketplace = marketplace
        self.config = config or {}
        self.logger = logging.getLogger(f"checker.{marketplace.value}")
        self._rate_limit_delay = self.config.get("rate_limit_delay", 1.0)
        self._last_request_time = 0

    @abstractmethod
    def search(self, product: Product, criteria: Optional[PriceCriteria] = None) -> List[MarketplacePrice]:
        """
        Busca un producto y retorna lista de precios encontrados.

        Args:
            product: Producto a buscar
            criteria: Criterios de filtrado opcionales

        Returns:
            Lista de MarketplacePrice con resultados
        """
        pass

    @abstractmethod
    def get_product_details(self, url: str) -> Optional[MarketplacePrice]:
        """
        Obtiene detalles de precio de un producto específico por URL.

        Args:
            url: URL del producto en el marketplace

        Returns:
            MarketplacePrice con detalles o None si no se encuentra
        """
        pass

    def _apply_rate_limit(self):
        """Aplica rate limiting entre requests"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._rate_limit_delay:
            sleep_time = self._rate_limit_delay - elapsed
            # Agregar jitter aleatorio para evitar patrones
            sleep_time += random.uniform(0, 0.5)
            time.sleep(sleep_time)
        self._last_request_time = time.time()

    def _filter_results(self, prices: List[MarketplacePrice],
                       criteria: Optional[PriceCriteria]) -> List[MarketplacePrice]:
        """
        Filtra resultados según criterios.

        Args:
            prices: Lista de precios a filtrar
            criteria: Criterios de filtrado

        Returns:
            Lista filtrada de precios
        """
        if not criteria:
            return prices

        filtered = []
        for price in prices:
            # Filtrar por precio
            if not criteria.matches_price(price.price, price.shipping_cost):
                continue

            # Filtrar por envío
            if not criteria.matches_shipping(price.shipping_cost):
                continue

            # Filtrar por vendedor
            rating = price.seller_rating or 0
            reviews = price.seller_reviews or 0
            if not criteria.matches_seller(rating, reviews, price.is_official_store):
                continue

            # Filtrar por condición
            if criteria.condition.value != "any":
                if price.condition.lower() != criteria.condition.value:
                    continue

            # Filtrar por Prime
            if criteria.prime_only and not price.is_prime:
                continue

            # Filtrar por keywords excluidas
            if criteria.exclude_keywords and price.title:
                title_lower = price.title.lower()
                if any(kw.lower() in title_lower for kw in criteria.exclude_keywords):
                    continue

            filtered.append(price)

        return filtered

    def _build_search_url(self, query: str) -> str:
        """Construye URL de búsqueda (a implementar por subclases)"""
        raise NotImplementedError

    def _parse_search_results(self, html: str) -> List[MarketplacePrice]:
        """Parsea resultados HTML (a implementar por subclases)"""
        raise NotImplementedError

    def is_available(self) -> bool:
        """Verifica si el checker está disponible/configurado"""
        return True

    def get_marketplace_name(self) -> str:
        """Retorna nombre del marketplace"""
        return self.marketplace.value.replace("_", " ").title()

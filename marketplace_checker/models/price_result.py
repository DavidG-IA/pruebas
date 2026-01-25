"""Resultados de verificación de precios"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Marketplace(Enum):
    """Marketplaces soportados"""
    AMAZON = "amazon"
    AMAZON_ES = "amazon_es"
    AMAZON_MX = "amazon_mx"
    MERCADOLIBRE = "mercadolibre"
    EBAY = "ebay"
    ALIEXPRESS = "aliexpress"
    WALMART = "walmart"
    BESTBUY = "bestbuy"
    CUSTOM = "custom"


@dataclass
class MarketplacePrice:
    """
    Precio de un producto en un marketplace específico.

    Attributes:
        marketplace: Marketplace de origen
        price: Precio del producto
        currency: Moneda (USD, EUR, MXN, etc.)
        shipping_cost: Costo de envío
        total_price: Precio total con envío
        url: URL del producto
        seller_name: Nombre del vendedor
        seller_rating: Rating del vendedor
        seller_reviews: Número de reviews del vendedor
        is_prime: Es producto Prime (Amazon)
        is_official_store: Es tienda oficial
        condition: Estado del producto
        stock_status: Estado de stock
        timestamp: Fecha/hora de la consulta
        title: Título del producto en el marketplace
        image_url: URL de la imagen
    """
    marketplace: Marketplace
    price: float
    currency: str = "USD"
    shipping_cost: float = 0.0
    url: Optional[str] = None
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None
    seller_reviews: Optional[int] = None
    is_prime: bool = False
    is_official_store: bool = False
    condition: str = "new"
    stock_status: str = "in_stock"
    timestamp: datetime = field(default_factory=datetime.now)
    title: Optional[str] = None
    image_url: Optional[str] = None

    @property
    def total_price(self) -> float:
        """Calcula precio total incluyendo envío"""
        return self.price + self.shipping_cost

    @property
    def has_free_shipping(self) -> bool:
        """Verifica si tiene envío gratis"""
        return self.shipping_cost == 0

    def format_price(self) -> str:
        """Formatea el precio para mostrar"""
        symbol = {
            "USD": "$",
            "EUR": "€",
            "MXN": "MX$",
            "ARS": "AR$",
            "COP": "CO$",
            "CLP": "CL$",
            "PEN": "S/",
            "BRL": "R$"
        }.get(self.currency, self.currency)

        return f"{symbol}{self.price:,.2f}"

    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            "marketplace": self.marketplace.value,
            "price": self.price,
            "currency": self.currency,
            "shipping_cost": self.shipping_cost,
            "total_price": self.total_price,
            "url": self.url,
            "seller_name": self.seller_name,
            "seller_rating": self.seller_rating,
            "seller_reviews": self.seller_reviews,
            "is_prime": self.is_prime,
            "is_official_store": self.is_official_store,
            "condition": self.condition,
            "stock_status": self.stock_status,
            "timestamp": self.timestamp.isoformat(),
            "title": self.title,
            "image_url": self.image_url
        }


@dataclass
class PriceResult:
    """
    Resultado completo de verificación de precios de un producto.

    Attributes:
        product_name: Nombre del producto buscado
        search_query: Query de búsqueda utilizada
        prices: Lista de precios encontrados
        best_price: Mejor precio encontrado
        timestamp: Fecha/hora de la búsqueda
        errors: Lista de errores durante la búsqueda
        search_duration_ms: Duración de la búsqueda en ms
    """
    product_name: str
    search_query: str
    prices: List[MarketplacePrice] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)
    search_duration_ms: int = 0

    @property
    def best_price(self) -> Optional[MarketplacePrice]:
        """Obtiene el mejor precio (más bajo)"""
        if not self.prices:
            return None
        return min(self.prices, key=lambda p: p.total_price)

    @property
    def worst_price(self) -> Optional[MarketplacePrice]:
        """Obtiene el peor precio (más alto)"""
        if not self.prices:
            return None
        return max(self.prices, key=lambda p: p.total_price)

    @property
    def average_price(self) -> Optional[float]:
        """Calcula precio promedio"""
        if not self.prices:
            return None
        return sum(p.total_price for p in self.prices) / len(self.prices)

    @property
    def price_range(self) -> Optional[tuple]:
        """Retorna rango de precios (min, max)"""
        if not self.prices:
            return None
        best = self.best_price
        worst = self.worst_price
        return (best.total_price, worst.total_price)

    def get_prices_by_marketplace(self, marketplace: Marketplace) -> List[MarketplacePrice]:
        """Filtra precios por marketplace"""
        return [p for p in self.prices if p.marketplace == marketplace]

    def get_prices_below(self, max_price: float) -> List[MarketplacePrice]:
        """Filtra precios por debajo de un umbral"""
        return [p for p in self.prices if p.total_price <= max_price]

    def sort_by_price(self, ascending: bool = True) -> List[MarketplacePrice]:
        """Ordena precios"""
        return sorted(self.prices, key=lambda p: p.total_price, reverse=not ascending)

    def has_errors(self) -> bool:
        """Verifica si hubo errores"""
        return len(self.errors) > 0

    def summary(self) -> str:
        """Genera resumen de resultados"""
        lines = [
            f"📦 Producto: {self.product_name}",
            f"🔍 Búsqueda: {self.search_query}",
            f"📅 Fecha: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"⏱️ Duración: {self.search_duration_ms}ms",
            f"📊 Resultados: {len(self.prices)} precios encontrados",
        ]

        if self.best_price:
            lines.append(f"💰 Mejor precio: {self.best_price.format_price()} ({self.best_price.marketplace.value})")

        if self.average_price:
            lines.append(f"📈 Precio promedio: ${self.average_price:,.2f}")

        if self.errors:
            lines.append(f"⚠️ Errores: {len(self.errors)}")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            "product_name": self.product_name,
            "search_query": self.search_query,
            "prices": [p.to_dict() for p in self.prices],
            "best_price": self.best_price.to_dict() if self.best_price else None,
            "average_price": self.average_price,
            "timestamp": self.timestamp.isoformat(),
            "errors": self.errors,
            "search_duration_ms": self.search_duration_ms
        }

"""Criterios de búsqueda y alertas"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class PriceCondition(Enum):
    """Condiciones de precio para alertas"""
    BELOW = "below"           # Precio por debajo de
    ABOVE = "above"           # Precio por encima de
    BETWEEN = "between"       # Precio entre rango
    DROPS_BY = "drops_by"     # Baja un porcentaje
    DROPS_TO = "drops_to"     # Baja a un precio específico
    ANY_CHANGE = "any_change" # Cualquier cambio de precio


class SellerType(Enum):
    """Tipos de vendedor"""
    ANY = "any"
    OFFICIAL = "official"     # Vendedor oficial/marca
    MARKETPLACE = "marketplace"  # Marketplace directo (ej: Amazon)
    THIRD_PARTY = "third_party"  # Terceros


class Condition(Enum):
    """Estado del producto"""
    ANY = "any"
    NEW = "new"
    USED = "used"
    REFURBISHED = "refurbished"


@dataclass
class PriceCriteria:
    """
    Criterios para filtrar resultados de precios.

    Attributes:
        max_price: Precio máximo a considerar
        min_price: Precio mínimo (para evitar ofertas sospechosas)
        include_shipping: Incluir costo de envío en comparación
        free_shipping_only: Solo productos con envío gratis
        seller_type: Tipo de vendedor preferido
        condition: Estado del producto
        min_rating: Rating mínimo del vendedor (0-5)
        min_reviews: Número mínimo de reviews
        prime_only: Solo productos Prime (Amazon)
        local_only: Solo vendedores locales
        exclude_keywords: Palabras a excluir en resultados
    """
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    include_shipping: bool = True
    free_shipping_only: bool = False
    seller_type: SellerType = SellerType.ANY
    condition: Condition = Condition.NEW
    min_rating: float = 0.0
    min_reviews: int = 0
    prime_only: bool = False
    local_only: bool = False
    exclude_keywords: List[str] = field(default_factory=list)

    def matches_price(self, price: float, shipping: float = 0.0) -> bool:
        """Verifica si un precio cumple los criterios"""
        total = price + shipping if self.include_shipping else price

        if self.max_price is not None and total > self.max_price:
            return False
        if self.min_price is not None and total < self.min_price:
            return False

        return True

    def matches_shipping(self, shipping_cost: float) -> bool:
        """Verifica criterios de envío"""
        if self.free_shipping_only and shipping_cost > 0:
            return False
        return True

    def matches_seller(self, rating: float, reviews: int, is_official: bool = False) -> bool:
        """Verifica criterios del vendedor"""
        if rating < self.min_rating:
            return False
        if reviews < self.min_reviews:
            return False
        if self.seller_type == SellerType.OFFICIAL and not is_official:
            return False
        return True

    def to_dict(self) -> dict:
        """Convierte criterios a diccionario"""
        return {
            "max_price": self.max_price,
            "min_price": self.min_price,
            "include_shipping": self.include_shipping,
            "free_shipping_only": self.free_shipping_only,
            "seller_type": self.seller_type.value,
            "condition": self.condition.value,
            "min_rating": self.min_rating,
            "min_reviews": self.min_reviews,
            "prime_only": self.prime_only,
            "local_only": self.local_only,
            "exclude_keywords": self.exclude_keywords
        }


@dataclass
class AlertCriteria:
    """
    Criterios para generar alertas de precio.

    Attributes:
        condition: Condición que dispara la alerta
        threshold_price: Precio umbral
        threshold_percentage: Porcentaje de cambio
        min_price_range: Precio mínimo del rango
        max_price_range: Precio máximo del rango
        notify_email: Enviar alerta por email
        notify_telegram: Enviar alerta por Telegram
        notify_webhook: URL de webhook para notificación
        cooldown_hours: Horas entre alertas del mismo producto
    """
    condition: PriceCondition = PriceCondition.BELOW
    threshold_price: Optional[float] = None
    threshold_percentage: Optional[float] = None
    min_price_range: Optional[float] = None
    max_price_range: Optional[float] = None
    notify_email: bool = False
    notify_telegram: bool = False
    notify_webhook: Optional[str] = None
    cooldown_hours: int = 24

    def should_alert(self, current_price: float, previous_price: Optional[float] = None) -> bool:
        """Determina si se debe generar una alerta"""

        if self.condition == PriceCondition.BELOW:
            return self.threshold_price is not None and current_price < self.threshold_price

        elif self.condition == PriceCondition.ABOVE:
            return self.threshold_price is not None and current_price > self.threshold_price

        elif self.condition == PriceCondition.BETWEEN:
            if self.min_price_range is None or self.max_price_range is None:
                return False
            return self.min_price_range <= current_price <= self.max_price_range

        elif self.condition == PriceCondition.DROPS_BY:
            if previous_price is None or self.threshold_percentage is None:
                return False
            drop_percentage = ((previous_price - current_price) / previous_price) * 100
            return drop_percentage >= self.threshold_percentage

        elif self.condition == PriceCondition.DROPS_TO:
            return self.threshold_price is not None and current_price <= self.threshold_price

        elif self.condition == PriceCondition.ANY_CHANGE:
            return previous_price is not None and current_price != previous_price

        return False

    def to_dict(self) -> dict:
        """Convierte criterios de alerta a diccionario"""
        return {
            "condition": self.condition.value,
            "threshold_price": self.threshold_price,
            "threshold_percentage": self.threshold_percentage,
            "min_price_range": self.min_price_range,
            "max_price_range": self.max_price_range,
            "notify_email": self.notify_email,
            "notify_telegram": self.notify_telegram,
            "notify_webhook": self.notify_webhook,
            "cooldown_hours": self.cooldown_hours
        }

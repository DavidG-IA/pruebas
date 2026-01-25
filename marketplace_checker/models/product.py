"""Modelo de Producto para monitorear"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class ProductCategory(Enum):
    """Categorías de productos"""
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    HOME = "home"
    SPORTS = "sports"
    BOOKS = "books"
    TOYS = "toys"
    FOOD = "food"
    BEAUTY = "beauty"
    AUTOMOTIVE = "automotive"
    OTHER = "other"


@dataclass
class Product:
    """
    Representa un producto a monitorear en marketplaces.

    Attributes:
        name: Nombre del producto
        keywords: Palabras clave para búsqueda
        category: Categoría del producto
        brand: Marca del producto (opcional)
        model: Modelo específico (opcional)
        sku: SKU o código del producto (opcional)
        asin: ASIN de Amazon (opcional)
        ean: Código EAN/UPC (opcional)
        min_price: Precio mínimo esperado (para evitar falsificaciones)
        max_price: Precio máximo aceptable
        target_marketplaces: Lista de marketplaces donde buscar
        active: Si el monitoreo está activo
        notes: Notas adicionales
    """
    name: str
    keywords: List[str] = field(default_factory=list)
    category: ProductCategory = ProductCategory.OTHER
    brand: Optional[str] = None
    model: Optional[str] = None
    sku: Optional[str] = None
    asin: Optional[str] = None
    ean: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    target_marketplaces: List[str] = field(default_factory=lambda: ["amazon", "mercadolibre", "ebay"])
    active: bool = True
    notes: Optional[str] = None

    def __post_init__(self):
        """Validaciones post-inicialización"""
        if not self.name:
            raise ValueError("El nombre del producto es requerido")

        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                raise ValueError("El precio mínimo no puede ser mayor al máximo")

        # Agregar nombre a keywords si no está
        if self.name.lower() not in [k.lower() for k in self.keywords]:
            self.keywords.insert(0, self.name)

    def get_search_query(self) -> str:
        """Genera query de búsqueda optimizada"""
        parts = []

        if self.brand:
            parts.append(self.brand)

        parts.append(self.name)

        if self.model:
            parts.append(self.model)

        return " ".join(parts)

    def is_price_acceptable(self, price: float) -> bool:
        """Verifica si un precio está dentro del rango aceptable"""
        if self.min_price is not None and price < self.min_price:
            return False
        if self.max_price is not None and price > self.max_price:
            return False
        return True

    def to_dict(self) -> dict:
        """Convierte el producto a diccionario"""
        return {
            "name": self.name,
            "keywords": self.keywords,
            "category": self.category.value,
            "brand": self.brand,
            "model": self.model,
            "sku": self.sku,
            "asin": self.asin,
            "ean": self.ean,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "target_marketplaces": self.target_marketplaces,
            "active": self.active,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """Crea un producto desde diccionario"""
        if "category" in data and isinstance(data["category"], str):
            data["category"] = ProductCategory(data["category"])
        return cls(**data)

"""Agregador de precios de múltiples marketplaces"""

from typing import List, Dict, Optional, Type
from datetime import datetime
import time
import logging
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_checker import BasePriceChecker
from .amazon_checker import AmazonPriceChecker
from .mercadolibre_checker import MercadoLibrePriceChecker
from .ebay_checker import EbayPriceChecker
from ..models.product import Product
from ..models.criteria import PriceCriteria
from ..models.price_result import PriceResult, MarketplacePrice


class PriceAggregator:
    """
    Agregador que coordina búsquedas en múltiples marketplaces.

    Features:
    - Búsqueda paralela en múltiples marketplaces
    - Caché de resultados
    - Historial de precios
    - Comparación de precios
    """

    AVAILABLE_CHECKERS: Dict[str, Type[BasePriceChecker]] = {
        "amazon": AmazonPriceChecker,
        "amazon_es": AmazonPriceChecker,
        "amazon_mx": AmazonPriceChecker,
        "mercadolibre": MercadoLibrePriceChecker,
        "ebay": EbayPriceChecker,
    }

    def __init__(self, config: Optional[dict] = None, cache_dir: Optional[str] = None):
        """
        Inicializa el agregador.

        Args:
            config: Configuración con API keys para los diferentes checkers
            cache_dir: Directorio para caché de resultados
        """
        self.config = config or {}
        self.logger = logging.getLogger("price_aggregator")

        self.checkers: Dict[str, BasePriceChecker] = {}
        self.price_history: Dict[str, List[PriceResult]] = {}

        # Configurar directorio de caché
        if cache_dir:
            self.cache_dir = Path(cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.cache_dir = None

        # Inicializar checkers
        self._init_checkers()

    def _init_checkers(self):
        """Inicializa los checkers configurados"""
        # Amazon US por defecto
        self.checkers["amazon"] = AmazonPriceChecker("amazon", self.config)

        # MercadoLibre México por defecto
        self.checkers["mercadolibre"] = MercadoLibrePriceChecker("MLM", self.config)

        # eBay US por defecto
        self.checkers["ebay"] = EbayPriceChecker("US", self.config)

        self.logger.info(f"Inicializados {len(self.checkers)} checkers")

    def add_checker(self, name: str, checker: BasePriceChecker):
        """Agrega un checker personalizado"""
        self.checkers[name] = checker
        self.logger.info(f"Agregado checker: {name}")

    def remove_checker(self, name: str):
        """Remueve un checker"""
        if name in self.checkers:
            del self.checkers[name]
            self.logger.info(f"Removido checker: {name}")

    def search(self, product: Product, criteria: Optional[PriceCriteria] = None,
               marketplaces: Optional[List[str]] = None, parallel: bool = True) -> PriceResult:
        """
        Busca un producto en los marketplaces especificados.

        Args:
            product: Producto a buscar
            criteria: Criterios de filtrado
            marketplaces: Lista de marketplaces (None = todos)
            parallel: Ejecutar búsquedas en paralelo

        Returns:
            PriceResult con todos los precios encontrados
        """
        start_time = time.time()

        # Determinar marketplaces a usar
        if marketplaces:
            target_checkers = {k: v for k, v in self.checkers.items() if k in marketplaces}
        elif product.target_marketplaces:
            target_checkers = {k: v for k, v in self.checkers.items()
                             if k in product.target_marketplaces}
        else:
            target_checkers = self.checkers

        if not target_checkers:
            self.logger.warning("No hay checkers disponibles para la búsqueda")
            return PriceResult(
                product_name=product.name,
                search_query=product.get_search_query(),
                errors=["No hay marketplaces configurados"]
            )

        all_prices: List[MarketplacePrice] = []
        errors: List[str] = []

        if parallel and len(target_checkers) > 1:
            # Búsqueda paralela
            with ThreadPoolExecutor(max_workers=len(target_checkers)) as executor:
                futures = {
                    executor.submit(checker.search, product, criteria): name
                    for name, checker in target_checkers.items()
                }

                for future in as_completed(futures):
                    name = futures[future]
                    try:
                        prices = future.result()
                        all_prices.extend(prices)
                        self.logger.info(f"{name}: {len(prices)} resultados")
                    except Exception as e:
                        error_msg = f"Error en {name}: {str(e)}"
                        errors.append(error_msg)
                        self.logger.error(error_msg)
        else:
            # Búsqueda secuencial
            for name, checker in target_checkers.items():
                try:
                    prices = checker.search(product, criteria)
                    all_prices.extend(prices)
                    self.logger.info(f"{name}: {len(prices)} resultados")
                except Exception as e:
                    error_msg = f"Error en {name}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)

        # Crear resultado
        duration_ms = int((time.time() - start_time) * 1000)

        result = PriceResult(
            product_name=product.name,
            search_query=product.get_search_query(),
            prices=all_prices,
            errors=errors,
            search_duration_ms=duration_ms
        )

        # Guardar en historial
        self._save_to_history(product.name, result)

        # Guardar en caché si está configurado
        if self.cache_dir:
            self._save_to_cache(product.name, result)

        return result

    def compare_prices(self, result: PriceResult) -> Dict:
        """
        Genera comparación detallada de precios.

        Args:
            result: Resultado de búsqueda

        Returns:
            Diccionario con análisis comparativo
        """
        if not result.prices:
            return {"error": "No hay precios para comparar"}

        # Agrupar por marketplace
        by_marketplace = {}
        for price in result.prices:
            mp = price.marketplace.value
            if mp not in by_marketplace:
                by_marketplace[mp] = []
            by_marketplace[mp].append(price)

        # Calcular estadísticas por marketplace
        stats = {}
        for mp, prices in by_marketplace.items():
            totals = [p.total_price for p in prices]
            stats[mp] = {
                "count": len(prices),
                "min_price": min(totals),
                "max_price": max(totals),
                "avg_price": sum(totals) / len(totals),
                "best_offer": min(prices, key=lambda p: p.total_price).to_dict(),
            }

        return {
            "product": result.product_name,
            "total_results": len(result.prices),
            "marketplaces_searched": len(by_marketplace),
            "best_overall": result.best_price.to_dict() if result.best_price else None,
            "by_marketplace": stats,
            "price_spread": result.price_range,
            "search_time_ms": result.search_duration_ms,
        }

    def get_price_history(self, product_name: str) -> List[PriceResult]:
        """Obtiene historial de precios de un producto"""
        return self.price_history.get(product_name, [])

    def _save_to_history(self, product_name: str, result: PriceResult):
        """Guarda resultado en historial"""
        if product_name not in self.price_history:
            self.price_history[product_name] = []

        # Mantener últimos 100 resultados por producto
        history = self.price_history[product_name]
        history.append(result)
        if len(history) > 100:
            self.price_history[product_name] = history[-100:]

    def _save_to_cache(self, product_name: str, result: PriceResult):
        """Guarda resultado en caché de disco"""
        if not self.cache_dir:
            return

        # Sanitizar nombre para archivo
        safe_name = "".join(c if c.isalnum() else "_" for c in product_name)
        cache_file = self.cache_dir / f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error guardando caché: {e}")

    def get_available_marketplaces(self) -> List[str]:
        """Retorna lista de marketplaces disponibles"""
        return list(self.checkers.keys())

    def health_check(self) -> Dict[str, bool]:
        """Verifica estado de todos los checkers"""
        status = {}
        for name, checker in self.checkers.items():
            status[name] = checker.is_available()
        return status

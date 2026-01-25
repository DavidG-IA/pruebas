"""Formateadores para presentación de datos"""

from typing import List, Optional
from ..models.price_result import PriceResult, MarketplacePrice


class PriceFormatter:
    """Formateador de precios para diferentes monedas"""

    CURRENCY_SYMBOLS = {
        "USD": "$",
        "EUR": "€",
        "MXN": "MX$",
        "ARS": "AR$",
        "COP": "CO$",
        "CLP": "CL$",
        "PEN": "S/",
        "BRL": "R$",
        "GBP": "£",
        "AUD": "A$",
    }

    @classmethod
    def format(cls, amount: float, currency: str = "USD",
               include_decimals: bool = True) -> str:
        """
        Formatea un precio con su símbolo de moneda.

        Args:
            amount: Monto a formatear
            currency: Código de moneda
            include_decimals: Incluir decimales

        Returns:
            Precio formateado
        """
        symbol = cls.CURRENCY_SYMBOLS.get(currency, currency + " ")

        if include_decimals:
            return f"{symbol}{amount:,.2f}"
        else:
            return f"{symbol}{amount:,.0f}"

    @classmethod
    def format_with_shipping(cls, price: float, shipping: float,
                            currency: str = "USD") -> str:
        """Formatea precio con información de envío"""
        total = price + shipping

        if shipping == 0:
            return f"{cls.format(price, currency)} (envío gratis)"
        else:
            return f"{cls.format(price, currency)} + {cls.format(shipping, currency)} envío = {cls.format(total, currency)}"

    @classmethod
    def format_discount(cls, original: float, current: float) -> str:
        """Formatea el descuento entre dos precios"""
        if original <= current:
            return "Sin descuento"

        discount = original - current
        percentage = (discount / original) * 100

        return f"-{percentage:.1f}% (ahorro: ${discount:.2f})"


class TableFormatter:
    """Formateador de tablas para resultados"""

    @classmethod
    def format_price_results(cls, result: PriceResult, max_rows: int = 10) -> str:
        """
        Formatea resultados de precios en tabla ASCII.

        Args:
            result: Resultados a formatear
            max_rows: Máximo de filas a mostrar

        Returns:
            Tabla formateada como string
        """
        if not result.prices:
            return "No se encontraron resultados"

        # Ordenar por precio
        sorted_prices = sorted(result.prices, key=lambda p: p.total_price)[:max_rows]

        # Headers
        lines = [
            "",
            f"📦 Resultados para: {result.product_name}",
            f"🔍 Búsqueda: {result.search_query}",
            f"📊 Total encontrados: {len(result.prices)}",
            "",
            "=" * 100,
            f"{'#':<3} {'Marketplace':<15} {'Precio':<12} {'Envío':<10} {'Total':<12} {'Vendedor':<20} {'Cond.':<10}",
            "=" * 100,
        ]

        for i, price in enumerate(sorted_prices, 1):
            shipping_str = "Gratis" if price.has_free_shipping else PriceFormatter.format(price.shipping_cost, price.currency)
            seller = (price.seller_name or "N/A")[:18]
            condition = price.condition[:8].title()

            line = (
                f"{i:<3} "
                f"{price.marketplace.value:<15} "
                f"{PriceFormatter.format(price.price, price.currency):<12} "
                f"{shipping_str:<10} "
                f"{PriceFormatter.format(price.total_price, price.currency):<12} "
                f"{seller:<20} "
                f"{condition:<10}"
            )

            # Agregar indicadores
            badges = []
            if price.is_prime:
                badges.append("🚀Prime")
            if price.is_official_store:
                badges.append("✓Oficial")

            if badges:
                line += " " + " ".join(badges)

            lines.append(line)

        lines.append("=" * 100)

        # Resumen
        if result.best_price:
            bp = result.best_price
            lines.append(f"\n💰 Mejor precio: {PriceFormatter.format(bp.total_price, bp.currency)} en {bp.marketplace.value}")

        if result.average_price:
            lines.append(f"📈 Precio promedio: ${result.average_price:.2f}")

        if result.price_range:
            min_p, max_p = result.price_range
            lines.append(f"📊 Rango: ${min_p:.2f} - ${max_p:.2f}")

        lines.append(f"⏱️ Tiempo de búsqueda: {result.search_duration_ms}ms")

        if result.errors:
            lines.append(f"\n⚠️ Errores: {', '.join(result.errors)}")

        return "\n".join(lines)

    @classmethod
    def format_comparison(cls, comparison: dict) -> str:
        """Formatea comparación de precios"""
        lines = [
            "",
            "=" * 80,
            "📊 COMPARACIÓN DE PRECIOS",
            "=" * 80,
            f"Producto: {comparison.get('product', 'N/A')}",
            f"Total resultados: {comparison.get('total_results', 0)}",
            f"Marketplaces: {comparison.get('marketplaces_searched', 0)}",
            "",
        ]

        # Por marketplace
        by_mp = comparison.get('by_marketplace', {})
        if by_mp:
            lines.append("Por Marketplace:")
            lines.append("-" * 60)

            for mp, stats in by_mp.items():
                lines.append(
                    f"  {mp.upper():15} | "
                    f"Min: ${stats['min_price']:.2f} | "
                    f"Max: ${stats['max_price']:.2f} | "
                    f"Avg: ${stats['avg_price']:.2f} | "
                    f"({stats['count']} ofertas)"
                )

        # Mejor oferta global
        best = comparison.get('best_overall')
        if best:
            lines.append("")
            lines.append("=" * 60)
            lines.append(f"🏆 MEJOR OFERTA: ${best['total_price']:.2f} en {best['marketplace']}")
            if best.get('url'):
                lines.append(f"   URL: {best['url']}")

        return "\n".join(lines)

    @classmethod
    def format_alert(cls, alert) -> str:
        """Formatea una alerta para mostrar"""
        lines = [
            "",
            "🔔 " + "=" * 50,
            "   ALERTA DE PRECIO",
            "=" * 53,
            f"Producto: {alert.product_name}",
            f"Condición: {alert.trigger_condition}",
            f"Precio actual: ${alert.current_price:.2f}",
            f"Marketplace: {alert.marketplace}",
        ]

        if alert.previous_price:
            lines.append(f"Precio anterior: ${alert.previous_price:.2f}")

        if alert.url:
            lines.append(f"URL: {alert.url}")

        lines.append(f"Fecha: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 53)

        return "\n".join(lines)

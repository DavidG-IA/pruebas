#!/usr/bin/env python3
"""
CLI para Marketplace Price Checker

Uso:
    python -m marketplace_checker search "iPhone 15"
    python -m marketplace_checker monitor products.json
    python -m marketplace_checker compare "PlayStation 5"
"""

import argparse
import json
import logging
import sys
from typing import Optional

from .models.product import Product, ProductCategory
from .models.criteria import PriceCriteria, AlertCriteria, PriceCondition, Condition
from .services.price_aggregator import PriceAggregator
from .services.alert_service import AlertService
from .utils.config_loader import ConfigLoader
from .utils.formatters import TableFormatter


def setup_logging(level: str = "INFO"):
    """Configura el logging"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def load_products_from_file(filepath: str) -> list:
    """Carga productos desde archivo JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    products = []
    for item in data.get('products', data if isinstance(data, list) else []):
        products.append(Product.from_dict(item))

    return products


def cmd_search(args, config: ConfigLoader):
    """Comando: buscar un producto"""
    print(f"\n🔍 Buscando: {args.query}")
    print("-" * 50)

    # Crear producto desde query
    product = Product(
        name=args.query,
        brand=args.brand,
        max_price=args.max_price,
        min_price=args.min_price,
        target_marketplaces=args.marketplaces.split(',') if args.marketplaces else None
    )

    # Crear criterios
    criteria = PriceCriteria(
        max_price=args.max_price,
        min_price=args.min_price,
        free_shipping_only=args.free_shipping,
        condition=Condition(args.condition) if args.condition else Condition.ANY,
        prime_only=args.prime_only
    )

    # Crear agregador y buscar
    aggregator = PriceAggregator(config.get_checker_config())

    print(f"📡 Marketplaces: {', '.join(aggregator.get_available_marketplaces())}")
    print()

    result = aggregator.search(product, criteria)

    # Mostrar resultados
    print(TableFormatter.format_price_results(result, max_rows=args.limit))

    # Guardar resultados si se especifica
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resultados guardados en: {args.output}")


def cmd_compare(args, config: ConfigLoader):
    """Comando: comparar precios de un producto"""
    print(f"\n📊 Comparando precios: {args.query}")
    print("-" * 50)

    product = Product(
        name=args.query,
        brand=args.brand,
        max_price=args.max_price
    )

    aggregator = PriceAggregator(config.get_checker_config())
    result = aggregator.search(product)

    comparison = aggregator.compare_prices(result)
    print(TableFormatter.format_comparison(comparison))


def cmd_monitor(args, config: ConfigLoader):
    """Comando: monitorear productos desde archivo"""
    print(f"\n👁️ Monitoreando productos desde: {args.file}")
    print("-" * 50)

    # Cargar productos
    try:
        products = load_products_from_file(args.file)
        print(f"📦 Productos cargados: {len(products)}")
    except Exception as e:
        print(f"❌ Error cargando productos: {e}")
        return

    # Crear servicios
    aggregator = PriceAggregator(
        config.get_checker_config(),
        cache_dir=config.get("cache_dir")
    )

    alert_service = AlertService(
        config.get_alert_config(),
        storage_path=config.get("alerts_storage_path")
    )

    # Criterios de alerta por defecto
    default_alert = AlertCriteria(
        condition=PriceCondition.BELOW,
        cooldown_hours=args.cooldown
    )

    # Monitorear cada producto
    for product in products:
        if not product.active:
            print(f"⏸️ {product.name} - Inactivo, saltando...")
            continue

        print(f"\n🔍 Buscando: {product.name}")

        # Crear criterios específicos del producto
        criteria = PriceCriteria(
            max_price=product.max_price,
            min_price=product.min_price
        )

        # Buscar
        result = aggregator.search(product, criteria)

        if result.best_price:
            print(f"   💰 Mejor: {result.best_price.format_price()} en {result.best_price.marketplace.value}")

            # Verificar alertas si hay precio objetivo
            if product.max_price:
                alert_criteria = AlertCriteria(
                    condition=PriceCondition.BELOW,
                    threshold_price=product.max_price,
                    cooldown_hours=args.cooldown
                )

                alerts = alert_service.check_and_alert(
                    product, result, alert_criteria
                )

                for alert in alerts:
                    print(TableFormatter.format_alert(alert))
        else:
            print(f"   ❌ Sin resultados")

    print(f"\n✅ Monitoreo completado")


def cmd_add_product(args, config: ConfigLoader):
    """Comando: agregar producto a monitorear"""
    products_file = args.file or config.get("products_file", "products.json")

    # Cargar productos existentes
    try:
        with open(products_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"products": []}

    # Crear nuevo producto
    new_product = {
        "name": args.name,
        "brand": args.brand,
        "category": args.category or "other",
        "max_price": args.max_price,
        "min_price": args.min_price,
        "target_marketplaces": args.marketplaces.split(',') if args.marketplaces else ["amazon", "mercadolibre", "ebay"],
        "active": True
    }

    if args.asin:
        new_product["asin"] = args.asin

    # Agregar
    if "products" not in data:
        data = {"products": [data] if isinstance(data, dict) else data}

    data["products"].append(new_product)

    # Guardar
    with open(products_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Producto agregado: {args.name}")
    print(f"📁 Guardado en: {products_file}")


def cmd_list_products(args, config: ConfigLoader):
    """Comando: listar productos configurados"""
    products_file = args.file or config.get("products_file", "products.json")

    try:
        products = load_products_from_file(products_file)
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {products_file}")
        return

    print(f"\n📦 Productos en {products_file}:")
    print("=" * 70)

    for i, p in enumerate(products, 1):
        status = "✅" if p.active else "⏸️"
        price_range = ""
        if p.min_price or p.max_price:
            min_p = f"${p.min_price:.2f}" if p.min_price else "-"
            max_p = f"${p.max_price:.2f}" if p.max_price else "-"
            price_range = f" [{min_p} - {max_p}]"

        print(f"{i}. {status} {p.name}{price_range}")
        if p.brand:
            print(f"      Marca: {p.brand}")
        print(f"      Marketplaces: {', '.join(p.target_marketplaces)}")

    print("=" * 70)
    print(f"Total: {len(products)} productos")


def cmd_init(args, config: ConfigLoader):
    """Comando: inicializar configuración"""
    print("🚀 Inicializando Marketplace Price Checker...")

    # Crear config de ejemplo
    config_file = ConfigLoader.create_sample_config("config.json")
    print(f"✅ Configuración creada: {config_file}")

    # Crear archivo de productos de ejemplo
    sample_products = {
        "products": [
            {
                "name": "iPhone 15 Pro",
                "brand": "Apple",
                "category": "electronics",
                "max_price": 1200,
                "target_marketplaces": ["amazon", "mercadolibre", "ebay"],
                "active": True
            },
            {
                "name": "PlayStation 5",
                "brand": "Sony",
                "category": "electronics",
                "max_price": 500,
                "target_marketplaces": ["amazon", "mercadolibre"],
                "active": True
            },
            {
                "name": "Nintendo Switch OLED",
                "brand": "Nintendo",
                "category": "electronics",
                "max_price": 350,
                "target_marketplaces": ["amazon", "ebay"],
                "active": True
            }
        ]
    }

    with open("products.json", 'w', encoding='utf-8') as f:
        json.dump(sample_products, f, indent=2, ensure_ascii=False)
    print("✅ Productos de ejemplo creados: products.json")

    print("\n📋 Próximos pasos:")
    print("1. Edita config.json con tus API keys (opcional)")
    print("2. Edita products.json con los productos a monitorear")
    print("3. Ejecuta: python -m marketplace_checker search 'tu producto'")


def main():
    """Punto de entrada principal"""
    parser = argparse.ArgumentParser(
        description="Marketplace Price Checker - Monitorea precios en múltiples marketplaces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s search "iPhone 15 Pro" --max-price 1000
  %(prog)s compare "PlayStation 5" --brand Sony
  %(prog)s monitor products.json --cooldown 12
  %(prog)s add "AirPods Pro" --brand Apple --max-price 250
  %(prog)s init
        """
    )

    parser.add_argument('-c', '--config', help='Archivo de configuración')
    parser.add_argument('-v', '--verbose', action='store_true', help='Modo verbose')

    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')

    # Comando: search
    search_parser = subparsers.add_parser('search', help='Buscar un producto')
    search_parser.add_argument('query', help='Nombre o descripción del producto')
    search_parser.add_argument('--brand', '-b', help='Marca del producto')
    search_parser.add_argument('--max-price', '-M', type=float, help='Precio máximo')
    search_parser.add_argument('--min-price', '-m', type=float, help='Precio mínimo')
    search_parser.add_argument('--marketplaces', help='Marketplaces (separados por coma)')
    search_parser.add_argument('--free-shipping', action='store_true', help='Solo envío gratis')
    search_parser.add_argument('--prime-only', action='store_true', help='Solo productos Prime')
    search_parser.add_argument('--condition', choices=['new', 'used', 'refurbished', 'any'],
                              default='any', help='Estado del producto')
    search_parser.add_argument('--limit', '-l', type=int, default=10, help='Máximo de resultados')
    search_parser.add_argument('--output', '-o', help='Guardar resultados en archivo JSON')

    # Comando: compare
    compare_parser = subparsers.add_parser('compare', help='Comparar precios entre marketplaces')
    compare_parser.add_argument('query', help='Nombre del producto')
    compare_parser.add_argument('--brand', '-b', help='Marca del producto')
    compare_parser.add_argument('--max-price', '-M', type=float, help='Precio máximo')

    # Comando: monitor
    monitor_parser = subparsers.add_parser('monitor', help='Monitorear productos desde archivo')
    monitor_parser.add_argument('file', help='Archivo JSON con productos')
    monitor_parser.add_argument('--cooldown', type=int, default=24,
                               help='Horas entre alertas del mismo producto')

    # Comando: add
    add_parser = subparsers.add_parser('add', help='Agregar producto a monitorear')
    add_parser.add_argument('name', help='Nombre del producto')
    add_parser.add_argument('--brand', '-b', help='Marca')
    add_parser.add_argument('--category', '-c', help='Categoría')
    add_parser.add_argument('--max-price', '-M', type=float, help='Precio máximo objetivo')
    add_parser.add_argument('--min-price', '-m', type=float, help='Precio mínimo')
    add_parser.add_argument('--asin', help='ASIN de Amazon')
    add_parser.add_argument('--marketplaces', help='Marketplaces (separados por coma)')
    add_parser.add_argument('--file', '-f', help='Archivo de productos')

    # Comando: list
    list_parser = subparsers.add_parser('list', help='Listar productos configurados')
    list_parser.add_argument('--file', '-f', help='Archivo de productos')

    # Comando: init
    init_parser = subparsers.add_parser('init', help='Inicializar configuración')

    args = parser.parse_args()

    # Setup
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)

    config = ConfigLoader(args.config)

    # Ejecutar comando
    if args.command == 'search':
        cmd_search(args, config)
    elif args.command == 'compare':
        cmd_compare(args, config)
    elif args.command == 'monitor':
        cmd_monitor(args, config)
    elif args.command == 'add':
        cmd_add_product(args, config)
    elif args.command == 'list':
        cmd_list_products(args, config)
    elif args.command == 'init':
        cmd_init(args, config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

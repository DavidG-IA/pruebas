# Marketplace Price Checker

Aplicación para verificar y monitorear precios de productos en múltiples marketplaces.

## Características

- **Búsqueda en múltiples marketplaces**: Amazon, MercadoLibre, eBay
- **Criterios de filtrado avanzados**: precio, envío, condición, vendedor
- **Sistema de alertas**: notificaciones por email, Telegram o webhook
- **Historial de precios**: seguimiento de cambios de precio
- **CLI completo**: interfaz de línea de comandos fácil de usar
- **Sin dependencias externas**: funciona con Python estándar

## Instalación

```bash
# Clonar el repositorio
git clone <repo-url>
cd pruebas

# (Opcional) Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
.\venv\Scripts\activate  # Windows

# No requiere instalación de dependencias para funcionalidad básica
```

## Uso Rápido

### Inicializar configuración

```bash
python -m marketplace_checker init
```

### Buscar un producto

```bash
python -m marketplace_checker search "iPhone 15 Pro"
python -m marketplace_checker search "PlayStation 5" --max-price 500 --brand Sony
python -m marketplace_checker search "AirPods" --free-shipping --prime-only
```

### Comparar precios

```bash
python -m marketplace_checker compare "Nintendo Switch"
```

### Monitorear productos

```bash
# Edita products.json con tus productos
python -m marketplace_checker monitor products.json
```

### Agregar producto a monitorear

```bash
python -m marketplace_checker add "MacBook Pro M3" --brand Apple --max-price 2000
```

### Listar productos configurados

```bash
python -m marketplace_checker list
```

## Configuración

### Archivo config.json

```json
{
  "log_level": "INFO",
  "amazon_region": "amazon",
  "mercadolibre_country": "MLM",
  "ebay_site": "US",
  "email_from": "tu-email@gmail.com",
  "telegram_token": "tu-token-bot"
}
```

### Variables de entorno

Todas las configuraciones pueden establecerse con variables de entorno usando el prefijo `MPC_`:

```bash
export MPC_AMAZON_API_KEY="tu-api-key"
export MPC_TELEGRAM_TOKEN="tu-token"
export MPC_EMAIL_FROM="tu-email@gmail.com"
```

### Productos (products.json)

```json
{
  "products": [
    {
      "name": "iPhone 15 Pro",
      "brand": "Apple",
      "category": "electronics",
      "max_price": 1200,
      "min_price": 800,
      "target_marketplaces": ["amazon", "mercadolibre", "ebay"],
      "active": true
    }
  ]
}
```

## Criterios de Búsqueda

| Criterio | Descripción |
|----------|-------------|
| `max_price` | Precio máximo aceptable |
| `min_price` | Precio mínimo (evita ofertas sospechosas) |
| `free_shipping_only` | Solo productos con envío gratis |
| `prime_only` | Solo productos Prime (Amazon) |
| `condition` | new, used, refurbished, any |
| `min_rating` | Rating mínimo del vendedor (0-5) |
| `exclude_keywords` | Palabras a excluir en resultados |

## Criterios de Alertas

| Condición | Descripción |
|-----------|-------------|
| `below` | Precio por debajo de umbral |
| `above` | Precio por encima de umbral |
| `between` | Precio entre rango |
| `drops_by` | Baja un porcentaje específico |
| `drops_to` | Baja a un precio específico |
| `any_change` | Cualquier cambio de precio |

## Marketplaces Soportados

- **Amazon**: US, ES, MX, DE, UK, FR, IT
- **MercadoLibre**: Argentina, Brasil, Chile, Colombia, México, Perú, Uruguay
- **eBay**: US, UK, DE, ES, FR, IT, AU

## Estructura del Proyecto

```
marketplace_checker/
├── __init__.py
├── __main__.py
├── cli.py                    # Interfaz de línea de comandos
├── models/
│   ├── product.py           # Modelo de producto
│   ├── criteria.py          # Criterios de búsqueda/alertas
│   └── price_result.py      # Resultados de precios
├── services/
│   ├── base_checker.py      # Clase base para checkers
│   ├── amazon_checker.py    # Checker de Amazon
│   ├── mercadolibre_checker.py  # Checker de MercadoLibre
│   ├── ebay_checker.py      # Checker de eBay
│   ├── price_aggregator.py  # Agregador de precios
│   └── alert_service.py     # Servicio de alertas
├── utils/
│   ├── formatters.py        # Formateadores de salida
│   └── config_loader.py     # Cargador de configuración
└── config/
```

## Notificaciones

### Email (Gmail)

1. Habilita "Contraseñas de aplicación" en tu cuenta de Google
2. Configura en config.json:
```json
{
  "email_from": "tu-email@gmail.com",
  "email_password": "tu-contraseña-de-app",
  "email_to": ["destinatario@email.com"]
}
```

### Telegram

1. Crea un bot con @BotFather
2. Obtén el chat_id enviando un mensaje al bot
3. Configura:
```json
{
  "telegram_token": "123456:ABC-DEF...",
  "telegram_chat_id": "tu-chat-id"
}
```

### Webhook

```json
{
  "notify_webhook": "https://tu-servidor.com/webhook"
}
```

## Ejemplos de Uso Avanzado

### Búsqueda con filtros múltiples

```bash
python -m marketplace_checker search "laptop gaming" \
  --max-price 1500 \
  --min-price 800 \
  --free-shipping \
  --condition new \
  --marketplaces amazon,ebay \
  --limit 20 \
  --output resultados.json
```

### Monitoreo programado (cron)

```bash
# Agregar a crontab para ejecutar cada hora
0 * * * * /usr/bin/python3 -m marketplace_checker monitor /ruta/products.json
```

## Notas Importantes

- Esta versión incluye **datos simulados** para demostración
- Para uso en producción, integrar con APIs oficiales:
  - Amazon Product Advertising API
  - MercadoLibre API
  - eBay Browse API
- Respetar los términos de servicio de cada marketplace
- Implementar rate limiting apropiado

## Licencia

MIT License

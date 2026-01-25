"""Servicio de alertas de precios"""

from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging
import json
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..models.product import Product
from ..models.criteria import AlertCriteria, PriceCondition
from ..models.price_result import PriceResult, MarketplacePrice


@dataclass
class Alert:
    """Representa una alerta generada"""
    id: str
    product_name: str
    trigger_condition: str
    current_price: float
    previous_price: Optional[float]
    threshold: Optional[float]
    marketplace: str
    url: Optional[str]
    timestamp: datetime = field(default_factory=datetime.now)
    sent: bool = False
    sent_via: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "product_name": self.product_name,
            "trigger_condition": self.trigger_condition,
            "current_price": self.current_price,
            "previous_price": self.previous_price,
            "threshold": self.threshold,
            "marketplace": self.marketplace,
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
            "sent": self.sent,
            "sent_via": self.sent_via
        }


class AlertService:
    """
    Servicio para gestionar y enviar alertas de precios.

    Features:
    - Múltiples canales de notificación (email, Telegram, webhook)
    - Control de cooldown para evitar spam
    - Historial de alertas
    - Callbacks personalizados
    """

    def __init__(self, config: Optional[dict] = None, storage_path: Optional[str] = None):
        """
        Inicializa el servicio de alertas.

        Args:
            config: Configuración de notificaciones
            storage_path: Ruta para persistir alertas
        """
        self.config = config or {}
        self.logger = logging.getLogger("alert_service")

        # Almacenamiento de alertas
        self.alerts: List[Alert] = []
        self.last_alert_times: Dict[str, datetime] = {}

        # Callbacks personalizados
        self.custom_handlers: List[Callable[[Alert], None]] = []

        # Configuración de email
        self.smtp_server = self.config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = self.config.get("smtp_port", 587)
        self.email_from = self.config.get("email_from")
        self.email_password = self.config.get("email_password")
        self.email_to = self.config.get("email_to", [])

        # Configuración de Telegram
        self.telegram_token = self.config.get("telegram_token")
        self.telegram_chat_id = self.config.get("telegram_chat_id")

        # Storage
        if storage_path:
            self.storage_path = Path(storage_path)
            self.storage_path.mkdir(parents=True, exist_ok=True)
            self._load_alerts()
        else:
            self.storage_path = None

    def check_and_alert(self, product: Product, result: PriceResult,
                        criteria: AlertCriteria,
                        previous_best_price: Optional[float] = None) -> List[Alert]:
        """
        Verifica si se deben generar alertas basadas en los resultados.

        Args:
            product: Producto monitoreado
            result: Resultado de la búsqueda de precios
            criteria: Criterios de alerta
            previous_best_price: Mejor precio anterior (para comparación)

        Returns:
            Lista de alertas generadas
        """
        generated_alerts = []

        if not result.best_price:
            return generated_alerts

        current_price = result.best_price.total_price

        # Verificar cooldown
        cooldown_key = f"{product.name}_{criteria.condition.value}"
        if not self._check_cooldown(cooldown_key, criteria.cooldown_hours):
            self.logger.debug(f"Alerta en cooldown para {product.name}")
            return generated_alerts

        # Verificar si se cumple la condición de alerta
        if criteria.should_alert(current_price, previous_best_price):
            alert = self._create_alert(product, result.best_price, criteria, previous_best_price)
            generated_alerts.append(alert)

            # Enviar notificaciones
            self._send_notifications(alert, criteria)

            # Actualizar cooldown
            self.last_alert_times[cooldown_key] = datetime.now()

            # Guardar alerta
            self.alerts.append(alert)
            self._save_alerts()

        return generated_alerts

    def _create_alert(self, product: Product, price: MarketplacePrice,
                     criteria: AlertCriteria, previous_price: Optional[float]) -> Alert:
        """Crea una nueva alerta"""
        alert_id = f"{product.name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        trigger_desc = self._get_trigger_description(criteria, price.total_price, previous_price)

        return Alert(
            id=alert_id,
            product_name=product.name,
            trigger_condition=trigger_desc,
            current_price=price.total_price,
            previous_price=previous_price,
            threshold=criteria.threshold_price,
            marketplace=price.marketplace.value,
            url=price.url,
        )

    def _get_trigger_description(self, criteria: AlertCriteria,
                                 current: float, previous: Optional[float]) -> str:
        """Genera descripción del trigger de la alerta"""
        if criteria.condition == PriceCondition.BELOW:
            return f"Precio por debajo de ${criteria.threshold_price}"
        elif criteria.condition == PriceCondition.ABOVE:
            return f"Precio por encima de ${criteria.threshold_price}"
        elif criteria.condition == PriceCondition.BETWEEN:
            return f"Precio entre ${criteria.min_price_range} y ${criteria.max_price_range}"
        elif criteria.condition == PriceCondition.DROPS_BY:
            if previous:
                drop = ((previous - current) / previous) * 100
                return f"Precio bajó {drop:.1f}% (de ${previous:.2f} a ${current:.2f})"
            return f"Precio bajó más de {criteria.threshold_percentage}%"
        elif criteria.condition == PriceCondition.DROPS_TO:
            return f"Precio bajó a ${current:.2f}"
        elif criteria.condition == PriceCondition.ANY_CHANGE:
            if previous:
                change = current - previous
                direction = "subió" if change > 0 else "bajó"
                return f"Precio {direction} ${abs(change):.2f}"
            return "Cambio de precio detectado"
        return "Condición de alerta cumplida"

    def _check_cooldown(self, key: str, cooldown_hours: int) -> bool:
        """Verifica si pasó el tiempo de cooldown"""
        if key not in self.last_alert_times:
            return True

        last_time = self.last_alert_times[key]
        cooldown_delta = timedelta(hours=cooldown_hours)

        return datetime.now() - last_time >= cooldown_delta

    def _send_notifications(self, alert: Alert, criteria: AlertCriteria):
        """Envía notificaciones por los canales configurados"""

        # Email
        if criteria.notify_email and self.email_from:
            try:
                self._send_email(alert)
                alert.sent_via.append("email")
            except Exception as e:
                self.logger.error(f"Error enviando email: {e}")

        # Telegram
        if criteria.notify_telegram and self.telegram_token:
            try:
                self._send_telegram(alert)
                alert.sent_via.append("telegram")
            except Exception as e:
                self.logger.error(f"Error enviando Telegram: {e}")

        # Webhook
        if criteria.notify_webhook:
            try:
                self._send_webhook(alert, criteria.notify_webhook)
                alert.sent_via.append("webhook")
            except Exception as e:
                self.logger.error(f"Error enviando webhook: {e}")

        # Custom handlers
        for handler in self.custom_handlers:
            try:
                handler(alert)
                alert.sent_via.append("custom")
            except Exception as e:
                self.logger.error(f"Error en handler personalizado: {e}")

        alert.sent = len(alert.sent_via) > 0

    def _send_email(self, alert: Alert):
        """Envía notificación por email"""
        if not self.email_to:
            self.logger.warning("No hay destinatarios de email configurados")
            return

        subject = f"🔔 Alerta de Precio: {alert.product_name}"

        html_body = f"""
        <html>
        <body>
            <h2>Alerta de Precio</h2>
            <p><strong>Producto:</strong> {alert.product_name}</p>
            <p><strong>Condición:</strong> {alert.trigger_condition}</p>
            <p><strong>Precio actual:</strong> ${alert.current_price:.2f}</p>
            <p><strong>Marketplace:</strong> {alert.marketplace}</p>
            {"<p><strong>Precio anterior:</strong> $" + f"{alert.previous_price:.2f}</p>" if alert.previous_price else ""}
            {"<p><a href='" + alert.url + "'>Ver producto</a></p>" if alert.url else ""}
            <p><em>Fecha: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</em></p>
        </body>
        </html>
        """

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.email_from
        msg['To'] = ", ".join(self.email_to)

        msg.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.email_from, self.email_password)
            server.sendmail(self.email_from, self.email_to, msg.as_string())

        self.logger.info(f"Email enviado para alerta: {alert.id}")

    def _send_telegram(self, alert: Alert):
        """Envía notificación por Telegram"""
        import urllib.request
        import urllib.parse

        message = f"""
🔔 *Alerta de Precio*

📦 *Producto:* {alert.product_name}
💰 *Precio actual:* ${alert.current_price:.2f}
📊 *Condición:* {alert.trigger_condition}
🏪 *Marketplace:* {alert.marketplace}
"""
        if alert.previous_price:
            message += f"📉 *Precio anterior:* ${alert.previous_price:.2f}\n"

        if alert.url:
            message += f"\n🔗 [Ver producto]({alert.url})"

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id': self.telegram_chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }).encode()

        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req)

        self.logger.info(f"Telegram enviado para alerta: {alert.id}")

    def _send_webhook(self, alert: Alert, webhook_url: str):
        """Envía notificación a webhook"""
        import urllib.request

        data = json.dumps(alert.to_dict()).encode('utf-8')

        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)

        self.logger.info(f"Webhook enviado para alerta: {alert.id}")

    def add_handler(self, handler: Callable[[Alert], None]):
        """Agrega un handler personalizado para alertas"""
        self.custom_handlers.append(handler)

    def get_alerts(self, product_name: Optional[str] = None,
                   since: Optional[datetime] = None) -> List[Alert]:
        """Obtiene alertas con filtros opcionales"""
        alerts = self.alerts

        if product_name:
            alerts = [a for a in alerts if a.product_name == product_name]

        if since:
            alerts = [a for a in alerts if a.timestamp >= since]

        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)

    def _save_alerts(self):
        """Persiste alertas a disco"""
        if not self.storage_path:
            return

        alerts_file = self.storage_path / "alerts.json"

        # Mantener últimas 1000 alertas
        recent_alerts = self.alerts[-1000:]

        with open(alerts_file, 'w', encoding='utf-8') as f:
            json.dump([a.to_dict() for a in recent_alerts], f, indent=2)

    def _load_alerts(self):
        """Carga alertas desde disco"""
        if not self.storage_path:
            return

        alerts_file = self.storage_path / "alerts.json"

        if alerts_file.exists():
            try:
                with open(alerts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for item in data:
                    item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                    self.alerts.append(Alert(**item))

                self.logger.info(f"Cargadas {len(self.alerts)} alertas desde disco")
            except Exception as e:
                self.logger.error(f"Error cargando alertas: {e}")

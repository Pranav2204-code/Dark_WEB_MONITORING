"""
Alert notification system
"""
import asyncio
from typing import List, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger
import httpx

from ..core.config import settings
from ..models import ThreatModel, ThreatSeverity, NotificationChannel


class Notifier:
    """
    Handles sending notifications through various channels
    """

    def __init__(self):
        """Initialize notifier"""
        self.email_enabled = settings.ALERT_EMAIL_ENABLED
        self.slack_enabled = settings.ALERT_SLACK_ENABLED
        self.webhook_enabled = settings.ALERT_WEBHOOK_ENABLED

    async def send_alert(
        self,
        threat: ThreatModel,
        channels: List[NotificationChannel],
        recipients: Optional[List[str]] = None,
    ) -> bool:
        """
        Send alert through specified channels

        Args:
            threat: Threat to alert about
            channels: Notification channels to use
            recipients: Optional list of recipients (email addresses)

        Returns:
            True if at least one notification was sent successfully
        """
        success = False

        for channel in channels:
            try:
                if channel == NotificationChannel.EMAIL and self.email_enabled:
                    result = await self.send_email_alert(threat, recipients)
                    success = success or result

                elif channel == NotificationChannel.SLACK and self.slack_enabled:
                    result = await self.send_slack_alert(threat)
                    success = success or result

                elif channel == NotificationChannel.WEBHOOK and self.webhook_enabled:
                    result = await self.send_webhook_alert(threat)
                    success = success or result

            except Exception as e:
                logger.error(f"Failed to send alert via {channel}: {e}")

        return success

    async def send_email_alert(
        self,
        threat: ThreatModel,
        recipients: Optional[List[str]] = None,
    ) -> bool:
        """
        Send email alert

        Args:
            threat: Threat to alert about
            recipients: Email recipients

        Returns:
            True if email sent successfully
        """
        try:
            if not recipients:
                recipients = settings.ALERT_RECIPIENTS

            if not recipients:
                logger.warning("No email recipients configured")
                return False

            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{threat.severity.upper()}] Dark Web Alert: {threat.title}"
            msg['From'] = settings.SMTP_FROM
            msg['To'] = ', '.join(recipients)

            # Create email body
            html = self._create_email_html(threat)
            text = self._create_email_text(threat)

            msg.attach(MIMEText(text, 'plain'))
            msg.attach(MIMEText(html, 'html'))

            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)

            logger.info(f"Email alert sent for threat: {threat.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False

    def _create_email_html(self, threat: ThreatModel) -> str:
        """Create HTML email body"""
        severity_color = {
            ThreatSeverity.CRITICAL: "#dc3545",
            ThreatSeverity.HIGH: "#fd7e14",
            ThreatSeverity.MEDIUM: "#ffc107",
            ThreatSeverity.LOW: "#17a2b8",
            ThreatSeverity.INFO: "#6c757d",
        }.get(threat.severity, "#6c757d")

        iocs_html = ""
        if threat.intelligence and threat.intelligence.iocs:
            iocs_html = "<h3>Indicators of Compromise</h3><ul>"
            for ioc in threat.intelligence.iocs[:10]:
                iocs_html += f"<li><strong>{ioc.type}:</strong> {ioc.value}</li>"
            iocs_html += "</ul>"

        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .header {{ background-color: {severity_color}; color: white; padding: 20px; }}
                .content {{ padding: 20px; }}
                .severity {{ font-size: 24px; font-weight: bold; }}
                .metadata {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
                .threat-content {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="severity">{threat.severity.upper()} THREAT DETECTED</div>
                <h2>{threat.title}</h2>
            </div>
            <div class="content">
                <div class="metadata">
                    <p><strong>Source:</strong> {threat.source} - {threat.source_name}</p>
                    <p><strong>Type:</strong> {threat.threat_type}</p>
                    <p><strong>Discovered:</strong> {threat.discovered_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    {f'<p><strong>URL:</strong> <a href="{threat.url}">{threat.url}</a></p>' if threat.url else ''}
                    {f'<p><strong>Author:</strong> {threat.author}</p>' if threat.author else ''}
                </div>

                <h3>Content Preview</h3>
                <div class="threat-content">
                    <p>{threat.content[:500]}...</p>
                </div>

                {iocs_html}

                <p style="margin-top: 30px;">
                    <small>This is an automated alert from the Dark Web Monitoring Platform.</small>
                </p>
            </div>
        </body>
        </html>
        """

    def _create_email_text(self, threat: ThreatModel) -> str:
        """Create plain text email body"""
        return f"""
[{threat.severity.upper()}] DARK WEB THREAT DETECTED

Title: {threat.title}
Source: {threat.source} - {threat.source_name}
Type: {threat.threat_type}
Discovered: {threat.discovered_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
{f'URL: {threat.url}' if threat.url else ''}
{f'Author: {threat.author}' if threat.author else ''}

Content Preview:
{threat.content[:500]}...

---
This is an automated alert from the Dark Web Monitoring Platform.
        """

    async def send_slack_alert(self, threat: ThreatModel) -> bool:
        """
        Send Slack alert

        Args:
            threat: Threat to alert about

        Returns:
            True if alert sent successfully
        """
        try:
            if not settings.SLACK_WEBHOOK_URL:
                logger.warning("Slack webhook URL not configured")
                return False

            severity_color = {
                ThreatSeverity.CRITICAL: "danger",
                ThreatSeverity.HIGH: "warning",
                ThreatSeverity.MEDIUM: "#ffc107",
                ThreatSeverity.LOW: "good",
                ThreatSeverity.INFO: "#6c757d",
            }.get(threat.severity, "#6c757d")

            # Create Slack message
            message = {
                "channel": settings.SLACK_CHANNEL,
                "username": "Dark Web Monitor",
                "icon_emoji": ":warning:",
                "attachments": [
                    {
                        "color": severity_color,
                        "title": f"[{threat.severity.upper()}] {threat.title}",
                        "title_link": threat.url if threat.url else None,
                        "text": threat.content[:500] + "...",
                        "fields": [
                            {
                                "title": "Source",
                                "value": f"{threat.source} - {threat.source_name}",
                                "short": True
                            },
                            {
                                "title": "Type",
                                "value": threat.threat_type,
                                "short": True
                            },
                            {
                                "title": "Discovered",
                                "value": threat.discovered_at.strftime('%Y-%m-%d %H:%M:%S UTC'),
                                "short": True
                            },
                        ],
                        "footer": "Dark Web Monitoring Platform",
                        "ts": int(threat.discovered_at.timestamp())
                    }
                ]
            }

            # Send to Slack
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.SLACK_WEBHOOK_URL,
                    json=message,
                    timeout=10.0
                )
                response.raise_for_status()

            logger.info(f"Slack alert sent for threat: {threat.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False

    async def send_webhook_alert(self, threat: ThreatModel) -> bool:
        """
        Send webhook alert

        Args:
            threat: Threat to alert about

        Returns:
            True if webhook sent successfully
        """
        try:
            if not settings.WEBHOOK_URL:
                logger.warning("Webhook URL not configured")
                return False

            # Create webhook payload
            payload = {
                "event": "threat_detected",
                "timestamp": datetime.utcnow().isoformat(),
                "threat": {
                    "id": str(threat.id),
                    "title": threat.title,
                    "content": threat.content,
                    "url": threat.url,
                    "source": threat.source,
                    "source_name": threat.source_name,
                    "threat_type": threat.threat_type,
                    "severity": threat.severity,
                    "discovered_at": threat.discovered_at.isoformat(),
                }
            }

            # Add intelligence if available
            if threat.intelligence:
                payload["threat"]["intelligence"] = {
                    "sentiment": threat.intelligence.sentiment,
                    "keywords": threat.intelligence.keywords,
                    "iocs": [
                        {"type": ioc.type, "value": ioc.value}
                        for ioc in threat.intelligence.iocs[:20]
                    ]
                }

            # Send webhook
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "DarkWebMonitor/1.0"
            }

            if settings.WEBHOOK_SECRET:
                import hmac
                import hashlib
                import json
                signature = hmac.new(
                    settings.WEBHOOK_SECRET.encode(),
                    json.dumps(payload).encode(),
                    hashlib.sha256
                ).hexdigest()
                headers["X-Signature"] = signature

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.WEBHOOK_URL,
                    json=payload,
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()

            logger.info(f"Webhook alert sent for threat: {threat.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
            return False


# Global notifier instance
notifier = Notifier()

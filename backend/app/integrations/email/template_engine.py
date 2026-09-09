"""
AgriNova AI — Jinja2 Email Template Engine (V5.2).

Renders HTML and plain-text email bodies from Jinja2 templates stored
in ``backend/app/integrations/email/templates/``.

Design:
  - Templates are loaded from disk using a FileSystemLoader.
  - Each email type has an HTML template and an optional plain-text
    template (``<name>.html`` / ``<name>.txt``).
  - The engine auto-escapes HTML to prevent injection.
  - Template rendering failures return a graceful fallback instead
    of crashing the email pipeline.
"""

from __future__ import annotations

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape

logger = logging.getLogger(__name__)

# Templates live alongside this module
TEMPLATES_DIR = Path(__file__).parent / "templates"


class TemplateEngine:
    """Jinja2-backed email template renderer.

    Usage::

        engine = TemplateEngine()
        html = engine.render_html("market_alert", commodity="Tomato", price=2500)
        text = engine.render_text("market_alert", commodity="Tomato", price=2500)
    """

    def __init__(self, templates_dir: Path | str | None = None) -> None:
        template_path = Path(templates_dir) if templates_dir else TEMPLATES_DIR

        # Create templates directory if it doesn't exist
        template_path.mkdir(parents=True, exist_ok=True)

        self._env = Environment(
            loader=FileSystemLoader(str(template_path)),
            autoescape=select_autoescape(["html", "htm"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register global template variables available in every template
        self._env.globals.update({
            "app_name": "AgriNova AI",
            "support_email": "support@agrinova.ai",
            "unsubscribe_url": "#",  # Placeholder until settings UI
        })

        logger.info(
            "TemplateEngine initialized with templates from: %s",
            template_path,
        )

    @property
    def env(self) -> Environment:
        """Expose the Jinja2 environment for testing/inspection."""
        return self._env

    def render_html(self, template_name: str, **context: object) -> str:
        """Render an HTML email template.

        Args:
            template_name: Name without extension (e.g. ``"market_alert"``).
            **context: Template variables.

        Returns:
            Rendered HTML string, or a minimal fallback on error.
        """
        try:
            template = self._env.get_template(f"{template_name}.html")
            return template.render(**context)
        except TemplateNotFound:
            logger.warning(
                "HTML template '%s.html' not found, returning fallback",
                template_name,
            )
            return self._fallback_html(template_name, context)
        except Exception as exc:
            logger.error(
                "Error rendering template '%s.html': %s",
                template_name,
                exc,
                exc_info=True,
            )
            return self._fallback_html(template_name, context)

    def render_text(self, template_name: str, **context: object) -> str | None:
        """Render a plain-text email template.

        Returns ``None`` if no text template exists (HTML-only is fine).
        """
        try:
            template = self._env.get_template(f"{template_name}.txt")
            return template.render(**context)
        except TemplateNotFound:
            # No text version — this is expected, not an error
            return None
        except Exception as exc:
            logger.error(
                "Error rendering text template '%s.txt': %s",
                template_name,
                exc,
                exc_info=True,
            )
            return None

    def template_exists(self, template_name: str) -> bool:
        """Check if at least an HTML template exists for the given name."""
        try:
            self._env.get_template(f"{template_name}.html")
            return True
        except TemplateNotFound:
            return False

    @staticmethod
    def _fallback_html(template_name: str, context: dict) -> str:
        """Minimal inline HTML when the template file is missing."""
        title = context.get("title", context.get("subject", "Notification"))
        message = context.get("message", context.get("body", ""))
        return (
            f"<html><body>"
            f"<h2>{title}</h2>"
            f"<p>{message}</p>"
            f"<hr><small>AgriNova AI — template '{template_name}' unavailable</small>"
            f"</body></html>"
        )

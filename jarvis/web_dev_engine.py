from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class WebProject:
    html: str
    css: str
    javascript: str


class WebDevelopmentEngine:
    """Generates a safe starter web project from structured inputs."""

    def build_landing_page(self, title: str, description: str) -> WebProject:
        safe_title = self._escape(title.strip() or "JARVIS Project")
        safe_description = self._escape(description.strip() or "Built with JARVIS.")
        html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main class="container">
    <h1>{safe_title}</h1>
    <p>{safe_description}</p>
    <button id="cta">Get started</button>
  </main>
  <script src="script.js"></script>
</body>
</html>
"""
        css = """.container { max-width: 760px; margin: 12vh auto; padding: 2rem; font-family: system-ui, sans-serif; }"""
        javascript = """document.querySelector("#cta").addEventListener("click", () => alert("JARVIS web engine is ready."));"""
        return WebProject(html, css, javascript)

    @staticmethod
    def _escape(value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )

    def validate_html(self, html: str) -> list[str]:
        errors = []
        if not re.search(r"<!doctype html>", html, re.I):
            errors.append("Missing HTML5 doctype")
        for tag in ("html", "head", "body"):
            if not re.search(rf"<{tag}\b", html, re.I):
                errors.append(f"Missing <{tag}> element")
        return errors

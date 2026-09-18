from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urlparse
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class ResearchDocument:
    url: str
    title: str
    text: str


class _TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        value = " ".join(data.split())
        if not value:
            return
        if self.in_title:
            self.title_parts.append(value)
        else:
            self.parts.append(value)


class ResearchEngine:
    """Dependency-free URL reader with basic SSRF protection."""

    def __init__(self, timeout: float = 10.0, max_chars: int = 20000):
        self.timeout = timeout
        self.max_chars = max_chars

    @staticmethod
    def _validate_host(host: str) -> None:
        normalized = host.lower().rstrip(".")
        if normalized in {"localhost", "localhost.localdomain"}:
            raise ValueError("Local hosts are not allowed")
        try:
            addresses = {ipaddress.ip_address(info[4][0]) for info in socket.getaddrinfo(normalized, None)}
        except socket.gaierror as exc:
            raise ValueError("Could not resolve research host") from exc
        if any(address.is_private or address.is_loopback or address.is_link_local or address.is_reserved for address in addresses):
            raise ValueError("Private or local research hosts are not allowed")

    def fetch(self, url: str) -> ResearchDocument:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("Only absolute HTTP(S) URLs are supported")
        self._validate_host(parsed.hostname)

        request = Request(url, headers={"User-Agent": "JARVIS-Research/1.0"})
        with urlopen(request, timeout=self.timeout) as response:
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                raise ValueError("Research engine currently supports HTML pages only")
            raw = response.read(self.max_chars * 4)
            charset = response.headers.get_content_charset() or "utf-8"

        parser = _TextParser()
        parser.feed(raw.decode(charset, errors="replace"))
        text = re.sub(r"\s+", " ", " ".join(parser.parts)).strip()
        return ResearchDocument(
            url=url,
            title=" ".join(parser.title_parts).strip() or parsed.netloc,
            text=text[: self.max_chars],
        )

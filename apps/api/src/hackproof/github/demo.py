import ipaddress
import re
from urllib.parse import urljoin, urlparse

import httpx

from hackproof.github.models import Ref
from hackproof.github.refs import extract_refs

SCRIPT_SRC = re.compile(r"""<script[^>]+src=["']([^"']+\.m?js)[^"']*["']""", re.IGNORECASE)
MAX_BUNDLES = 5
MAX_BYTES = 3_000_000


def is_public_http(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return False
    if parsed.hostname == "localhost" or parsed.hostname.endswith(".local"):
        return False
    try:
        address = ipaddress.ip_address(parsed.hostname)
    except ValueError:
        return True
    return address.is_global


async def _fetch_text(http: httpx.AsyncClient, url: str) -> str:
    if not is_public_http(url):
        return ""
    try:
        response = await http.get(url, follow_redirects=False)
    except httpx.HTTPError:
        return ""
    if response.status_code != 200 or len(response.content) > MAX_BYTES:
        return ""
    return response.text


async def scan_demo(http: httpx.AsyncClient, url: str) -> list[Ref]:
    html = await _fetch_text(http, url)
    bundles = [urljoin(url, src) for src in SCRIPT_SRC.findall(html)[:MAX_BUNDLES]]
    refs = list(extract_refs(html, url))
    for bundle in bundles:
        refs.extend(extract_refs(await _fetch_text(http, bundle), bundle))
    return refs

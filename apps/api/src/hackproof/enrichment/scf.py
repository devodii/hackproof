import re
import time
import urllib.robotparser
from typing import List, Optional
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, HttpUrl


class ScfAward(BaseModel):
    round_name: str
    status: Optional[str] = None
    amount_usd: Optional[float] = None


class ScfProject(BaseModel):
    name: str
    slug: str
    url: HttpUrl
    team_members: List[str] = []
    github_handles: List[str] = []
    awards: List[ScfAward] = []
    website: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None

    @property
    def total_awarded_usd(self) -> Optional[float]:
        amounts = [a.amount_usd for a in self.awards if a.amount_usd is not None]
        if not amounts:
            return None
        return float(sum(amounts))


BASE_URL = "https://communityfund.stellar.org"
ROBOTS_URL = f"{BASE_URL}/robots.txt"
REQUEST_INTERVAL = 1.0


def _robots_allowed(path: str = "/") -> bool:
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(ROBOTS_URL)
        rp.read()
        return rp.can_fetch("*", urljoin(BASE_URL, path))
    except Exception:
        return True


def _fetch(url: str, client: httpx.Client) -> str:
    if not _robots_allowed(url.replace(BASE_URL, "")):
        raise PermissionError(f"robots.txt disallows {url}")
    time.sleep(REQUEST_INTERVAL)
    resp = client.get(url)
    resp.raise_for_status()
    return resp.text


def _parse_project(html: str, url: str) -> ScfProject:
    # Minimal, regex-based extraction resilient to fixture HTML
    name_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
    name = name_match.group(1).strip() if name_match else "Unknown"

    slug_match = re.search(r"/projects/([a-zA-Z0-9\-_]+)", url)
    slug = slug_match.group(1) if slug_match else url.rstrip("/").split("/")[-1]

    # team members / github handles
    handles = re.findall(r"github\.com/([A-Za-z0-9\-_]+)", html)
    # dedupe preserving order
    seen = set()
    github_handles = []
    for h in handles:
        if h.lower() not in seen:
            seen.add(h.lower())
            github_handles.append(h)

    team_members = re.findall(r'data-team-member="([^"]+)"', html)
    if not team_members:
        team_members = re.findall(r'class="team-member"[^>]*>([^<]+)</', html)

    # awards
    awards = []
    for m in re.finditer(r"round[:\s]*([^<]+)</[^>]*>.*?status[:\s]*([^<]+)</[^>]*>.*?amount[:\s]*\$?([\d,\.]+)", html, re.I | re.S):
        try:
            amt = float(m.group(3).replace(",", ""))
        except Exception:
            amt = None
        awards.append(ScfAward(round_name=m.group(1).strip(), status=m.group(2).strip(), amount_usd=amt))

    # fallback: simpler award lines
    if not awards:
        for m in re.finditer(r"\$([\d,\.]+)", html):
            pass

    website_match = re.search(r'href="(https?://(?!github\.com)[^"]+)"[^>]*>\s*(?:Website|Site)', html, re.I)
    website = website_match.group(1) if website_match else None

    github_match = re.search(r'href="(https://github\.com/[^"]+)"', html, re.I)
    github_url = github_match.group(1) if github_match else None

    return ScfProject(
        name=name,
        slug=slug,
        url=url,
        team_members=team_members,
        github_handles=github_handles,
        awards=awards,
        website=website,
        github_url=github_url,
    )


def crawl_project(url: str, client: Optional[httpx.Client] = None) -> ScfProject:
    own = client is None
    if own:
        client = httpx.Client(timeout=30.0, follow_redirects=True)
    try:
        html = _fetch(url, client)
        return _parse_project(html, url)
    finally:
        if own:
            client.close()


def crawl_index(project_urls: List[str]) -> List[ScfProject]:
    results = []
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        for u in project_urls:
            results.append(crawl_project(u, client=client))
    return results
import re
import base64
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

SITE_URL = "https://amwaleh.github.io/"
LINKEDIN_URL = "https://www.linkedin.com/in/mwaleh/"


PUBLIC_ASSETS = (
    "profile.md", "robots.txt", "sitemap.xml", "llms.txt",
    "Career-Journey-2016-2026.svg",
    "Mwaleh-Muturi-Master-CV-2026-11-22.pdf",
    "assets/logos/andela.png",
    "assets/logos/pbp.png",
    "assets/logos/brck.png",
    "assets/logos/microsoft.png",
    "assets/logos/metalab.png",
    "assets/logos/pluralsight.png",
    "assets/logos/fixico.png",
    "assets/logos/scotch.png",
)


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.references = []
        self.methods = 0
        self.schemas = []
        self.schema_text = None
        self.metadata = {}
        self.canonical = None
        self.proof_roles = []
        self.primary_cv = None
        self.secondary_linkedin = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f"Duplicate element ID: {attrs['id']}"
            self.ids.add(attrs["id"])
        if tag == "script":
            assert attrs.get("type") == "application/ld+json" and "src" not in attrs, (
                "Only non-executing inline structured data is permitted."
            )
            self.schema_text = []
        if tag == "meta":
            self.metadata[attrs.get("name", attrs.get("http-equiv", ""))] = attrs.get("content")
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if tag == "details" and attrs.get("class") == "capability-method":
            assert "open" not in attrs, "Methods must be collapsed by default."
            self.methods += 1
        if tag == "li" and attrs.get("class") == "leadership-proof":
            self.proof_roles.append(attrs.get("data-proof"))
        if tag == "a" and attrs.get("class") == "primary-action":
            self.primary_cv = attrs.get("href")
        if tag == "a" and attrs.get("class") == "secondary-action":
            self.secondary_linkedin = attrs.get("href")
        if tag == "img":
            assert "alt" in attrs, "Images need an alt attribute."
            assert attrs["alt"] or attrs.get("class") == "company-logo", (
                "Only decorative company marks may have empty alternative text."
            )
        for name in ("src", "href"):
            if name in attrs:
                self.references.append(attrs[name])

    def handle_data(self, data):
        if self.schema_text is not None:
            self.schema_text.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.schema_text is not None:
            self.schemas.append("".join(self.schema_text))
            self.schema_text = None


def check_site(root):
    html = (root / "index.html").read_text()
    assert "Content-Security-Policy" in html
    assert not re.search(
        r"Connect[-s]|evidence_quote|additional_evidence|source-index|master-cv-data"
        r"|career-journey-data|interview-evidence|Interview-Capabilities|private-sources"
        r"|Interview_QA|Interview_Questions|sharepoint\.com|outlook\.office\.com|/home/",
        html,
        re.IGNORECASE,
    ), "Private source material is not a public presentation."
    page = Page()
    page.feed(html)
    assert page.methods == 7, "All seven capability methods must remain collapsible."
    assert page.proof_roles == ["microsoft", "pbp-director"], "Recent leadership precedes the full journey."
    assert page.primary_cv == "Mwaleh-Muturi-Master-CV-2026-11-22.pdf"
    assert page.secondary_linkedin == LINKEDIN_URL
    assert {"career", "journey", "impact", "engagements"}.issubset(page.ids)
    assert page.canonical == SITE_URL
    assert page.metadata.get("description")
    assert len(page.schemas) == 1
    schema = json.loads(page.schemas[0])
    assert schema["@type"] == "ProfilePage" and schema["url"] == SITE_URL
    person = schema["mainEntity"]
    assert person["@type"] == "Person" and person["name"] == "Mwaleh Muturi"
    assert person["jobTitle"] == "Senior Engineering Manager", "CTO is a target role, not a title held."
    assert LINKEDIN_URL in person["sameAs"] and LINKEDIN_URL in page.references
    digest = base64.b64encode(hashlib.sha256(page.schemas[0].encode()).digest()).decode()
    assert "'sha256-" + digest + "'" in page.metadata["Content-Security-Policy"]
    assert "Interested in Engineering Manager, Director of Engineering and CTO opportunities" in html
    assert "across Kenya, East Africa and EMEA." in html
    for reference in page.references:
        url = urlsplit(reference)
        if url.scheme or url.netloc:
            assert reference in {SITE_URL, LINKEDIN_URL, "https://github.com/amwaleh"}, reference
            continue
        if url.path:
            asset = (root / unquote(url.path)).resolve()
            assert asset.is_relative_to(root.resolve()), f"Asset escapes the site: {reference}"
            assert asset.is_file(), f"Missing public asset: {reference}"
            assert asset.suffix.lower() in {".pdf", ".svg", ".png", ".md"}, reference
        elif url.fragment:
            assert unquote(url.fragment) in page.ids, f"Broken section link: {reference}"
    robots = RobotFileParser()
    robots.parse((root / "robots.txt").read_text().splitlines())
    for bot in ("Googlebot", "bingbot", "OAI-SearchBot", "PerplexityBot"):
        assert robots.can_fetch(bot, SITE_URL), f"Search crawler blocked: {bot}"
    assert robots.site_maps() == [SITE_URL + "sitemap.xml"]
    locations = ET.parse(root / "sitemap.xml").findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    assert [location.text for location in locations] == [SITE_URL]
    assert SITE_URL + "profile.md" in (root / "llms.txt").read_text()
    for name in ("profile.md", "llms.txt"):
        text = (root / name).read_text()
        assert "Mwaleh Muturi" in text and "East Africa" in text and "EMEA" in text
        assert not re.search(r"evidence_quote|additional_evidence|sharepoint\.com|outlook\.office\.com|DOCX paragraph", text)
    allowed = {
        "index.html", ".gitignore", ".nojekyll", "README.md",
        "tools/export_site.py", "tools/check_site.py", *PUBLIC_ASSETS,
    }
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if not path.is_file() or any(part in {".git", "__pycache__"} for part in relative.parts):
            continue
        assert not path.is_symlink(), f"Do not publish symlinks: {path.name}"
        assert relative.as_posix() in allowed, f"Unapproved public file: {relative}"
    print("Public links, local assets, disclosure defaults and source-exclusion checks passed.")


if __name__ == "__main__":
    check_site(Path(__file__).resolve().parents[1])

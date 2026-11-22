import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


PUBLIC_ASSETS = (
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

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f"Duplicate element ID: {attrs['id']}"
            self.ids.add(attrs["id"])
        if tag == "script":
            raise AssertionError("The public profile must remain script-free.")
        if tag == "details" and attrs.get("class") == "capability-method":
            assert "open" not in attrs, "Methods must be collapsed by default."
            self.methods += 1
        if tag == "img":
            assert "alt" in attrs, "Images need an alt attribute."
            assert attrs["alt"] or attrs.get("class") == "company-logo", (
                "Only decorative company marks may have empty alternative text."
            )
        for name in ("src", "href"):
            if name in attrs:
                self.references.append(attrs[name])


def check_site(root):
    html = (root / "index.html").read_text()
    assert "Content-Security-Policy" in html
    assert not re.search(
        r"Connect[-s]|evidence_quote|additional_evidence|source-index|master-cv-data"
        r"|career-journey-data|sharepoint\.com|outlook\.office\.com|/home/",
        html,
        re.IGNORECASE,
    ), "Private source material is not a public presentation."
    page = Page()
    page.feed(html)
    assert page.methods == 7, "All seven capability methods must remain collapsible."
    for reference in page.references:
        url = urlsplit(reference)
        assert not url.scheme and not url.netloc, f"Unexpected external resource: {reference}"
        if url.path:
            asset = (root / unquote(url.path)).resolve()
            assert asset.is_relative_to(root.resolve()), f"Asset escapes the site: {reference}"
            assert asset.is_file(), f"Missing public asset: {reference}"
            assert asset.suffix.lower() in {".pdf", ".svg", ".png"}, reference
        elif url.fragment:
            assert unquote(url.fragment) in page.ids, f"Broken section link: {reference}"
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

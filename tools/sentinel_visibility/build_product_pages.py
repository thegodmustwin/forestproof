"""Render the public product guide and research explanation without private data."""

from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent
PAGES = {"guide": ROOT / "guide.html", "research": ROOT / "research.html"}
STYLES = ROOT / "assets" / "product-pages.css"


def render_product_page(name: str) -> str:
    """Accept an exact published page name, never a filesystem or URL path."""
    if name not in PAGES:
        raise ValueError("Unknown public product page")
    return Template(PAGES[name].read_text(encoding="utf-8")).substitute(
        styles=STYLES.read_text(encoding="utf-8")
    )

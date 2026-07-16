import re
from pathlib import Path

from fastapi.testclient import TestClient

from phraseframe.main import app

FORBIDDEN_PATTERNS = [
    r"PhraseFrame users (gain|improve)",
    r"understand(?:ing)? improved by \d+%",
    r"ADHD",
    r"effortless.{0,20}500\s*WPM",
    r"AI understood your book",
    r"Prove you understood",
]

PUBLIC_PAGE = (
    Path(__file__).resolve().parents[1] / "src" / "phraseframe" / "web" / "templates" / "index.html"
)


def test_home_page_forbidden_claims_absent() -> None:
    with TestClient(app) as test_client:
        html = test_client.get("/").text
    for pattern in FORBIDDEN_PATTERNS:
        assert re.search(pattern, html, re.IGNORECASE) is None, pattern


def test_public_percentages_have_attribution_or_product_rule() -> None:
    html = PUBLIC_PAGE.read_text(encoding="utf-8")
    percentages = re.findall(r"\d{1,3}%", html)
    assert percentages, "expected at least one attributed percentage on the landing page"
    science_block = html.split('class="science"', 1)[1]
    for match in re.finditer(r"\d{1,3}%", science_block):
        window = science_block[max(0, match.start() - 120) : match.end() + 120]
        has_context = any(
            token in window.lower()
            for token in (
                "study",
                "studies",
                "lab",
                "classic",
                "research",
                "product rule",
                "self-check",
                "roediger",
                "szpunar",
                "cepeda",
            )
        )
        assert has_context, f"missing attribution near {match.group(0)}: {window!r}"


def test_hero_uses_loop_narrative_not_overclaim() -> None:
    with TestClient(app) as test_client:
        html = test_client.get("/").text
    assert "Read with focus. Check what stuck. Keep it." in html
    assert "self-check" in html.lower() or "Self-check" in html
    assert 'id="science"' in html
    assert html.count("<article>") >= 5

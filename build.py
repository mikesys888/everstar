"""Builds the Everstar website draft.

Each file in src/pages/ starts with three header lines:
    title: Page title
    nav: home|services|projects|about|contact
    ---
followed by the page's <main> content. This script wraps every page with the
shared header, footer, stylesheet and script, and writes <name>.html here.

Run:  python build.py
"""
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
CSS = (SRC / "site.css").read_text(encoding="utf-8")

NAV = [
    ("services", "services.html", "Services"),
    ("projects", "projects.html", "Projects"),
    ("about", "about.html", "About"),
    ("contact", "contact.html", "Contact"),
]

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700'
    '&family=Open+Sans:wght@400;600&family=IBM+Plex+Mono:wght@500&display=swap">'
)

BASE_CSS = "body{margin:0}img{max-width:100%}[hidden]{display:none!important}\n"

DRAFT = (
    '<div class="draft"><div class="wrap">Draft for review. Not the live website. '
    "Content taken from the July 2025 company presentation, business card and everstar.sg.</div></div>"
)

FOOTER = """<footer class="site">
  <div class="wrap">
    <span>© 2026 Everstar Engineering &amp; Services Pte Ltd · BRN 200819367H</span>
    <span>+65 6862 3563 · mail@everstar.com.sg</span>
    <span>Singapore · Malaysia · Indonesia</span>
  </div>
</footer>"""

FORM_JS = """<script>
(function () {
  var f = document.getElementById('enq');
  if (!f) return;
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var msg = document.getElementById('form-msg');
    var name = document.getElementById('f-name'), email = document.getElementById('f-email');
    if (!name.value.trim()) { msg.textContent = 'Enter your name.'; name.focus(); return; }
    if (!email.checkValidity() || !email.value.trim()) { msg.textContent = 'Enter a valid work email, like name@company.com.'; email.focus(); return; }
    msg.textContent = 'Draft only: this form is not connected yet, so nothing was sent.';
  });
})();
</script>"""


def links(active):
    out = []
    for key, href, label in NAV:
        cur = ' aria-current="page"' if key == active else ""
        out.append(f'<a href="{href}"{cur}>{label}</a>')
    return "\n      ".join(out)


def header(active):
    return f"""<header class="site">
  <div class="wrap">
    <a class="logo" href="index.html" aria-label="Everstar home"><img src="img/logo.svg" alt="everstar" width="117" height="40"></a>
    <nav class="main" aria-label="Main">
      {links(active)}
    </nav>
    <details class="menu">
      <summary aria-label="Open menu">Menu</summary>
      <nav aria-label="Main (mobile)">
      <a href="index.html"{' aria-current="page"' if active == 'home' else ''}>Home</a>
      {links(active)}
      </nav>
    </details>
    <a class="btn primary" href="contact.html">Request a quote</a>
  </div>
</header>"""


def build(path):
    raw = path.read_text(encoding="utf-8")
    head, body = raw.split("\n---\n", 1)
    meta = dict(line.split(":", 1) for line in head.strip().splitlines())
    title = meta["title"].strip()
    active = meta["nav"].strip()
    parts = [
        f"<title>{title}</title>",
        '<meta name="claude:viewport-fit-sides" content="cover">',
        FONTS,
        f"<style>\n{BASE_CSS}{CSS}</style>",
        "",
        DRAFT,
        "",
        header(active),
        "",
        body.strip(),
        "",
        FOOTER,
        "",
        FORM_JS,
        "",
    ]
    page = "\n".join(parts)
    if path.stem != "index":
        # Only the main page gets a document skeleton added at publish time.
        page = (
            '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + page.replace("\n\n" + DRAFT, "\n</head>\n<body>\n" + DRAFT, 1)
            + "</body>\n</html>\n"
        )
    out = ROOT / f"{path.stem}.html"
    out.write_text(page, encoding="utf-8")
    print(f"built {out.name} ({len(page):,} bytes)")


if __name__ == "__main__":
    for p in sorted((SRC / "pages").glob("*.html")):
        build(p)

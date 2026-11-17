"""Builds the Everstar website draft.

Each file in src/pages/ starts with three header lines:
    title: Page title
    nav: home|services|projects|about|team|contact
    ---
followed by the page's <main> content. This script wraps every page with the
shared header, footer, stylesheet and script, and writes <name>.html here.
The marker {{ORG_CHART}} is replaced with the organisation chart built from
src/team.json.

Run:  python build.py
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
CSS = (SRC / "site.css").read_text(encoding="utf-8")
TEAM = json.loads((SRC / "team.json").read_text(encoding="utf-8"))

NAV = [
    ("services", "services.html", "Services"),
    ("projects", "projects.html", "Projects"),
    ("about", "about.html", "About"),
    ("team", "team.html", "Our Team"),
    ("contact", "contact.html", "Contact"),
]


def initials(name):
    parts = [p for p in name.replace(".", " ").split() if p]
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()


def avatar(p, size):
    if p.get("photo"):
        return (f'<img class="av av-{size}" src="img/team/{escape(p["photo"])}.jpg?v=3" '
                f'alt="" width="240" height="320"' + ('' if size == 'lg' else ' loading="lazy"') + '>')
    return f'<span class="av av-{size} av-initials" aria-hidden="true">{escape(initials(p["name"]))}</span>'


def person(p, size, tag="div", cls="person-chip"):
    return (f'<{tag} class="{cls}">{avatar(p, size)}<span class="pc-text">'
            f'<b>{escape(p["name"])}</b><span>{escape(p["role"])}</span></span></{tag}>')


def org_chart():
    leaders = TEAM["leaders"]
    depts = TEAM["departments"]
    count = len(leaders) + sum(1 + len(d["members"]) for d in depts)
    out = ['<div class="org" role="group" aria-label="Organisation chart">', '<div class="org-top">']
    for i, p in enumerate(leaders):
        if i:
            out.append('<span class="org-vline" aria-hidden="true"></span>')
        out.append(person(p, "lg", cls="leader"))
    out.append('<span class="org-vline" aria-hidden="true"></span>')
    out.append(f'<span class="org-hub">{len(depts)} teams · {count} people</span>')
    out.append("</div>")
    out.append('<div class="org-depts">')
    for d in depts:
        out.append('<section class="dept">')
        out.append(f'<h3 class="dept-name">{escape(d["name"])}</h3>')
        out.append(person(d["lead"], "md", cls="dept-lead"))
        if d["members"]:
            out.append('<ul class="dept-members">')
            for m in d["members"]:
                out.append(person(m, "sm", tag="li", cls="member"))
            out.append("</ul>")
        out.append("</section>")
    out.append("</div></div>")
    return "\n".join(out)

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700'
    '&family=Open+Sans:wght@400;600&family=IBM+Plex+Mono:wght@500&display=swap">'
)

BASE_CSS = "body{margin:0}img{max-width:100%}[hidden]{display:none!important}\n"

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
  var FALLBACK = 'Please email mail@everstar.com.sg or call +65 6862 3563.';
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var msg = document.getElementById('form-msg');
    var btn = document.getElementById('f-send');
    var name = document.getElementById('f-name'), email = document.getElementById('f-email');
    if (!name.value.trim()) { msg.textContent = 'Enter your name.'; name.focus(); return; }
    if (!email.checkValidity() || !email.value.trim()) { msg.textContent = 'Enter a valid work email, like name@company.com.'; email.focus(); return; }
    var data = {};
    new FormData(f).forEach(function (v, k) { data[k] = v; });
    btn.disabled = true; btn.textContent = 'Sending…'; msg.textContent = '';
    fetch('/api/enquiry', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
      .then(function (out) {
        if (out.ok) {
          f.reset();
          msg.textContent = 'Thank you. Your enquiry has been sent and our team will reply by email.';
        } else if (out.error && out.error.indexOf(' ') > -1) {
          msg.textContent = out.error;
        } else {
          msg.textContent = 'Sorry, your enquiry could not be sent. ' + FALLBACK;
        }
      })
      .catch(function () { msg.textContent = 'Sorry, your enquiry could not be sent. Check your connection, or ' + FALLBACK.charAt(0).toLowerCase() + FALLBACK.slice(1); })
      .then(function () { btn.disabled = false; btn.textContent = 'Send enquiry'; });
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
    body = body.replace("{{ORG_CHART}}", org_chart())
    parts = [
        f"<title>{title}</title>",
        '<meta name="claude:viewport-fit-sides" content="cover">',
        FONTS,
        f"<style>\n{BASE_CSS}{CSS}</style>",
        "</head>",
        "<body>",
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
    # Every page is a complete document, so it works on any static host.
    page = (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + page
        + "</body>\n</html>\n"
    )
    out = ROOT / f"{path.stem}.html"
    out.write_text(page, encoding="utf-8")
    print(f"built {out.name} ({len(page):,} bytes)")


if __name__ == "__main__":
    for p in sorted((SRC / "pages").glob("*.html")):
        build(p)

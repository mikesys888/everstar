# Everstar website

Static website for Everstar Engineering & Services Pte Ltd.

- Pages: `index.html`, `services.html`, `projects.html`, `about.html`, `contact.html`
- Edit the sources in `src/` (`src/site.css` for shared styles, `src/pages/*.html` for page content), then rebuild:

```bash
python build.py
```

The built `.html` files at the repo root are what gets deployed (Vercel, no build step).

#!/usr/bin/env python3
"""Renderizza un template HTML in PNG 1080x1350 sostituendo i segnaposto {{CHIAVE}}.

Uso:
  python3 scripts/render.py --template promo --data post.json --out posts/2026-10-21.png

post.json: {"ETICHETTA": "Offerta", "GRANDE": "-20%", "TITOLO": "...", "NOTA": "..."}
I valori sono testo puro (escapato); un "\n" nel valore diventa un a capo.
Segnaposto non forniti vengono svuotati e segnalati a stderr.
"""
import argparse, html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")

def fill(template_html: str, data: dict) -> str:
    missing = set()
    def sub(m):
        key = m.group(1)
        if key not in data:
            missing.add(key)
            return ""
        return html.escape(str(data[key])).replace("\n", "<br>")
    out = PLACEHOLDER.sub(sub, template_html)
    if missing:
        print(f"[render] segnaposto senza valore: {', '.join(sorted(missing))}", file=sys.stderr)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True, help="nome file in templates/ senza .html")
    ap.add_argument("--data", required=True, help="file JSON con i valori dei segnaposto")
    ap.add_argument("--out", required=True, help="PNG di destinazione")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1350)
    a = ap.parse_args()

    tpl_path = ROOT / "templates" / f"{a.template}.html"
    data = json.loads(Path(a.data).read_text(encoding="utf-8"))
    filled = fill(tpl_path.read_text(encoding="utf-8"), data)
    tmp = ROOT / "templates" / f"_render_{a.template}.html"
    tmp.write_text(filled, encoding="utf-8")

    from playwright.sync_api import sync_playwright
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": a.width, "height": a.height}, device_scale_factor=1)
        pg.goto(tmp.as_uri())
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        pg.screenshot(path=str(out), full_page=False)
        b.close()
    tmp.unlink(missing_ok=True)
    print(out)

if __name__ == "__main__":
    main()

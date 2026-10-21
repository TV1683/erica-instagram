#!/usr/bin/env python3
"""Genera lo sfondo fotografico di un post con l'API Images di OpenAI e lo salva come JPG verticale.

Uso:
  python3 scripts/genera_sfondo.py --key /percorso/openai.key --prompt "..." --out posts/2026-10-22-foto.jpg

Il prompt va scritto in inglese, descrittivo, senza testi, loghi o marchi; lo script aggiunge da solo le
regole fisse di stile (fotorealistico, verticale, soggetto in alto, zona bassa più scura).
Costo indicativo: 0,10-0,20 EUR per immagine (qualità "medium", 1024x1536).
"""
import argparse, base64, json, sys, urllib.request
from pathlib import Path

STILE = (" Photorealistic editorial photograph, natural light, shallow depth of field, vertical 2:3 framing, "
         "main subject in the upper two thirds of the frame, lower third darker and uncluttered so a text "
         "panel can be placed over it. No text, no letters, no logos, no brand names, no license plates, "
         "no people's faces. Realistic European setting.")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True, help="file con la chiave API (una riga)")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--quality", default="medium", choices=["low", "medium", "high"])
    a = ap.parse_args()

    key = Path(a.key).read_text(encoding="utf-8").strip()
    body = json.dumps({
        "model": "gpt-image-1",
        "prompt": a.prompt.strip() + STILE,
        "size": "1024x1536",
        "quality": a.quality,
        "n": 1,
        "output_format": "jpeg",
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        print(f"[genera_sfondo] errore HTTP {e.code}: {e.read()[:400].decode(errors='replace')}", file=sys.stderr)
        sys.exit(1)

    img = base64.b64decode(data["data"][0]["b64_json"])
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(img)
    print(out)

if __name__ == "__main__":
    main()

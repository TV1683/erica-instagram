#!/usr/bin/env python3
"""Genera lo sfondo fotografico di un post con FLUX.1 Krea su Hugging Face (gratuito, quota ZeroGPU giornaliera).

Uso:
  python3 scripts/genera_sfondo_hf.py --key ../erica-segreti/hf.key --prompt "..." --out posts/2026-10-25-foto.jpg

Il prompt va in inglese (max ~70 parole), descrittivo, con termini fotografici; lo script aggiunge le regole fisse.
Se FLUX non risponde o la quota è finita prova Qwen-Image; se fallisce anche quello esce con codice 2
(il copione allora ripiega sulla foto Unsplash).
Richiede: pip install --break-system-packages gradio_client pillow
Domini da consentire: huggingface.co, *.hf.space
"""
import argparse, shutil, sys
from pathlib import Path

STILE = (" Editorial automotive photography, natural light, realistic textures, vertical composition, "
         "main subject in the upper two thirds, lower third darker and uncluttered. "
         "No text, no letters, no logos, no brand names, no license plates, no faces.")

SPAZI = [
    ("mcp-tools/FLUX.1-Krea-dev", "/infer",
     lambda p: dict(prompt=p, seed=0, randomize_seed=True, width=832, height=1040, guidance_scale=4.5, num_inference_steps=28)),
    ("mcp-tools/Qwen-Image", "/generate_image",
     lambda p: dict(prompt=p, seed=0, randomize_seed=True, aspect_ratio="3:4",
                    negative_prompt="text, letters, watermark, logo, brand name, license plate, blurry, low resolution, cartoon, illustration",
                    guidance_scale=4.0, num_inference_steps=24)),
]

def salva(risultato, out: Path):
    # gradio restituisce un percorso file, oppure una tupla (file, seed), oppure un dict con 'path'
    r = risultato[0] if isinstance(risultato, (list, tuple)) else risultato
    if isinstance(r, dict):
        r = r.get("path") or r.get("url")
    from PIL import Image
    im = Image.open(r).convert("RGB")
    # porta a 1080x1350 (4:5) con ritaglio centrato verso l'alto
    w, h = im.size
    target = 1080 / 1350
    if w / h > target:
        nw = int(h * target); x = (w - nw) // 2; im = im.crop((x, 0, x + nw, h))
    else:
        nh = int(w / target); im = im.crop((0, 0, w, nh))
    im = im.resize((1080, 1350), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, quality=92)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    token = Path(a.key).read_text(encoding="utf-8").strip()
    from gradio_client import Client
    ultimo = None
    for spazio, api, parametri in SPAZI:
        try:
            c = Client(spazio, token=token, verbose=False)
            res = c.predict(**parametri(a.prompt.strip() + STILE), api_name=api)
            salva(res, Path(a.out))
            print(f"{a.out} (generata con {spazio})")
            return
        except Exception as e:  # quota finita, Space in pausa, parametri cambiati
            ultimo = e
            print(f"[genera_sfondo_hf] {spazio} non disponibile: {str(e)[:200]}", file=sys.stderr)
    print(f"[genera_sfondo_hf] nessun generatore disponibile: {ultimo}", file=sys.stderr)
    sys.exit(2)

if __name__ == "__main__":
    main()

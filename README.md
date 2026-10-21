# erica-instagram

Automazione dei post Instagram di E.RIC.A (Emporio Ricambi Auto, Conegliano).
Il repo è pubblico perché le immagini dei post vengono servite da qui a Metricool.

## Come funziona

Ogni 2 giorni un'attività pianificata di Claude:

1. legge `calendario.json` (ricorrenze e argomenti sempreverdi) e `registro.json` (post già fatti);
2. cerca notizie automotive recenti e sceglie un argomento rispettando il mix
   editoriale (ricambi/accessori ~60%, automotive ~30%, generale ~10%);
3. sceglie il template adatto da `templates/templates.json`, scrive i testi e la didascalia;
4. renderizza il PNG 1080×1350 con `scripts/render.py` e lo salva in `posts/AAAA-MM-GG.png`;
5. fa commit su questo repo e crea su Metricool una bozza **da approvare**
   con l'URL raw dell'immagine;
6. aggiorna `registro.json`.

## Struttura

```
templates/        HTML dei template + _base.css (font, colori) + templates.json (catalogo)
fonts/            Poppins e Montserrat (gli stessi del sito ericaricambi.it)
posts/            PNG generati, uno per post
scripts/render.py template + JSON → PNG
calendario.json   ricorrenze stagionali e argomenti sempreverdi
registro.json     storico dei post (argomento, template, stato)
```

## Aggiungere o sostituire un template

Un template è un file `templates/<nome>.html`:

- dimensione fissa 1080×1350 (`<div class="post">`), può includere `_base.css`
  per font e colori del brand (`var(--rosso)`, `var(--blu)`, `var(--navy)`);
- i testi variabili sono segnaposto `{{CHIAVE}}` in maiuscolo
  (es. `{{TITOLO}}`, `{{TESTO}}`); vengono sostituiti con testo puro,
  un `\n` nel valore diventa un a capo;
- immagini e font vanno referenziati con percorsi relativi dentro al repo
  (niente URL esterni: il rendering non ha accesso a internet).

Poi va aggiunta una voce in `templates/templates.json` con i campi, i limiti
di caratteri e una riga `usa_per` che spiega quando usarlo.

## Rendering manuale

```
pip install playwright && playwright install chromium
python3 scripts/render.py --template consiglio --data esempio.json --out posts/prova.png
```

# DHLAB – digital tekstanalyse

Dette repoet inneholder koden som lager jupyterboka som kjører på https://nationallibraryofnorway.github.io/digital_tekstanalyse/

## Installasjon

### Med uv

```bash
uv sync
```

### Med Poetry

```bash
poetry install
```

### Med venv og pip

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

## Bruk
Start Jupyter og åpne notatbøkene i `tutorial/` eller `cookbook/`:

```bash
uv run jupyter notebook
```

Eller bruk [Binder](https://mybinder.org/v2/gh/NationalLibraryOfNorway/digital_tekstanalyse/update_binder_link) for å kjøre notatbøkene i nettleseren uten lokal installasjon.

## Bygg jupyter-book
```bash
uv run jupyter-book build .
```
Deretter kan du åpne `_build/html/index.html` i browseren. 

## Deploy

Bygg og deploy til gh-pages med ghp-import:

```bash
uv run jupyter-book build .
uv run ghp-import -n -p -f _build/html
```

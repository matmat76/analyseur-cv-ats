# Analyseur CV / ATS

Contexte complet : `BRIEF.md`.

## Installation

```
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

## Ingestion ESCO (Phase A)

```
source .venv/bin/activate
python backend/esco_ingest.py
```

Télécharge (une seule fois, mis en cache dans `data/esco_raw/`) `skills.csv` et `occupations.csv`
depuis le miroir ouvert `tabiya-tech/tabiya-open-dataset` (ESCO v1.1.1, anglais uniquement),
puis génère `data/esco_index.json` : une liste d'objets `{label, lang, type, aliases}`.

Le français est couvert séparément par l'API ROME (Phase B), pas par ESCO.

## Structure du fichier généré

```json
{
  "label": "communicate effectively",
  "lang": "en",
  "type": "skill",
  "aliases": ["communicate clearly", "..."]
}
```

Un objet par ligne source (`skills.csv` ou `occupations.csv`), pas de déduplication à ce stade.

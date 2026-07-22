# Ticket Phase A — Scaffolding + ingestion ESCO

Contexte complet : `../BRIEF.md`. Ne pas dévier de ce brief. Ne modifier aucun fichier hors de ceux listés ci-dessous.

## Objectif
Poser la structure du projet et ingérer la base ESCO en local (JSON), sans dépendance à une clé API (ROME viendra en Phase B).

## Périmètre exact
1. Créer un environnement virtuel Python **3.12** (pas le Python système 3.14) :
   ```
   /opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv
   ```
   dans `02_Projets/Sites_Personnels/Analyseur_CV_ATS/`.
2. Créer `backend/requirements.txt` : `spacy`, `requests`, `flask` (serveur local minimal, pas de dépendance lourde type Django).
3. Télécharger les CSV ESCO **anglais + français** depuis le miroir ouvert GitHub `tabiya-tech/tabiya-open-dataset` (dossier `tabiya-esco-v1.1.1/`, fichiers `skills.csv` et `occupations.csv` — voir leur `README.md` pour les colonnes exactes). Les stocker bruts dans `data/esco_raw/en/` et `data/esco_raw/fr/`.
   - Si le dépôt ne propose pas les deux langues séparément, documenter dans un commentaire en tête de script ce qui a été trouvé réellement (ne pas inventer une structure de colonnes qui n'existe pas).
4. Écrire `backend/esco_ingest.py` : script qui parse ces CSV et produit `data/esco_index.json` — structure : liste d'objets `{ "label": str, "lang": "fr"|"en", "type": "skill"|"occupation", "aliases": [str, ...] }`. Un objet par ligne source, pas de déduplication agressive à ce stade.
5. Écrire un `README.md` dans le dossier racine du projet expliquant : comment activer le venv, comment relancer `esco_ingest.py`, taille du fichier généré.

## Contraintes
- Ne pas committer `.venv/` ni les CSV bruts volumineux si `data/esco_raw/` dépasse quelques Mo — ajouter un `.gitignore` local dans le projet couvrant `.venv/`, `data/esco_raw/`, `__pycache__/`.
- Ne rien faire tourner en tâche de fond (pas de serveur Flask lancé dans ce ticket — Phase D s'en charge).
- Ne pas toucher à `frontend/`, ni à `tickets/`, ni à `BRIEF.md`.

## Critère de succès
- `source .venv/bin/activate && python backend/esco_ingest.py` s'exécute sans erreur et produit `data/esco_index.json` non vide (quelques milliers d'entrées attendues, FR+EN confondus).
- `requirements.txt` s'installe proprement dans le venv 3.12 (`pip install -r backend/requirements.txt`).

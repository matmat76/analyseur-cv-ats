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

## Ingestion ROME (Phase B)

Nécessite un fichier `/Users/matthieu/Library/CloudStorage/Dropbox/DigitalGarden/.env.secret`
contenant `ROME_CLIENT_ID` et `ROME_CLIENT_SECRET` (identifiants de l'application créée sur
francetravail.io, API "ROME 4.0 - Compétences" + "ROME 4.0 - Métiers"). Ce fichier n'est jamais lu
par l'agent — seul le script Python le charge à l'exécution.

```
source .venv/bin/activate
python backend/rome_ingest.py
```

Génère `data/rome_index.json` : 35 595 compétences + 1 911 métiers (`{label, lang: "fr", type,
code, aliases: []}`). Un seul appel par ressource, pas de pagination côté API.

Détails techniques trouvés par tâtonnement (à ne pas re-chercher) :
- Jeton : `POST https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=/partenaire`
  (grant_type=client_credentials)
- Scope compétences : `api_rome-competencesv1 nomenclatureRome`
- Scope métiers : `api_rome-metiersv1 nomenclatureRome`
- Liste compétences : `GET https://api.francetravail.io/partenaire/rome-competences/v1/competences/competence`
- Liste métiers : `GET https://api.francetravail.io/partenaire/rome-metiers/v1/metiers/metier`
- Limite de débit constatée sur le tableau de bord : 1 appel/seconde (géré par `rome_client.py`).

## Moteur d'extraction de mots-clés (Phase C)

```
source .venv/bin/activate
python backend/skill_matcher.py
```

`backend/skill_matcher.py` charge `data/esco_index.json` (anglais) ou `data/rome_index.json`
(français) selon la langue demandée, construit un automate Aho-Corasick (`pyahocorasick`) sur tous
les libellés + alias, et expose `extract_matches(text, lang)` : recherche exacte (insensible à la
casse, respect des frontières de mot), retourne les compétences/métiers trouvés dans le texte —
zéro LLM, zéro invention. Utilisé ensuite (Phase D) pour comparer une annonce et un CV.

Limite connue : les libellés d'un seul caractère sont écartés (trop de faux positifs, ex. "C").
Quelques libellés de 3 caractères qui sont aussi des mots français courants (ex. "Son", "Nez",
"Cor") peuvent occasionnellement créer un faux positif — non filtrés pour ne pas perdre les
acronymes techniques légitimes de la même longueur (CSS, XML, PHP, Ada, GRH, PMB).

## Interface web (Phase D + E)

```
source .venv/bin/activate
python backend/app.py
```

Ouvre ensuite **http://127.0.0.1:5001/** dans le navigateur. Une seule commande, un seul port :
Flask sert à la fois la page (`frontend/index.html`) et l'API.

- Colle le texte de l'annonce à gauche, choisis la langue (FR = ROME, EN = ESCO).
- CV à droite : colle le texte ou importe un PDF (extraction automatique via `pypdf`, y compris
  les PDF chiffrés avec mot de passe vide — un vrai mot de passe non vide reste hors de portée,
  utiliser "Coller le texte" dans ce cas).
- Bouton "Analyser" → tableau des mots-clés de l'annonce **présents** dans le CV (vert) et
  **manquants** (rouge), à valider et reporter manuellement sur le CV Canva master.
- Testé de bout en bout (Playwright) : chargement, saisie, bascule PDF, résultats — 0 erreur JS
  (hors 404 favicon, sans conséquence).

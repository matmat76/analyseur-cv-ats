# Analyseur CV / ATS — Brief

Projet personnel (pas client) → reste dans `Sites_Personnels/`. Construit en direct avec Matthieu, aucune image/brief externe.

## Besoin
Coller le texte d'une annonce (n'importe quel domaine, FR ou EN) + coller/uploader un CV → obtenir la liste des mots-clés attendus par le poste, ceux déjà présents dans le CV, ceux manquants, et une suggestion de formulation (piochée dans les CV déjà écrits par Matthieu) pour combler les manques. Validation manuelle de chaque suggestion avant application — pas d'écriture automatique du CV final.

## Contrainte fondamentale (posée par Matthieu)
Le moteur d'analyse doit être **déterministe, pas dépendant d'un appel IA générative payant**. La comparaison mots-clés / matching doit reposer sur des règles et des bases de données de référence, pas sur un LLM qui invente. Une couche sémantique locale (embeddings Ollama, déjà installés pour le RAG du jardin) est acceptée en renfort — gratuite, locale, pas de génération de texte, juste du scoring de similarité.

## Décisions d'architecture (validées avec Matthieu le 2026-07-22)

1. **Pas de scraping de lien d'offre.** Interface = copier-coller du texte de l'annonce (repli fiable, évite CORS/blocage Workday/SuccessFactors et autres portails RH).
2. **Bases de mots-clés multi-domaines, deux sources combinées dès la v1** (Matthieu : « il y a des offres en anglais pour des sites hors de France, fais les deux ») :
   - **ROME 4.0** (France Travail, francetravail.io) — référentiel officiel français, 1911 fiches métiers, 14 301 appellations, compétences savoir-faire/savoirs/savoir-être. Colle au phrasé réel des annonces françaises. **Nécessite une clé API (client_id/secret) — Matthieu doit créer un compte sur francetravail.io et me fournir les identifiants dans le chat** (jamais dans un `.env` que je lirais moi-même).
   - **ESCO** (Union Européenne) — taxonomie tous secteurs. **Correction 2026-07-22** : le miroir ouvert utilisé (`tabiya-tech/tabiya-open-dataset`, csv `skills.csv`/`occupations.csv`) est **anglais uniquement**, pas de variante française dans ce dépôt. Pas un problème : ROME couvre déjà tout le volet français, ESCO ne sert que pour l'anglais/international (offres hors France). Colonnes réelles confirmées : `PREFERREDLABEL` (label principal), `ALTLABELS` (liste d'alias séparés par `\n`, pas par virgule), `DESCRIPTION`. Fichiers sources : `csv/skills.csv` et `csv/occupations.csv` uniquement (pas de sous-dossiers de langue).
3. **Extraction des compétences** : approche par règles (pas de LLM), inspirée de **SkillNER** (github AnasAito/SkillNER, spaCy + `PhraseMatcher` + base de compétences) — adapté pour tourner en français (`fr_core_news_lg`) et anglais (`en_core_web_lg`), avec la base de compétences alimentée par ROME + ESCO au lieu de la base par défaut (anglo-centrée).
4. **Couche sémantique v2 (itération 2, pas bloquante pour la v1)** : embeddings locaux via Ollama (`nomic-embed`, déjà utilisé pour `rag.sh`) pour rattraper les reformulations que le matching par règles raterait, et classer les meilleures phrases à réutiliser dans les CV déjà écrits par Matthieu.
5. **Backend Python local** (feu vert Matthieu) — pas une page 100% statique. Environnement dédié : **venv Python 3.12** (`brew` a `python@3.12` déjà installé) — **pas** le Python système 3.14, trop récent, spaCy n'a pas de wheels garantis dessus (risque de compilation cassée). Petit serveur local (Flask ou FastAPI, à trancher en Phase A) qui expose un endpoint `/analyser`, appelé par la page front en JS. Même logique que les autres services locaux de Matthieu (RAG, Ollama, pile vocale) — zéro VPS, zéro coût, zéro donnée envoyée dehors sauf l'appel ROME.
6. **Sortie** : tableau mots-clés présents/manquants + suggestion de formulation si trouvée dans la banque de CV existants de Matthieu (Canva master exporté en texte, dossiers `Recherche_Emploi/candidatures/`). Pas de PDF généré automatiquement — Matthieu applique lui-même sur son Canva master.

## Phasage
- **Phase A** — scaffolding projet (venv 3.12, dépendances, structure), ingestion ESCO (téléchargement + parsing local, pas de clé nécessaire).
- **Phase B** — intégration ROME (nécessite la clé API de Matthieu — bloquant tant qu'il n'a pas fourni client_id/secret).
- **Phase C** — moteur d'extraction de compétences (SkillNER-like) FR+EN sur texte libre (annonce + CV).
- **Phase D** — moteur de comparaison (annonce vs CV) + endpoint local `/analyser`.
- **Phase E** — page front (coller annonce / coller CV / bouton Analyser / tableau de résultats).
- **Phase F (v2, différée)** — couche embeddings Ollama.

## Dépendance bloquante à lever par Matthieu
Créer un compte sur https://francetravail.io, s'abonner à l'API **ROME 4.0 – Compétences** + **ROME 4.0 – Métiers**, et me transmettre `client_id` / `client_secret` directement dans le chat (jamais dans un fichier `.env`, je ne les lis pas).

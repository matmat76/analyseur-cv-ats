import json
import os

from rome_client import (
    authenticated_get,
    get_access_token,
    COMPETENCES_BASE,
    METIERS_BASE,
    SCOPE_COMPETENCES,
    SCOPE_METIERS,
)

OUTPUT_FILE = "data/rome_index.json"


def fetch_competences():
    token = get_access_token(SCOPE_COMPETENCES)
    resp = authenticated_get(COMPETENCES_BASE, "/v1/competences/competence", token)
    resp.raise_for_status()
    entries = []
    for item in resp.json():
        label = (item.get("libelle") or "").strip()
        if not label:
            continue
        entries.append({
            "label": label,
            "lang": "fr",
            "type": "competence",
            "code": item.get("code"),
            "aliases": [],
        })
    return entries


def fetch_metiers():
    token = get_access_token(SCOPE_METIERS)
    resp = authenticated_get(METIERS_BASE, "/v1/metiers/metier", token)
    resp.raise_for_status()
    entries = []
    for item in resp.json():
        label = (item.get("libelle") or "").strip()
        if not label:
            continue
        entries.append({
            "label": label,
            "lang": "fr",
            "type": "metier",
            "code": item.get("code"),
            "aliases": [],
        })
    return entries


def main():
    all_entries = fetch_competences() + fetch_metiers()

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)

    print(f"{len(all_entries)} entrées écrites dans {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

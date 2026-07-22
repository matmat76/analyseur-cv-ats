import csv
import json
import os

import requests

URLS = {
    "skill": "https://raw.githubusercontent.com/tabiya-tech/tabiya-open-dataset/main/tabiya-esco-v1.1.1/csv/skills.csv",
    "occupation": "https://raw.githubusercontent.com/tabiya-tech/tabiya-open-dataset/main/tabiya-esco-v1.1.1/csv/occupations.csv",
}
RAW_DIR = "data/esco_raw"
OUTPUT_FILE = "data/esco_index.json"


def download_if_missing(entity_type, url):
    os.makedirs(RAW_DIR, exist_ok=True)
    local_path = os.path.join(RAW_DIR, f"{entity_type}.csv")
    if not os.path.exists(local_path):
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(response.text)
    return local_path


def parse_csv(path, entity_type):
    entries = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = (row.get("PREFERREDLABEL") or "").strip()
            if not label:
                continue
            alt = row.get("ALTLABELS") or ""
            aliases = [a.strip() for a in alt.split("\n") if a.strip()]
            entries.append({
                "label": label,
                "lang": "en",
                "type": entity_type,
                "aliases": aliases,
            })
    return entries


def main():
    all_entries = []
    for entity_type, url in URLS.items():
        path = download_if_missing(entity_type, url)
        all_entries.extend(parse_csv(path, entity_type))

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)

    print(f"{len(all_entries)} entrées écrites dans {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

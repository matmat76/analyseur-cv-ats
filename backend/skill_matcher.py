import json
import re
import unicodedata

import ahocorasick

ESCO_FILE = "data/esco_index.json"
ROME_FILE = "data/rome_index.json"


def normalize(text):
    text = text.replace(" ", " ")
    text = unicodedata.normalize("NFC", text)
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_word_char(ch):
    return ch is not None and (ch.isalnum() or ch == "-")


def _build_automaton(entries):
    automaton = ahocorasick.Automaton()
    for entry in entries:
        surface_forms = [entry["label"]] + entry.get("aliases", [])
        for surface in surface_forms:
            norm = normalize(surface)
            if not norm:
                continue
            payload = (norm, entry["label"], entry["type"], entry.get("code"))
            existing = automaton.get(norm, None)
            if existing is None:
                automaton.add_word(norm, [payload])
            elif payload not in existing:
                existing.append(payload)
    automaton.make_automaton()
    return automaton


def _load_entries(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


_automatons = {}


def _get_automaton(lang):
    if lang not in _automatons:
        path = ROME_FILE if lang == "fr" else ESCO_FILE
        _automatons[lang] = _build_automaton(_load_entries(path))
    return _automatons[lang]


def extract_matches(text, lang):
    if lang not in ("fr", "en"):
        raise ValueError("lang doit être 'fr' ou 'en'")

    automaton = _get_automaton(lang)
    norm_text = normalize(text)

    seen = {}
    for end_index, payloads in automaton.iter(norm_text):
        for norm_word, label, entry_type, code in payloads:
            start_index = end_index - len(norm_word) + 1
            before = norm_text[start_index - 1] if start_index > 0 else None
            after = norm_text[end_index + 1] if end_index + 1 < len(norm_text) else None
            if _is_word_char(before) or _is_word_char(after):
                continue
            key = (label, entry_type, code)
            if key not in seen:
                seen[key] = {"label": label, "type": entry_type, "code": code}

    return list(seen.values())


if __name__ == "__main__":
    exemple_fr = (
        "Nous recherchons un développeur avec de bonnes compétences en gestion de projet "
        "et capable d'anticiper les risques opérationnels, financiers et techniques."
    )
    matches_fr = extract_matches(exemple_fr, "fr")
    print(f"FR: {len(matches_fr)} correspondances")
    for m in matches_fr[:10]:
        print(" -", m)

    exemple_en = "We are looking for a developer able to manage musical staff and communicate effectively."
    matches_en = extract_matches(exemple_en, "en")
    print(f"\nEN: {len(matches_en)} correspondances")
    for m in matches_en[:10]:
        print(" -", m)

import io
import os

from flask import Flask, jsonify, request, send_from_directory
from pypdf import PdfReader

from skill_matcher import extract_matches

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = Flask(__name__, static_folder=None)


def extract_pdf_text(file_storage):
    reader = PdfReader(io.BytesIO(file_storage.read()))
    if reader.is_encrypted:
        reader.decrypt("")
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:filename>")
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.post("/analyser")
def analyser():
    lang = request.form.get("lang")
    if lang not in ("fr", "en"):
        return jsonify({"erreur": "lang doit être 'fr' ou 'en'"}), 400

    offre_text = request.form.get("offre_text", "").strip()
    if not offre_text:
        return jsonify({"erreur": "le texte de l'annonce est vide"}), 400

    cv_text = request.form.get("cv_text", "").strip()
    cv_file = request.files.get("cv_file")
    if cv_file and cv_file.filename:
        cv_text = extract_pdf_text(cv_file)

    if not cv_text.strip():
        return jsonify({"erreur": "aucun CV fourni (texte ou fichier PDF)"}), 400

    matches_offre = extract_matches(offre_text, lang)
    matches_cv = extract_matches(cv_text, lang)

    keys_cv = {(m["label"], m["type"], m["code"]) for m in matches_cv}

    presents = [m for m in matches_offre if (m["label"], m["type"], m["code"]) in keys_cv]
    manquants = [m for m in matches_offre if (m["label"], m["type"], m["code"]) not in keys_cv]

    return jsonify({
        "matches_offre": matches_offre,
        "matches_cv": matches_cv,
        "presents": presents,
        "manquants": manquants,
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)

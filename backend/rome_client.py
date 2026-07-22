import os
import time

import requests
from dotenv import load_dotenv

load_dotenv("/Users/matthieu/Library/CloudStorage/Dropbox/DigitalGarden/.env.secret")

TOKEN_URL = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=/partenaire"
COMPETENCES_BASE = "https://api.francetravail.io/partenaire/rome-competences"
METIERS_BASE = "https://api.francetravail.io/partenaire/rome-metiers"

SCOPE_COMPETENCES = "api_rome-competencesv1 nomenclatureRome"
SCOPE_METIERS = "api_rome-metiersv1 nomenclatureRome"

# Constat du tableau de bord francetravail.io : 1 appel/seconde max sur ces deux API.
MIN_DELAY_SECONDS = 1.1

_last_call_time = 0.0


def _throttle():
    global _last_call_time
    elapsed = time.time() - _last_call_time
    if elapsed < MIN_DELAY_SECONDS:
        time.sleep(MIN_DELAY_SECONDS - elapsed)
    _last_call_time = time.time()


def get_access_token(scope):
    client_id = os.environ["ROME_CLIENT_ID"]
    client_secret = os.environ["ROME_CLIENT_SECRET"]
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(TOKEN_URL, data=data, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()["access_token"]


def authenticated_get(base_url, path, token, params=None):
    _throttle()
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    response = requests.get(f"{base_url}{path}", headers=headers, params=params, timeout=30)
    return response


if __name__ == "__main__":
    token = get_access_token(SCOPE_COMPETENCES)
    resp = authenticated_get(COMPETENCES_BASE, "/v1/competences/competence", token)
    print(f"status={resp.status_code}, {len(resp.json())} compétences reçues")

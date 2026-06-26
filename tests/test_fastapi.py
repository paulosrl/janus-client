from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from janus_client import JanusVerifier
from janus_client.fastapi import require_system_access
from tests.conftest import make_token

JWKS_URL = "https://janus.test/.well-known/jwks.json"


def _build_app(verifier: JanusVerifier) -> FastAPI:
    app = FastAPI()

    @app.get("/protegido")
    def rota(payload=Depends(require_system_access("xavier", verifier))):
        return {"sub": payload.sub}

    return app


def test_valid_token_with_access_returns_200(httpx_mock, rsa_keypair, jwks_body, kid):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    token = make_token(rsa_keypair, kid, authorized_systems=["xavier"])

    verifier = JanusVerifier(jwks_url=JWKS_URL, issuer="janus", audience="janus")
    client = TestClient(_build_app(verifier))

    resp = client.get("/protegido", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


def test_valid_token_without_access_returns_403(httpx_mock, rsa_keypair, jwks_body, kid):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    token = make_token(rsa_keypair, kid, authorized_systems=["outro-sistema"])

    verifier = JanusVerifier(jwks_url=JWKS_URL, issuer="janus", audience="janus")
    client = TestClient(_build_app(verifier))

    resp = client.get("/protegido", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


def test_missing_token_returns_401(httpx_mock):
    verifier = JanusVerifier(jwks_url=JWKS_URL, issuer="janus", audience="janus")
    client = TestClient(_build_app(verifier))

    resp = client.get("/protegido")
    assert resp.status_code == 401


def test_invalid_token_returns_401(httpx_mock):
    verifier = JanusVerifier(jwks_url=JWKS_URL, issuer="janus", audience="janus")
    client = TestClient(_build_app(verifier))

    resp = client.get("/protegido", headers={"Authorization": "Bearer lixo.invalido.aqui"})
    assert resp.status_code == 401


def test_expired_token_returns_401(httpx_mock, rsa_keypair, jwks_body, kid):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    token = make_token(rsa_keypair, kid, authorized_systems=["xavier"], expires_in=-3600)

    verifier = JanusVerifier(jwks_url=JWKS_URL, issuer="janus", audience="janus")
    client = TestClient(_build_app(verifier))

    resp = client.get("/protegido", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Token expirado."

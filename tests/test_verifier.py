from __future__ import annotations

import pytest

from janus_client import JanusTokenError, JanusTokenExpiredError, JanusVerifier
from tests.conftest import make_token

JWKS_URL = "https://janus.test/.well-known/jwks.json"


def test_verify_valid_token_returns_payload(httpx_mock, rsa_keypair, jwks_body, kid):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    token = make_token(rsa_keypair, kid, sub="user-1", authorized_systems=["xavier"])

    verifier = JanusVerifier(jwks_url=JWKS_URL, issuer="janus", audience="janus")
    payload = verifier.verify(token)

    assert payload.sub == "user-1"
    assert payload.authorized_systems == ["xavier"]


def test_authorizes_true_when_slug_present(httpx_mock, rsa_keypair, jwks_body, kid):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    token = make_token(rsa_keypair, kid, authorized_systems=["xavier", "delta"])

    verifier = JanusVerifier(jwks_url=JWKS_URL, issuer="janus", audience="janus")
    payload = verifier.verify(token)

    assert payload.authorizes("xavier") is True
    assert payload.authorizes("outro") is False


def test_expired_token_raises_expired_error(httpx_mock, rsa_keypair, jwks_body, kid):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    token = make_token(rsa_keypair, kid, expires_in=-3600)

    verifier = JanusVerifier(jwks_url=JWKS_URL, issuer="janus", audience="janus")
    with pytest.raises(JanusTokenExpiredError):
        verifier.verify(token)


def test_wrong_audience_raises_token_error(httpx_mock, rsa_keypair, jwks_body, kid):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    token = make_token(rsa_keypair, kid, audience="outro-publico")

    verifier = JanusVerifier(jwks_url=JWKS_URL, issuer="janus", audience="janus")
    with pytest.raises(JanusTokenError):
        verifier.verify(token)


def test_wrong_issuer_raises_token_error(httpx_mock, rsa_keypair, jwks_body, kid):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    token = make_token(rsa_keypair, kid, issuer="impostor")

    verifier = JanusVerifier(jwks_url=JWKS_URL, issuer="janus", audience="janus")
    with pytest.raises(JanusTokenError):
        verifier.verify(token)


def test_garbage_token_raises_token_error(httpx_mock):
    verifier = JanusVerifier(jwks_url=JWKS_URL, issuer="janus", audience="janus")
    with pytest.raises(JanusTokenError):
        verifier.verify("isso.nao.e.jwt")


def test_unknown_kid_raises_token_error(httpx_mock, rsa_keypair, jwks_body, kid):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    token = make_token(rsa_keypair, "kid-que-nao-existe-no-jwks")

    verifier = JanusVerifier(jwks_url=JWKS_URL, issuer="janus", audience="janus")
    with pytest.raises(JanusTokenError):
        verifier.verify(token)

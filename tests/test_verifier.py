from __future__ import annotations

import time

import pytest
from jose import jwt as jose_jwt

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


def test_token_without_kid_raises_token_error(httpx_mock, rsa_keypair):
    token = jose_jwt.encode(
        {"sub": "user-1", "iss": "janus", "aud": "janus"},
        rsa_keypair[0],
        algorithm="RS256",
    )

    verifier = JanusVerifier(jwks_url=JWKS_URL, issuer="janus", audience="janus")
    with pytest.raises(JanusTokenError):
        verifier.verify(token)


def test_token_missing_required_claim_raises_token_error(httpx_mock, rsa_keypair, jwks_body, kid):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    now = int(time.time())
    claims = {
        # "sub" omitido deliberadamente — token assinado e válido, claim obrigatória ausente.
        "jti": "jti-1",
        "email": "user@example.com",
        "role": "user",
        "authorized_systems": [],
        "iss": "janus",
        "aud": "janus",
        "iat": now,
        "exp": now + 3600,
    }
    token = jose_jwt.encode(claims, rsa_keypair[0], algorithm="RS256", headers={"kid": kid})

    verifier = JanusVerifier(jwks_url=JWKS_URL, issuer="janus", audience="janus")
    with pytest.raises(JanusTokenError):
        verifier.verify(token)


def test_verify_token_signed_by_second_key_during_rotation(
    httpx_mock, rsa_keypair_2, jwks_body_rotation, kid_2
):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body_rotation)
    token = make_token(rsa_keypair_2, kid_2, sub="user-2", authorized_systems=["xavier"])

    verifier = JanusVerifier(jwks_url=JWKS_URL, issuer="janus", audience="janus")
    payload = verifier.verify(token)

    assert payload.sub == "user-2"
    assert payload.authorizes("xavier") is True


def test_close_closes_underlying_jwks_cache(httpx_mock):
    verifier = JanusVerifier(jwks_url=JWKS_URL, issuer="janus", audience="janus")
    verifier.close()
    assert verifier._jwks._http_client.is_closed

from __future__ import annotations

import pytest

from janus_client.exceptions import JanusJwksFetchError
from janus_client.jwks import JwksCache

JWKS_URL = "https://janus.test/.well-known/jwks.json"


def test_get_key_fetches_and_returns_jwk(httpx_mock, jwks_body, kid):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    cache = JwksCache(JWKS_URL)
    key = cache.get_key(kid)
    assert key["kid"] == kid


def test_get_key_uses_cache_without_refetch(httpx_mock, jwks_body, kid):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    cache = JwksCache(JWKS_URL, cache_ttl_seconds=3600)
    cache.get_key(kid)
    cache.get_key(kid)  # segunda chamada não deve disparar novo fetch
    assert len(httpx_mock.get_requests()) == 1


def test_get_key_unknown_kid_raises(httpx_mock, jwks_body):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    cache = JwksCache(JWKS_URL)
    with pytest.raises(JanusJwksFetchError):
        cache.get_key("kid-inexistente")


def test_get_key_network_failure_raises(httpx_mock):
    httpx_mock.add_exception(__import__("httpx").ConnectError("boom"))
    cache = JwksCache(JWKS_URL)
    with pytest.raises(JanusJwksFetchError):
        cache.get_key("qualquer-kid")

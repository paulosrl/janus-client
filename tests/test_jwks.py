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


def test_get_key_force_refresh_kid_still_missing_raises(httpx_mock, jwks_body, kid):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    cache = JwksCache(JWKS_URL)
    cache.get_key(kid)
    with pytest.raises(JanusJwksFetchError):
        cache.get_key("kid-inexistente", force_refresh=True)


def test_get_key_response_without_keys_list_raises(httpx_mock):
    httpx_mock.add_response(url=JWKS_URL, json={"keys": "nao-e-uma-lista"})
    cache = JwksCache(JWKS_URL)
    with pytest.raises(JanusJwksFetchError):
        cache.get_key("qualquer-kid")


def test_close_closes_owned_http_client(httpx_mock, jwks_body, kid):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    cache = JwksCache(JWKS_URL)
    cache.get_key(kid)
    cache.close()
    assert cache._http_client.is_closed


def test_get_key_resolves_correct_key_among_two_simultaneous(
    httpx_mock, jwks_body_rotation, kid, kid_2
):
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body_rotation)
    cache = JwksCache(JWKS_URL)
    key_1 = cache.get_key(kid)
    key_2 = cache.get_key(kid_2)
    assert key_1["kid"] == kid
    assert key_2["kid"] == kid_2
    assert key_1 != key_2
    # ambas resolvidas a partir do mesmo fetch — sem refetch pra pegar a segunda
    assert len(httpx_mock.get_requests()) == 1


def test_get_key_rotation_new_key_appears_without_removing_old(
    httpx_mock, jwks_body, jwks_body_rotation, kid, kid_2
):
    """Simula rotação real: cache começa só com a chave antiga, Janus passa a expor
    chave atual + anterior, kid novo força refresh e ambas ficam resolvíveis depois."""
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body)
    httpx_mock.add_response(url=JWKS_URL, json=jwks_body_rotation)
    cache = JwksCache(JWKS_URL, cache_ttl_seconds=3600)

    cache.get_key(kid)  # popula cache só com a chave antiga
    key_2 = cache.get_key(kid_2)  # kid novo não está no cache -> força refresh
    key_1_again = cache.get_key(kid)  # chave antiga ainda resolve, sem novo fetch

    assert key_2["kid"] == kid_2
    assert key_1_again["kid"] == kid
    assert len(httpx_mock.get_requests()) == 2

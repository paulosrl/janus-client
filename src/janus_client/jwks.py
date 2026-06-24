"""Busca e cache do JWKS exposto pelo Janus (GET /.well-known/jwks.json)."""

from __future__ import annotations

import time
from typing import Any

import httpx

from janus_client.exceptions import JanusJwksFetchError

_DEFAULT_CACHE_TTL_SECONDS = 3600


class JwksCache:
    """Busca o JWKS do Janus e cacheia em memória por um TTL.

    Não é thread-safe para escrita concorrente do cache — em caso de corrida,
    pior caso é uma busca de rede extra, sem corrupção de estado.
    """

    def __init__(
        self,
        jwks_url: str,
        *,
        cache_ttl_seconds: int = _DEFAULT_CACHE_TTL_SECONDS,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._jwks_url = jwks_url
        self._ttl = cache_ttl_seconds
        self._http_client = http_client or httpx.Client(timeout=5.0)
        self._owns_client = http_client is None
        self._cached_keys: dict[str, dict[str, Any]] = {}
        self._fetched_at: float = 0.0

    def _is_stale(self) -> bool:
        return (time.monotonic() - self._fetched_at) > self._ttl

    def _fetch(self) -> None:
        try:
            response = self._http_client.get(self._jwks_url)
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise JanusJwksFetchError(
                f"Falha ao buscar JWKS em '{self._jwks_url}': {exc}"
            ) from exc

        keys = data.get("keys")
        if not isinstance(keys, list):
            raise JanusJwksFetchError(
                f"Resposta JWKS em '{self._jwks_url}' não contém lista 'keys'."
            )

        self._cached_keys = {k["kid"]: k for k in keys if "kid" in k}
        self._fetched_at = time.monotonic()

    def get_key(self, kid: str, *, force_refresh: bool = False) -> dict[str, Any]:
        """Retorna o JWK correspondente ao ``kid``, buscando/atualizando o cache.

        Se o ``kid`` não estiver no cache (ex: chave rotacionada), tenta uma
        busca forçada antes de desistir.
        """
        if force_refresh or self._is_stale() or kid not in self._cached_keys:
            self._fetch()

        if kid not in self._cached_keys:
            raise JanusJwksFetchError(
                f"kid '{kid}' não encontrado no JWKS de '{self._jwks_url}'."
            )
        return self._cached_keys[kid]

    def close(self) -> None:
        if self._owns_client:
            self._http_client.close()

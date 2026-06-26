"""Verificação de access tokens RS256 emitidos pelo Janus, via JWKS."""

from __future__ import annotations

from datetime import UTC, datetime

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from janus_client.exceptions import (
    JanusJwksFetchError,
    JanusTokenError,
    JanusTokenExpiredError,
)
from janus_client.jwks import JwksCache
from janus_client.payload import JanusTokenPayload

_ALGORITHM = "RS256"


class JanusVerifier:
    """Decodifica e valida access tokens do Janus contra o JWKS configurado."""

    def __init__(
        self,
        *,
        jwks_url: str,
        issuer: str,
        audience: str,
        cache_ttl_seconds: int = 3600,
    ) -> None:
        """Configura o verificador contra um JWKS, issuer e audience fixos."""
        self._issuer = issuer
        self._audience = audience
        self._jwks = JwksCache(jwks_url, cache_ttl_seconds=cache_ttl_seconds)

    def verify(self, token: str) -> JanusTokenPayload:
        """Valida assinatura, expiração, issuer e audience; retorna o payload.

        Raises:
            JanusTokenExpiredError: token estruturalmente válido, mas expirado.
            JanusTokenError: token inválido (assinatura, formato, kid desconhecido).
        """
        try:
            header = jwt.get_unverified_header(token)
        except JWTError as exc:
            raise JanusTokenError("Token malformado — header inválido.") from exc

        kid = header.get("kid")
        if not kid:
            raise JanusTokenError("Token sem 'kid' no header.")

        try:
            key = self._jwks.get_key(kid)
        except JanusJwksFetchError as exc:
            raise JanusTokenError(f"Não foi possível obter a chave de verificação: {exc}") from exc

        try:
            claims = jwt.decode(
                token,
                key,
                algorithms=[_ALGORITHM],
                audience=self._audience,
                issuer=self._issuer,
            )
        except ExpiredSignatureError as exc:
            raise JanusTokenExpiredError("Token expirado.") from exc
        except JWTError as exc:
            raise JanusTokenError(f"Token inválido: {exc}") from exc

        return JanusTokenPayload(
            sub=claims["sub"],
            email=claims["email"],
            role=claims["role"],
            expires_at=datetime.fromtimestamp(claims["exp"], tz=UTC),
            authorized_systems=claims.get("authorized_systems", []),
        )

    def close(self) -> None:
        """Libera o cliente HTTP usado para buscar o JWKS, se for dono dele."""
        self._jwks.close()

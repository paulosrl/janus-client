"""Erros do janus-client. Sem dependência de framework."""

from __future__ import annotations


class JanusClientError(Exception):
    """Erro base do janus-client."""


class JanusTokenError(JanusClientError):
    """Token inválido (assinatura, formato, claims ausentes)."""


class JanusTokenExpiredError(JanusClientError):
    """Token estruturalmente válido, mas expirado."""


class JanusSystemNotAuthorizedError(JanusClientError):
    """Token válido, mas o sistema-alvo não está na claim authorized_systems."""

    def __init__(self, slug: str) -> None:
        super().__init__(f"Token não autoriza acesso ao sistema '{slug}'.")
        self.slug = slug


class JanusJwksFetchError(JanusClientError):
    """Falha ao buscar o JWKS do Janus (rede, formato inesperado)."""

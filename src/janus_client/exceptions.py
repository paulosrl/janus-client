"""Erros do janus-client. Sem dependência de framework."""

from __future__ import annotations


class JanusClientError(Exception):
    """Erro base do janus-client."""


class JanusTokenError(JanusClientError):
    """Token inválido (assinatura, formato, claims ausentes)."""


class JanusTokenExpiredError(JanusClientError):
    """Token estruturalmente válido, mas expirado."""


class JanusJwksFetchError(JanusClientError):
    """Falha ao buscar o JWKS do Janus (rede, formato inesperado)."""

"""Payload decodificado de um access token do Janus."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True, slots=True)
class JanusTokenPayload:
    """Claims extraídos de um access token do Janus, já validado."""

    sub: str
    email: str
    role: str
    expires_at: datetime
    authorized_systems: list[str] = field(default_factory=list)

    def authorizes(self, slug: str) -> bool:
        """True se o token autoriza acesso ao sistema identificado por ``slug``."""
        return slug in self.authorized_systems

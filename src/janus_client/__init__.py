"""
janus-client — cliente leve para validar access tokens emitidos pelo Janus.

Uso mínimo (sem FastAPI)::

    from janus_client import JanusVerifier

    verifier = JanusVerifier(
        jwks_url="https://janus.exemplo.com/.well-known/jwks.json",
        issuer="janus",
        audience="janus",
    )
    payload = verifier.verify(token)
    if not payload.authorizes("xavier"):
        ...  # 403

Com FastAPI (requer extra ``janus-client[fastapi]``)::

    from janus_client import JanusVerifier
    from janus_client.fastapi import require_system_access

    verifier = JanusVerifier(jwks_url=..., issuer="janus", audience="janus")

    @router.get("/protegido")
    def rota(payload = Depends(require_system_access("xavier", verifier))):
        ...
"""

from janus_client.exceptions import (
    JanusClientError,
    JanusJwksFetchError,
    JanusSystemNotAuthorizedError,
    JanusTokenError,
    JanusTokenExpiredError,
)
from janus_client.payload import JanusTokenPayload
from janus_client.verifier import JanusVerifier

__version__ = "0.1.0"

__all__ = [
    "JanusVerifier",
    "JanusTokenPayload",
    "JanusClientError",
    "JanusTokenError",
    "JanusTokenExpiredError",
    "JanusSystemNotAuthorizedError",
    "JanusJwksFetchError",
    "__version__",
]

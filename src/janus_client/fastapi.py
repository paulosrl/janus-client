"""Integração opcional com FastAPI — dependency factory pra checagem de acesso.

Requer o extra ``janus-client[fastapi]``. Importar este módulo sem o extra
instalado levanta ImportError claro, não falha silenciosa.
"""

from __future__ import annotations

from collections.abc import Callable

try:
    from fastapi import Depends, HTTPException, status
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "janus_client.fastapi requer o extra 'fastapi': "
        "instale com 'pip install janus-client[fastapi]'."
    ) from exc

from janus_client.exceptions import JanusTokenError, JanusTokenExpiredError
from janus_client.payload import JanusTokenPayload
from janus_client.verifier import JanusVerifier

_bearer = HTTPBearer(auto_error=False)


def require_system_access(
    slug: str, verifier: JanusVerifier
) -> Callable[..., JanusTokenPayload]:
    """Cria uma dependency FastAPI que exige token Janus válido autorizado pra ``slug``.

    Uso::

        verifier = JanusVerifier(jwks_url=..., issuer="janus", audience="janus")

        @router.get("/protegido")
        def rota(payload: JanusTokenPayload = Depends(require_system_access("xavier", verifier))):
            ...
    """

    def _check(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    ) -> JanusTokenPayload:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acesso não informado.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            payload = verifier.verify(credentials.credentials)
        except JanusTokenExpiredError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        except JanusTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        if not payload.authorizes(slug):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso não autorizado a '{slug}'.",
            )

        return payload

    return _check

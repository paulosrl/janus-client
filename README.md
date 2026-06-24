# janus-client

Cliente leve para validar access tokens RS256 emitidos pelo [Janus](https://github.com/) via JWKS — sem reimplementar verify de JWT em cada sistema-alvo.

## Instalação

```bash
pip install janus-client          # core (verify + JWKS)
pip install janus-client[fastapi] # + dependency factory pra FastAPI
```

## Uso

```python
from janus_client import JanusVerifier

verifier = JanusVerifier(
    jwks_url="https://janus.exemplo.com/.well-known/jwks.json",
    issuer="janus",
    audience="janus",
)

payload = verifier.verify(token)
if not payload.authorizes("xavier"):
    ...  # 403
```

Com FastAPI:

```python
from fastapi import Depends
from janus_client import JanusVerifier
from janus_client.fastapi import require_system_access

verifier = JanusVerifier(jwks_url=..., issuer="janus", audience="janus")

@router.get("/protegido")
def rota(payload=Depends(require_system_access("xavier", verifier))):
    return {"sub": payload.sub}
```

## O que isso NÃO faz

- Não decide permissão/papel dentro do seu sistema — só responde "essa
  identidade pode entrar, sim/não". `is_admin` (ou equivalente) continua
  100% controlado localmente por cada sistema-alvo.
- Não suporta rotação de chave sem downtime ainda — o Janus hoje expõe
  sempre 1 chave só via JWKS.

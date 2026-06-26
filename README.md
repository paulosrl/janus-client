# janus-client

Cliente leve para validar access tokens RS256 emitidos pelo [Janus](https://github.com/) via JWKS — sem reimplementar verify de JWT em cada sistema-alvo.

Requer Python 3.12+.

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

## Arquitetura

Fluxo de `JanusVerifier.verify(token)`:

```
token (JWT compacto)
  │
  ▼
1. lê header sem validar assinatura → extrai "kid"
  │  (sem "kid" ou header malformado → JanusTokenError)
  ▼
2. JwksCache.get_key(kid)
  │  busca o JWKS em jwks_url (com cache em memória por cache_ttl_seconds)
  │  se "kid" não estiver no cache, força um refresh antes de desistir
  │  (falha de rede, resposta sem "keys", ou kid não encontrado → JanusJwksFetchError)
  ▼
3. valida assinatura RS256, expiração, issuer e audience com a chave obtida
  │  (token expirado → JanusTokenExpiredError; qualquer outra falha → JanusTokenError)
  ▼
4. monta JanusTokenPayload (sub, email, role, expires_at, authorized_systems)
```

`payload.authorizes(slug)` apenas checa se `slug` está na lista `authorized_systems` da claim — nenhuma chamada de rede adicional.

A dependency `require_system_access` (extra `fastapi`) chama `verify()` e traduz as exceções acima em respostas HTTP: `401` para token ausente/inválido/expirado, `403` se o token é válido mas não autoriza o `slug` pedido.

## O que isso NÃO faz

- Não decide permissão/papel dentro do seu sistema — só responde "essa
  identidade pode entrar, sim/não". `is_admin` (ou equivalente) continua
  100% controlado localmente por cada sistema-alvo.
- Não suporta rotação de chave sem downtime ainda — o Janus hoje expõe
  sempre 1 chave só via JWKS.

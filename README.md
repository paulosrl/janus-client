# janus-client

Cliente leve para validar access tokens RS256 emitidos pelo [Janus](https://github.com/) via JWKS — sem reimplementar verify de JWT em cada sistema-alvo.

Requer Python 3.12+.

## Instalação

```bash
pip install janus-client          # core (verify + JWKS)
pip install janus-client[fastapi] # + dependency factory pra FastAPI
```

### Versão fixada (consumidores externos)

Este pacote não é publicado em índice PyPI — releases são identificados por tag git (`vMAJOR.MINOR.PATCH`, ver [CHANGELOG.md](CHANGELOG.md)). Um repositório externo (ex: `xavier`) que dependa de uma versão exata, em vez de seguir `HEAD` da branch principal, deve apontar pra tag:

```bash
uv add "janus-client @ git+https://github.com/paulosrl/janus-client.git@v0.1.0"
```

ou, em `pyproject.toml`:

```toml
[tool.uv.sources]
janus-client = { git = "https://github.com/paulosrl/janus-client.git", tag = "v0.1.0" }
```

Versionamento segue SemVer em relação à API pública exportada em `src/janus_client/__init__.py` (`JanusVerifier`, `JanusTokenPayload`, exceções, e `janus_client.fastapi.require_system_access`):

- **MAJOR**: remoção ou mudança incompatível em símbolo público.
- **MINOR**: adição compatível (novo símbolo, novo parâmetro opcional).
- **PATCH**: correção sem mudança de superfície pública.

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

## Desenvolvimento

```bash
uv sync --extra fastapi   # instala core + extra fastapi + dev deps
./scripts/verify.sh       # pytest + cobertura + mypy + ruff, nessa ordem
```

Documentação completa do codebase (passo a passo, módulo por módulo, e
como verificar cada parte) em [`docs/PRD.md`](docs/PRD.md).

## Processo de release

Pra publicar uma nova versão (depois de mudar `version` em `pyproject.toml` e `__version__` em `src/janus_client/__init__.py`):

1. Atualizar `CHANGELOG.md` com a nova seção `[MAJOR.MINOR.PATCH] - YYYY-MM-DD`.
2. Commitar o bump de versão + changelog.
3. Criar tag anotada: `git tag -a vMAJOR.MINOR.PATCH -m "..."` no commit do bump.
4. `git push origin vMAJOR.MINOR.PATCH` — só a partir daqui a versão está disponível pra consumidores pinarem.

## O que isso NÃO faz

- Não decide permissão/papel dentro do seu sistema — só responde "essa
  identidade pode entrar, sim/não". `is_admin` (ou equivalente) continua
  100% controlado localmente por cada sistema-alvo.
- Não executa rotação de chave — ele apenas consome o JWKS exposto pelo Janus.
  Quando o Janus publica chave atual e chave anterior durante uma janela de
  rotação, o cliente escolhe a chave correta pelo `kid` do token.

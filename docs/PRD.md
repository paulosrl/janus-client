# PRD — janus-client

> Documento de referência do produto/codebase. Complementa o `README.md`
> (que foca em "como usar") com uma leitura passo a passo de "como o
> código funciona" e "como verificar que continua funcionando".

## 1. Problema e proposta de valor

Sistemas internos que confiam no Janus como identity provider precisam
verificar access tokens RS256 e checar se a identidade tem acesso a um
sistema específico (`authorized_systems`). Sem essa lib, cada sistema-alvo
reimplementaria: fetch de JWKS, cache de chave, decodificação RS256,
validação de `iss`/`aud`/`exp`, e tradução de erros pra HTTP.

`janus-client` resolve só essa parte — verificação de identidade — e
deixa autorização local (`is_admin` etc.) inteiramente fora de escopo.
Ver `README.md` → "O que isso NÃO faz".

## 2. Escopo atual (v0.1.0)

- Requer Python 3.12+.
- Core sem dependência de framework: `JanusVerifier`, `JwksCache`,
  `JanusTokenPayload`, exceções em `exceptions.py`.
- Extra opcional `[fastapi]`: dependency factory `require_system_access`.
- Limitações conhecidas (documentadas no README): sem rotação de chave
  sem downtime; sem decisão de autorização local.

## 3. Codebase passo a passo

A leitura abaixo segue a ordem de dependência dos módulos — de "sem
dependências internas" até "depende de tudo".

### 3.1 `src/janus_client/exceptions.py` (19 linhas)

Hierarquia de erros, sem dependência de framework:

```
JanusClientError (base)
├── JanusTokenError        — token inválido (assinatura, formato, claims ausentes)
├── JanusTokenExpiredError — token estruturalmente válido, mas expirado
└── JanusJwksFetchError    — falha ao buscar o JWKS (rede, formato inesperado)
```

Ponto de atenção histórico: uma quarta exceção (`JanusSystemNotAuthorizedError`)
existiu aqui mas foi removida — nunca era levantada por nenhum caminho de
código real (ver `openspec/changes/archive/2026-06-26-0002-revisar-e-documentar-codebase/`).
Regra vigente: toda exceção pública SHALL ser levantada por pelo menos um
caminho de código (capability `error-handling` em `openspec/specs/`).

### 3.2 `src/janus_client/payload.py` (21 linhas)

`JanusTokenPayload` — dataclass congelado com os claims já validados:
`sub`, `email`, `role`, `expires_at`, `authorized_systems`. Método
`authorizes(slug) -> bool`: checagem pura em memória, sem I/O.

### 3.3 `src/janus_client/jwks.py` (77 linhas)

`JwksCache` — busca `GET <jwks_url>` e cacheia em memória por
`cache_ttl_seconds` (default 3600s).

```
get_key(kid, force_refresh=False)
  │
  ├─ cache stale OU kid ausente OU force_refresh=True?
  │    └─ sim → _fetch() (1 chamada de rede)
  │
  └─ kid ainda ausente após fetch?
       └─ sim → JanusJwksFetchError
       └─ não → retorna o JWK
```

`_fetch()` trata dois tipos de falha, ambos virando `JanusJwksFetchError`:
falha de rede/HTTP (`httpx.HTTPError`) e resposta sem uma lista `"keys"`
válida (`ValueError`/checagem manual).

Não é thread-safe para escrita concorrente — pior caso documentado é uma
busca de rede extra, sem corrupção de estado.

### 3.4 `src/janus_client/verifier.py` (81 linhas)

`JanusVerifier.verify(token)` — o ponto de entrada principal:

```
token
  │
  ▼ jwt.get_unverified_header(token)
  │   sem validar assinatura ainda; só extrai o header
  │   header malformado → JanusTokenError
  │
  ▼ extrai "kid" do header
  │   ausente → JanusTokenError
  │
  ▼ JwksCache.get_key(kid)
  │   falha → JanusTokenError (encapsula JanusJwksFetchError)
  │
  ▼ jwt.decode(token, key, algorithms=["RS256"], audience=, issuer=)
  │   valida assinatura + exp + iss + aud nesta única chamada
  │   expirado → JanusTokenExpiredError
  │   qualquer outra falha → JanusTokenError
  │
  ▼ JanusTokenPayload(sub, email, role, expires_at, authorized_systems)
```

`close()` delega para `JwksCache.close()`, que só fecha o `httpx.Client`
interno se o `JwksCache` for o dono dele (não fecha clients injetados
pelo caller).

### 3.5 `src/janus_client/fastapi.py` (74 linhas)

Módulo opcional (`pip install janus-client[fastapi]`). Falha com
`ImportError` claro se o extra não estiver instalado — não falha
silenciosamente em runtime depois.

`require_system_access(slug, verifier)` retorna uma dependency FastAPI
que traduz o resultado de `verify()` em HTTP:

| Situação | Status |
|---|---|
| `Authorization` header ausente | 401 |
| `JanusTokenExpiredError` | 401 "Token expirado." |
| `JanusTokenError` (qualquer outra falha de validação) | 401 "Token inválido." |
| Token válido mas `not payload.authorizes(slug)` | 403 |
| Token válido e autorizado | retorna `JanusTokenPayload` pro handler |

### 3.6 `src/janus_client/__init__.py` (48 linhas)

Superfície pública (`__all__`): `JanusVerifier`, `JanusTokenPayload`,
`JanusClientError`, `JanusTokenError`, `JanusTokenExpiredError`,
`JanusJwksFetchError`, `__version__`. Tudo que não está aqui (`JwksCache`,
o módulo `fastapi`) é acessível via import direto do submódulo, mas não
é a API "recomendada" de primeira linha.

## 4. Como testar e verificar

### 4.1 Setup do ambiente

```bash
uv sync --extra fastapi   # instala core + extra fastapi + dev deps
```

> `uv sync` sozinho (sem `--extra fastapi`) remove o extra do venv —
> sempre inclua `--extra fastapi` ao sincronizar neste projeto.

### 4.2 Verificação completa (recomendado)

```bash
./scripts/verify.sh
```

Roda em sequência, parando no primeiro erro:
1. `pytest -q` — suíte de testes (21 testes em `tests/`)
2. `pytest --cov=src/janus_client --cov-report=term-missing` — cobertura
   (baseline atual: **100%** em todos os módulos de `src/janus_client/`)
3. `mypy src/` — checagem de tipos (depende de `types-python-jose` no
   `dependency-groups.dev`)
4. `ruff check src/ tests/` — lint

### 4.3 Verificações pontuais

```bash
uv run python -m pytest -q tests/test_verifier.py   # só um módulo de teste
uv run python -m pytest -k "expired"                 # só testes que casam com "expired"
uv run python -m mypy src/janus_client/verifier.py   # só um arquivo
```

### 4.4 Mapa de testes por módulo

| Módulo de produção | Módulo de teste | O que cobre |
|---|---|---|
| `jwks.py` | `tests/test_jwks.py` | fetch+cache, kid desconhecido, `force_refresh`, falha de rede, resposta sem `"keys"`, `close()` |
| `verifier.py` | `tests/test_verifier.py` | caminho feliz, expiração, audience/issuer errados, token malformado, kid ausente/desconhecido, `close()` |
| `fastapi.py` | `tests/test_fastapi.py` | 200 autorizado, 403 não autorizado, 401 sem token, 401 token inválido, 401 token expirado |
| `payload.py` | exercitado indiretamente via `test_verifier.py` (`authorizes`) | — |
| `exceptions.py` | exercitado indiretamente em todos os testes de erro | — |

`tests/conftest.py` concentra as fixtures compartilhadas: par de chaves
RSA de sessão (`rsa_keypair`), corpo de JWKS (`jwks_body`), e o helper
`make_token(...)` pra gerar JWTs assinados com claims customizáveis.

### 4.5 Sinais de regressão a observar

- Cobertura cair abaixo de 100% sem justificativa documentada no PR/commit.
- `mypy` voltando a reportar `import-untyped` em `verifier.py` (geralmente
  indica que `types-python-jose` saiu do ambiente — checar `uv sync --extra fastapi`).
- Qualquer exceção pública adicionada a `exceptions.py`/`__all__` sem um
  teste que a levante (ver capability `error-handling` em `openspec/specs/`).

## 5. Histórico de decisões relevantes

Mudanças significativas de qualidade/arquitetura ficam registradas em
`openspec/changes/archive/`:

- `2026-06-26-0001-corrigir-versao-minima-python` — `requires-python`
  corrigido pra `>=3.12` (uso de `datetime.UTC`), `types-python-jose`
  adicionado.
- `2026-06-26-0002-revisar-e-documentar-codebase` — remoção do código
  morto `JanusSystemNotAuthorizedError`, cobertura de testes elevada a
  100%, docstrings completas, seção de arquitetura no README.

As specs vigentes (capabilities testáveis) ficam em `openspec/specs/`:
`package-compatibility`, `error-handling`, `test-coverage`,
`documentation-completeness`.

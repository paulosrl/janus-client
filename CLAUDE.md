# CLAUDE.md

Este arquivo orienta o Claude Code (claude.ai/code) ao trabalhar neste repositório.

## Projeto

`janus-client`: cliente leve pra validar access tokens RS256 emitidos pelo "Janus" via JWKS. Core sem dependência de framework; integração FastAPI é extra opcional. Docs/comentários/commits deste repo são em português.

## Comandos

```bash
uv sync --extra fastapi          # instala core + extra fastapi + dev deps
./scripts/verify.sh               # checagem completa: pytest, pytest --cov, mypy, ruff (para no 1º erro)

uv run python -m pytest -q                                    # só testes
uv run python -m pytest tests/test_verifier.py -q              # 1 arquivo
uv run python -m pytest tests/test_verifier.py::test_name -q   # 1 teste
uv run python -m pytest --cov=src/janus_client --cov-report=term-missing -q  # cobertura
uv run python -m mypy src/                                     # type check
uv run ruff check src/ tests/                                  # lint
```

Requer Python 3.12+.

## Arquitetura

Fluxo de `JanusVerifier.verify(token)` (src/janus_client/verifier.py):

1. `jose.jwt.get_unverified_header` lê header sem validar assinatura, extrai `kid`. Ausente/malformado → `JanusTokenError`.
2. `JwksCache.get_key(kid)` (src/janus_client/jwks.py) — busca JWKS, cache em memória por `cache_ttl_seconds`. Se `kid` não estiver no cache (ex: rotação de chave), força 1 refresh antes de desistir. Falha de rede / sem campo `keys` / kid desconhecido → `JanusJwksFetchError`.
3. `jose.jwt.decode` valida assinatura RS256, expiração, issuer, audience. Expirado → `JanusTokenExpiredError`; qualquer outra falha → `JanusTokenError`.
4. Monta `JanusTokenPayload` (sub, email, role, expires_at, authorized_systems).

`payload.authorizes(slug)` (src/janus_client/payload.py) é checagem local pura contra `authorized_systems` — sem chamada de rede.

`require_system_access(slug, verifier)` (src/janus_client/fastapi.py, extra `fastapi`) é dependency factory: chama `verify()` e traduz exceções pra HTTP — `401` token ausente/inválido/expirado, `403` se válido mas não autoriza `slug`. Importar `janus_client.fastapi` sem o extra instalado levanta `ImportError` claro.

### Limites de design

- Este cliente NÃO decide permissão/papel dentro do sistema — só responde "essa identidade pode entrar em X, sim/não". `is_admin` e equivalentes ficam 100% sob controle de cada sistema-alvo.
- Sem suporte a rotação de chave sem downtime ainda — Janus hoje expõe só 1 chave via JWKS.
- Escrita do `JwksCache` não é thread-safe sob refresh concorrente; pior caso é 1 fetch de rede extra, sem corrupção de estado.

## Workflow OpenSpec

Repo usa workflow spec-driven do OpenSpec (`openspec/config.yaml`, schema `spec-driven`). Specs em `openspec/specs/`, changes em andamento em `openspec/changes/`, concluídas arquivadas em `openspec/changes/archive/`.

Pastas de archive seguem `YYYY-MM-DD-NNNN-nome-em-portugues` (data, número sequencial, slug em português).

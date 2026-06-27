# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
seguindo [SemVer](https://semver.org/lang/pt-BR/).

## [0.1.0] - 2026-06-27

Baseline retroativo — primeira versão com tag, sem mudança de código.

### Added

- `JanusVerifier`: valida access tokens RS256 emitidos pelo Janus via JWKS (`kid` no header, cache em memória por `cache_ttl_seconds`, refresh forçado em `kid` desconhecido).
- `JanusTokenPayload` com `authorizes(slug)` — checagem local de `authorized_systems`, sem chamada de rede.
- Exceções públicas: `JanusClientError`, `JanusTokenError`, `JanusTokenExpiredError`, `JanusJwksFetchError`.
- Extra opcional `fastapi`: `require_system_access(slug, verifier)`, dependency factory que traduz falhas de verificação em `401`/`403`.

[0.1.0]: https://github.com/paulosrl/janus-client/releases/tag/v0.1.0

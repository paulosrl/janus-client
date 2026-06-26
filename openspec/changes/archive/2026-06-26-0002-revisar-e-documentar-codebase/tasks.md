## 1. Remover código morto (error-handling)

- [x] 1.1 Remover `JanusSystemNotAuthorizedError` de `src/janus_client/exceptions.py`
- [x] 1.2 Remover import e entrada em `__all__` de `JanusSystemNotAuthorizedError` em `src/janus_client/__init__.py`
- [x] 1.3 Confirmar (grep) que não há nenhuma outra referência a `JanusSystemNotAuthorizedError` no repo (código, testes, docs)

## 2. Medir e fechar gaps de cobertura (test-coverage)

- [x] 2.1 Adicionar `pytest-cov` ao `dependency-groups.dev` em `pyproject.toml` e sincronizar o ambiente
- [x] 2.2 Rodar `pytest --cov=src/janus_client --cov-report=term-missing` e levantar os gaps reais
- [x] 2.3 Adicionar teste pra `JwksCache.get_key` com `kid` ausente mesmo após `force_refresh`
- [x] 2.4 Adicionar teste pra resposta JWKS sem a lista `"keys"`
- [x] 2.5 Adicionar testes para quaisquer outros gaps relevantes encontrados em 2.2 (caminhos de erro em `verifier.py` e `fastapi.py`) — cobertura final 100%

## 3. Documentação (documentation-completeness)

- [x] 3.1 Auditar docstrings de `JanusVerifier` (`__init__`, `verify`, `close`), `JanusTokenPayload.authorizes`, `JwksCache` e exceções restantes; completar onde estiver ausente
- [x] 3.2 Adicionar ao `README.md` uma seção descrevendo o fluxo de verificação (token → header/kid → JWKS → claims → payload)

## 4. Verificação final

- [x] 4.1 Rodar `pytest -q` e confirmar que todos os testes passam (21 passed)
- [x] 4.2 Rodar `pytest --cov=src/janus_client --cov-report=term-missing` novamente e registrar a cobertura final (100%)
- [x] 4.3 Rodar `mypy src/` e confirmar que continua limpo
- [x] 4.4 Rodar `ruff check src/ tests/` e confirmar que continua limpo

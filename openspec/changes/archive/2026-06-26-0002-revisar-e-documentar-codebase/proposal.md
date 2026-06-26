## Why

O `janus-client` está em sua primeira versão (`0.1.0`), com um único commit inicial. Antes de evoluir a API (rotação de chaves, novos claims, etc.), vale fechar lacunas de qualidade já visíveis: há código morto na superfície pública de exceções (`JanusSystemNotAuthorizedError` é exportado mas nunca levantado em nenhum fluxo real), não há medição formal de cobertura de testes, e a documentação (docstrings internas + README) não cobre toda a API pública nem os achados de revisão. Fazer essa revisão agora, com poucos consumidores, evita que o código morto e os gaps de teste se cristalizem como "comportamento esperado" por integradores externos.

## What Changes

- **BREAKING**: Remover `JanusSystemNotAuthorizedError` de `exceptions.py` e do `__all__`/import em `__init__.py` — nunca é levantada (`verifier.py` não a usa; `fastapi.py` levanta `HTTPException` diretamente), então mantê-la na API pública é uma promessa falsa de comportamento.
- Adicionar `pytest-cov` ao `dependency-groups.dev` e medir cobertura real de `src/janus_client/`.
- Fechar gaps de teste identificados pela medição de cobertura (ex.: caminhos de erro do `JwksCache.get_key` / `_fetch`, casos de `JanusTokenError` em `verifier.py`, branches não exercitadas em `fastapi.py`).
- Completar docstrings ausentes/inconsistentes em todos os símbolos públicos exportados (`JanusVerifier`, `JwksCache`, `JanusTokenPayload`, exceções restantes, `require_system_access`).
- Expandir o `README.md` com uma seção descrevendo a arquitetura (fluxo verify → JWKS → claims) e registrar a remoção do código morto no changelog/notas de versão, se houver.

## Capabilities

### New Capabilities
- `error-handling`: define a superfície pública de exceções do `janus-client` — quais existem, quando cada uma é levantada, e garante que toda exceção exportada tem pelo menos um teste que a exercita.
- `test-coverage`: define o padrão de medição de cobertura de testes do projeto (ferramenta, limiar mínimo, processo pra fechar gaps).
- `documentation-completeness`: define que todo símbolo público exportado em `__init__.py` tem docstring, e que o README cobre arquitetura e limitações conhecidas.

### Modified Capabilities
(nenhuma — não há overlap com `package-compatibility`, a única spec existente)

## Impact

- `src/janus_client/exceptions.py`, `src/janus_client/__init__.py`: remoção de `JanusSystemNotAuthorizedError`.
- `src/janus_client/verifier.py`, `src/janus_client/jwks.py`, `src/janus_client/fastapi.py`, `src/janus_client/payload.py`: adição/ajuste de docstrings; sem mudança de lógica além da remoção da exceção morta.
- `tests/`: novos testes pra fechar gaps de cobertura.
- `pyproject.toml`: `pytest-cov` no `dependency-groups.dev`.
- `README.md`: nova seção de arquitetura.
- Consumidores que importam `JanusSystemNotAuthorizedError` diretamente (improvável, dado que nunca é levantada) terão `ImportError` — mudança de major/minor version recomendada no `pyproject.toml`.

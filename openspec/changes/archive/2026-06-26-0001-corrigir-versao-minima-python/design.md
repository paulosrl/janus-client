## Context

`pyproject.toml` declara `requires-python = ">=3.10"` mas `verifier.py:5` usa `from datetime import UTC`, símbolo introduzido no `datetime` apenas em versões mais recentes do Python. O mantenedor decidiu fixar `3.12` como piso suportado (em vez de reescrever o código para `timezone.utc`, compatível com 3.10). Também há um erro `import-untyped` do mypy em `verifier.py` por falta de stubs de `python-jose`.

## Goals / Non-Goals

**Goals:**
- Fazer `requires-python` refletir a versão mínima real exigida pelo código (`>=3.12`).
- Eliminar o erro `import-untyped` do mypy em `verifier.py` instalando `types-python-jose`.
- Documentar a versão mínima de Python no README.

**Non-Goals:**
- Não reescrever `verifier.py` para suportar 3.10/3.11 (decisão explícita do mantenedor: subir o piso, não rebaixar o uso de `datetime.UTC`).
- Não tratar o `StarletteDeprecationWarning` de `httpx`/`starlette.testclient` — é dependência externa (FastAPI/Starlette), fora do controle deste pacote.
- Não alterar comportamento de runtime do `JanusVerifier`, `JwksCache` ou `JanusTokenPayload`.

## Decisions

- **Subir `requires-python` em vez de reescrever para `timezone.utc`**: a alternativa (trocar `UTC` por `datetime.timezone.utc`) manteria compatibilidade com 3.10, mas o mantenedor preferiu fixar a versão mínima real, evitando reescrever código que já funciona e está testado.
- **Adicionar `types-python-jose` ao `dependency-groups.dev`** em vez de ignorar o erro via `# type: ignore` ou config do mypy: stubs de terceiro resolvem a causa raiz (falta de tipos) sem suprimir checagem futura no módulo.

## Risks / Trade-offs

- [Risco] Consumidores que hoje instalam o pacote em Python 3.10/3.11 terão a instalação bloqueada pelo pip por causa do `requires-python`. → Mitigação: esse uso já estava quebrado em runtime (`ImportError` ao importar `janus_client`); o bloqueio no `pip install` é estritamente melhor (falha cedo, com mensagem clara, em vez de falhar no primeiro `verify()`).
- [Risco] `types-python-jose` pode não cobrir 100% da API usada, exigindo `# type: ignore` pontual depois. → Mitigação: rodar `mypy src/` após a mudança e tratar quaisquer gaps residuais como follow-up, não bloqueador desta mudança.

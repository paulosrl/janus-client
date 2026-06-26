## Why

`pyproject.toml` declara `requires-python = ">=3.10"`, mas `src/janus_client/verifier.py` importa `datetime.UTC`, disponível apenas a partir do Python 3.12 (CPython adicionou em 3.11, mas o projeto fixa 3.12 como piso real conforme decisão do mantenedor). Instalar o pacote em 3.10 ou 3.11 quebra no `import janus_client` com `ImportError`. Junto disso, `mypy` reporta `import-untyped` em `verifier.py` por falta de stubs do `python-jose`, deixando esse módulo sem checagem de tipos efetiva.

## What Changes

- Atualizar `requires-python` em `pyproject.toml` de `">=3.10"` para `">=3.12"`, refletindo a dependência real em `datetime.UTC`. **BREAKING** para quem instalava em 3.10/3.11 (uso nunca foi de fato suportado, já quebrava em runtime).
- Adicionar `types-python-jose` ao `dependency-groups.dev` em `pyproject.toml`, eliminando o erro `import-untyped` do mypy em `verifier.py`.
- Documentar no `README.md` a versão mínima de Python exigida (3.12+).

Fora de escopo: o `StarletteDeprecationWarning` sobre `httpx`/`starlette.testclient` (dependência externa do FastAPI/Starlette, não controlado por este pacote).

## Capabilities

### New Capabilities
- `package-compatibility`: garante que os metadados de empacotamento (`requires-python`) declarados em `pyproject.toml` refletem a versão mínima de Python de fato exigida pelo código-fonte.

### Modified Capabilities
(nenhuma — não há specs existentes em `openspec/specs/` além desta nova capability)

## Impact

- `pyproject.toml`: campo `requires-python`, grupo `dependency-groups.dev`.
- `README.md`: seção de instalação/requisitos.
- Nenhuma mudança em `src/janus_client/*.py` — o código já usa `datetime.UTC`; o ajuste é só o metadata declarar a versão correta.
- Sem impacto em testes (15 passam) ou em `ruff check src/ tests/` (limpo).

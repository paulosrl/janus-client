## 1. Metadados do pacote

- [x] 1.1 Atualizar `requires-python` em `pyproject.toml` de `">=3.10"` para `">=3.12"`
- [x] 1.2 Adicionar `types-python-jose` ao grupo `dependency-groups.dev` em `pyproject.toml`

## 2. Documentação

- [x] 2.1 Adicionar ao `README.md` a versão mínima de Python exigida (3.12+)

## 3. Verificação

- [x] 3.1 Rodar `mypy src/` e confirmar que o erro `import-untyped` em `verifier.py` desapareceu
- [x] 3.2 Rodar `pytest -q` e confirmar que os 15 testes continuam passando
- [x] 3.3 Rodar `ruff check src/ tests/` e confirmar que continua limpo

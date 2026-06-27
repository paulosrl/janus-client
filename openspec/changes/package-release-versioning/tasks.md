## 1. Changelog e baseline

- [x] 1.1 Criar `CHANGELOG.md` (formato Keep a Changelog) com entrada retroativa para `0.1.0`, resumindo o estado atual da API pública.
- [x] 1.2 Criar tag git anotada `v0.1.0` apontando para o commit atual de HEAD (`git tag -a v0.1.0 -m "..."`), estabelecendo baseline sem bump de versão.
- [ ] 1.3 Push da tag para `origin` (`git push origin v0.1.0`). **Pendente: requer confirmação explícita do usuário antes de empurrar pra remoto.**

## 2. Documentação para consumidores

- [x] 2.1 Adicionar seção no `README.md` explicando instalação por versão pinada via git tag (ex: `uv add git+https://github.com/paulosrl/janus-client.git@vX.Y.Z`), já que não há publish em PyPI.
- [x] 2.2 Documentar no `README.md` (ou em `CLAUDE.md`) a regra de quando incrementar MAJOR/MINOR/PATCH, referenciando a superfície pública em `src/janus_client/__init__.py`.

## 3. Processo de release (próximos bumps)

- [x] 3.1 Documentar checklist de release no README ou em `docs/`: bump de `version` em `pyproject.toml` → atualizar `CHANGELOG.md` → tag `vX.Y.Z` no commit de bump → push da tag.
- [ ] 3.2 Verificar que `openspec/specs/release-versioning/spec.md` foi arquivado corretamente após o merge desta change (via `openspec archive`), confirmando que a capability passa a existir como spec permanente do repo. **Pendente: só faz sentido após commit/merge desta change.**

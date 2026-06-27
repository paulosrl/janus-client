## Why

`janus-client` está parado em `version = "0.1.0"` desde o início, sem tags git e sem processo de release. O único consumidor hoje (`xavier`) depende dele via path editable (`{ path = "../../../janus-client", editable = true }`), sem nenhum pin de versão — uma auditoria cross-repo (janusmppa/xavier/janus-client) identificou isso como fragilidade estrutural: qualquer commit em `janus-client`, incluindo um breaking change, é adotado silenciosamente pelo `xavier` sem que ninguém precise decidir. Sem um processo de release versionado no `janus-client`, não existe nada para o consumidor pinar.

## What Changes

- Adotar SemVer (`MAJOR.MINOR.PATCH`) como contrato de versionamento público do pacote, cobrindo a API exportada em `src/janus_client/__init__.py`.
- Cada release SHALL corresponder a uma tag git anotada (`vX.Y.Z`) apontando para o commit cuja `pyproject.toml` declara essa versão.
- Adicionar `CHANGELOG.md` no formato Keep a Changelog, atualizado a cada release.
- Documentar no README como um consumidor externo deve referenciar uma versão específica (ex: `uv add git+https://github.com/paulosrl/janus-client.git@vX.Y.Z`), já que o pacote não é publicado em índice PyPI.
- **BREAKING**: nenhuma mudança de comportamento em código — o impacto é de processo/contrato de release, não da API do `JanusVerifier`.

## Capabilities

### New Capabilities
- `release-versioning`: o pacote segue SemVer, cada release tem tag git correspondente e changelog documentado, permitindo que consumidores externos fixem uma versão exata em vez de seguir HEAD via path editable.

### Modified Capabilities
(nenhuma — `package-compatibility` trata de `requires-python`, não de versionamento de release; não há mudança de requisito nela)

## Impact

- `pyproject.toml`: nenhuma mudança de schema, apenas disciplina de bump de `version` por release.
- Novo `CHANGELOG.md` na raiz do repo.
- `README.md`: nova seção de instalação versionada para consumidores externos.
- Nenhum código em `src/janus_client/` é alterado.
- Fora de escopo desta change: a migração do `xavier` para consumir uma versão pinada (em vez de path editable) é uma change separada, a ser proposta no repositório `xavier`, depois que este processo de release existir aqui.

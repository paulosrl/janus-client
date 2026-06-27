# release-versioning Specification

## Purpose
TBD - created by archiving change package-release-versioning. Update Purpose after archive.
## Requirements
### Requirement: Versionamento SemVer da API pública
O pacote SHALL versionar `pyproject.toml` (`project.version`) seguindo SemVer (`MAJOR.MINOR.PATCH`) em relação à superfície pública exportada por `src/janus_client/__init__.py`. Mudança que remove ou altera de forma incompatível um símbolo exportado SHALL incrementar `MAJOR`. Adição compatível de símbolo/parâmetro opcional SHALL incrementar `MINOR`. Correção sem mudança de superfície pública SHALL incrementar `PATCH`.

#### Scenario: Breaking change na API pública exige bump de MAJOR
- **WHEN** um símbolo hoje exportado em `src/janus_client/__init__.py` é removido ou tem sua assinatura alterada de forma incompatível
- **THEN** a versão em `pyproject.toml` SHALL ter o componente `MAJOR` incrementado em relação à última release

#### Scenario: Correção de bug sem mudança de superfície pública usa PATCH
- **WHEN** uma correção é feita em `verifier.py`/`jwks.py`/`payload.py` sem alterar nenhum símbolo exportado em `__init__.py`
- **THEN** a versão em `pyproject.toml` SHALL ter apenas o componente `PATCH` incrementado

### Requirement: Tag git por release
Toda versão declarada em `pyproject.toml` que for considerada "released" SHALL ter uma tag git anotada no formato `vMAJOR.MINOR.PATCH` apontando exatamente para o commit que introduziu essa versão no `pyproject.toml`.

#### Scenario: Release sem tag correspondente é incompleta
- **WHEN** a versão em `pyproject.toml` é incrementada e o commit é mesclado na branch principal
- **THEN** uma tag `vMAJOR.MINOR.PATCH` SHALL existir apontando para esse commit antes da release ser considerada disponível para consumidores externos pinarem

#### Scenario: Consumidor externo pina uma versão exata via tag
- **WHEN** um consumidor externo (ex: `xavier`) declara a dependência como `git+https://github.com/paulosrl/janus-client.git@vMAJOR.MINOR.PATCH`
- **THEN** a instalação resolve exatamente o commit daquela tag, de forma reprodutível, sem seguir HEAD da branch principal

### Requirement: Changelog por release
O repositório SHALL manter um `CHANGELOG.md` no formato Keep a Changelog, com uma entrada por versão publicada listando mudanças relevantes para consumidores (Added/Changed/Fixed/Removed).

#### Scenario: Nova release adiciona entrada no changelog
- **WHEN** uma nova tag de release `vMAJOR.MINOR.PATCH` é criada
- **THEN** `CHANGELOG.md` SHALL conter uma seção para essa versão, descrevendo as mudanças visíveis para consumidores

### Requirement: Documentação de instalação por versão pinada
O `README.md` SHALL documentar como um consumidor externo instala uma versão específica do pacote via referência de tag git, dado que o pacote não é publicado em índice PyPI nesta fase.

#### Scenario: Consumidor consulta README para fixar versão
- **WHEN** um desenvolvedor de outro repositório (ex: `xavier`) quer depender de uma versão específica de `janus-client` em vez de path editable
- **THEN** o `README.md` SHALL mostrar o comando de instalação (ex: `uv add git+https://github.com/paulosrl/janus-client.git@vX.Y.Z`) sem que ele precise inspecionar `pyproject.toml` ou histórico de commits


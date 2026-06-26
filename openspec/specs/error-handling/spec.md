# error-handling Specification

## Purpose
TBD - created by archiving change revisar-documentar-codebase. Update Purpose after archive.

## Requirements
### Requirement: Toda exceção pública exportada é efetivamente levantada
Toda exceção listada em `janus_client.__all__` SHALL ser levantada por pelo menos um caminho de código real do pacote (não apenas declarada).

#### Scenario: Auditoria da superfície de exceções
- **WHEN** se inspeciona cada exceção em `janus_client.__all__` (`JanusClientError`, `JanusTokenError`, `JanusTokenExpiredError`, `JanusJwksFetchError`)
- **THEN** existe ao menos um teste que provoca essa exceção sendo levantada por `JanusVerifier`, `JwksCache` ou pela dependency do FastAPI

### Requirement: Exceções não utilizadas são removidas da API pública
Uma exceção SHALL ser removida de `exceptions.py` e de `__init__.py` (`__all__`/import) se não houver nenhum caminho de código no pacote que a levante.

#### Scenario: JanusSystemNotAuthorizedError removida
- **WHEN** se importa `janus_client` após esta mudança
- **THEN** `JanusSystemNotAuthorizedError` não está mais disponível em `janus_client.__all__` nem é importável como `from janus_client import JanusSystemNotAuthorizedError`

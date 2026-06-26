## ADDED Requirements

### Requirement: Cobertura de testes é medida formalmente
O projeto SHALL medir cobertura de testes de `src/janus_client/` usando `pytest-cov`, disponível como dependência de desenvolvimento.

#### Scenario: Rodar suíte com medição de cobertura
- **WHEN** se executa `pytest --cov=src/janus_client --cov-report=term-missing`
- **THEN** o comando roda com sucesso e reporta percentual de cobertura por arquivo, sem erro de "unrecognized arguments"

### Requirement: Caminhos de erro relevantes têm teste dedicado
Os caminhos de erro identificados na revisão (falha de fetch do JWKS, `kid` desconhecido após refresh, token expirado, token com claims ausentes, header malformado) SHALL ter pelo menos um teste que os exercita diretamente.

#### Scenario: JwksCache sem o kid após refresh forçado
- **WHEN** `JwksCache.get_key` é chamado com um `kid` que não existe no JWKS mesmo após `force_refresh`
- **THEN** um teste verifica que `JanusJwksFetchError` é levantada com mensagem mencionando o `kid` ausente

#### Scenario: JWKS retorna resposta sem a lista "keys"
- **WHEN** a resposta HTTP do endpoint JWKS não contém a chave `"keys"` como lista
- **THEN** um teste verifica que `JwksCache._fetch` (via `get_key`) levanta `JanusJwksFetchError`

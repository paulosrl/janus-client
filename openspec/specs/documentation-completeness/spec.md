# documentation-completeness Specification

## Purpose
TBD - created by archiving change revisar-documentar-codebase. Update Purpose after archive.

## Requirements
### Requirement: Todo símbolo público exportado tem docstring
Todo símbolo listado em `janus_client.__all__`, e todo método público das classes ali exportadas (`JanusVerifier`, `JanusTokenPayload`), SHALL ter uma docstring não vazia.

#### Scenario: Auditoria de docstrings da API pública
- **WHEN** se inspeciona `JanusVerifier.__init__`, `JanusVerifier.verify`, `JanusVerifier.close`, `JanusTokenPayload.authorizes`, e cada classe de exceção em `__all__`
- **THEN** cada um tem um `__doc__` não vazio

### Requirement: README documenta a arquitetura do fluxo de verificação
O `README.md` SHALL conter uma seção descrevendo o fluxo de verificação (token → header/kid → JWKS → claims → payload), além do uso básico já documentado.

#### Scenario: Leitor entende o fluxo sem ler o código-fonte
- **WHEN** um integrador lê o `README.md` pela primeira vez
- **THEN** ele encontra uma descrição de como `JanusVerifier.verify()` obtém a chave de verificação e quais validações são aplicadas (assinatura, expiração, issuer, audience), sem precisar abrir `verifier.py`

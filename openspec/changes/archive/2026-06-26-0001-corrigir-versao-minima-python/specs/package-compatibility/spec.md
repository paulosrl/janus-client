## ADDED Requirements

### Requirement: Versão mínima de Python declarada corretamente
O pacote SHALL declarar em `pyproject.toml` (`requires-python`) a versão mínima de Python que é de fato compatível com o código em `src/janus_client/`. Se o código usa uma feature da stdlib disponível apenas a partir da versão N, `requires-python` SHALL ser `>=N` ou mais restritivo.

#### Scenario: Instalação em versão de Python abaixo do piso é rejeitada pelo instalador
- **WHEN** alguém tenta `pip install janus-client` (ou equivalente) usando um interpretador Python anterior à versão mínima declarada em `requires-python`
- **THEN** o instalador rejeita a instalação antes de baixar/instalar o pacote, em vez de instalar com sucesso e falhar depois em `import janus_client`

#### Scenario: Instalação na versão mínima declarada funciona
- **WHEN** o pacote é instalado e importado em um interpretador na versão mínima exatamente igual à declarada em `requires-python`
- **THEN** `import janus_client` e `from janus_client import JanusVerifier` SHALL funcionar sem `ImportError` relacionado a símbolos da stdlib

### Requirement: Versão mínima de Python documentada no README
O `README.md` SHALL informar a versão mínima de Python exigida para instalar e usar o pacote.

#### Scenario: Usuário consulta o README antes de instalar
- **WHEN** um usuário lê o `README.md` para decidir se pode usar o `janus-client` em seu ambiente
- **THEN** ele encontra a versão mínima de Python exigida sem precisar inspecionar `pyproject.toml`

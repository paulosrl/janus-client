## Context

O `janus-client` tem 559 linhas de código + testes em 5 módulos. A revisão atual encontrou três lacunas concretas:
1. `JanusSystemNotAuthorizedError` (em `exceptions.py`) é exportada em `__init__.py` mas nunca é levantada — nem por `JanusVerifier.verify()`, nem por `JanusTokenPayload.authorizes()`, nem pela dependency do FastAPI (que levanta `HTTPException` diretamente).
2. Não há `pytest-cov` configurado; a cobertura real de `src/janus_client/` é desconhecida, embora os 15 testes existentes pareçam cobrir os caminhos felizes.
3. Docstrings públicas existem mas são desiguais (módulos têm docstring de topo, mas nem todos os métodos têm).

## Goals / Non-Goals

**Goals:**
- Remover a exceção morta da API pública, simplificando o contrato de erros.
- Medir cobertura de testes com `pytest-cov` e fechar os gaps relevantes (caminhos de erro, não só caminho feliz).
- Garantir que todo símbolo em `__all__` de `janus_client/__init__.py` tem docstring.
- Adicionar ao README uma seção de arquitetura (diagrama textual do fluxo verify → JWKS → claims) — sem reescrever as seções já existentes.

**Non-Goals:**
- Não adicionar suporte a rotação de chave sem downtime (fora de escopo, já documentado como limitação conhecida).
- Não mudar a lógica de `JwksCache`, `JanusVerifier` ou `require_system_access` além da remoção da exceção morta — sem refactors de comportamento.
- Não perseguir 100% de cobertura por si só; o limiar é "suficiente pra cobrir caminhos de erro relevantes", não um número arbitrário.

## Decisions

- **Remover `JanusSystemNotAuthorizedError` em vez de conectá-la a um fluxo real**: a alternativa (fazer `payload.authorizes()` levantar a exceção, com o chamador decidindo o que fazer) mudaria a assinatura/contrato de `authorizes()` de `bool` pra "levanta ou retorna True", quebrando o uso atual em `fastapi.py` (`if not payload.authorizes(slug): raise HTTPException(403)`). Remover é mais simples e não há indicação de que algum consumidor externo dependa dela (lib tem um único commit).
- **`pytest-cov` em vez de ferramenta de cobertura externa (coverage.py direto)**: `pytest-cov` já integra com o `pytest` existente sem mudar a forma de rodar testes; não há necessidade de configuração adicional de CI nesta change.
- **Limiar de cobertura não é travado em CI nesta change**: focar em fechar os gaps identificados manualmente após medir, em vez de configurar `--cov-fail-under` agora — isso evita travar builds futuros com um número arbitrário antes de entender a curva de cobertura real do projeto.

## Risks / Trade-offs

- [Risco] Remover `JanusSystemNotAuthorizedError` é breaking change de API pública. → Mitigação: o `pyproject.toml` já está em `0.1.0` (pré-1.0), e a exceção nunca foi de fato levantada — o risco real de algum consumidor depender dela é baixíssimo. Documentar a remoção no proposal como **BREAKING**.
- [Risco] Adicionar testes pra fechar gaps de cobertura pode revelar comportamento não especificado (ex: o que `JwksCache` faz se o JWKS retornar uma lista de `keys` vazia). → Mitigação: tratar esses achados caso a caso durante a implementação; se revelar um bug real, pausar e reportar antes de "testar em torno do bug".
- [Risco] Docstrings em excesso podem virar ruído (descrever o que o código já deixa claro). → Mitigação: seguir a convenção já estabelecida no projeto (docstring curta de uma linha, sem prosa multi-parágrafo), consistente com `payload.py` e `exceptions.py`.

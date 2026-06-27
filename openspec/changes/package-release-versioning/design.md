## Context

`janus-client` é distribuído fora de um índice PyPI — o único caminho de instalação hoje é git (clone local com path editable, no caso do `xavier`). Não há CI (`.github/workflows/` não existe) nem tags (`git tag` vazio). O repo já segue OpenSpec/SDD (`openspec/specs/`), então o contrato de release deveria virar uma capability como qualquer outra regra do domínio.

## Goals / Non-Goals

**Goals:**
- Definir regra clara de quando/como a `version` em `pyproject.toml` muda (SemVer) em função do tipo de mudança na API pública.
- Garantir que toda versão publicada tenha uma tag git imutável e um changelog rastreável.
- Documentar a forma de instalação por versão pinada (via git tag), já que não há publish em PyPI nesta fase.

**Non-Goals:**
- Publicar o pacote em PyPI/registry privado (pode vir depois, não é pré-requisito para resolver a fragilidade do pin).
- Automatizar o release via CI/Action (poderia ser uma change futura; aqui o processo pode começar manual/documentado).
- Migrar o `xavier` para consumir a versão pinada — isso é uma change no repo `xavier`, depende desta existir primeiro.

## Decisions

- **SemVer sobre a API pública de `src/janus_client/__init__.py`, não sobre arquivos internos.** Mudança em `verifier.py`/`jwks.py` que não altera símbolos exportados não é breaking. Alternativa rejeitada: versionar por "qualquer commit" (CalVer) — não comunica risco de breaking change pra quem faz pin, que é o problema real a resolver.
- **Tag git anotada `vX.Y.Z` como fonte da verdade da versão, criada só depois do commit que bump `pyproject.toml`.** Alternativa rejeitada: confiar só no campo `version` do `pyproject.toml` sem tag — não dá um ref estável pra `uv add git+...@<ref>` pinar (branch/commit hash funciona, mas tag é o que comunica intenção de release pra humano e ferramenta).
- **Sem publish em PyPI por agora — instalação pinada via `git+https://...@vX.Y.Z`.** Alternativa considerada: publicar em PyPI público. Rejeitada nesta change porque adiciona escopo (conta, token, trust publishing) não necessário pra resolver o problema imediato (xavier só precisa de um ref git estável); pode ser change futura sem quebrar este processo.
- **`CHANGELOG.md` formato Keep a Changelog, mantido manualmente por release.** Alternativa rejeitada: gerar changelog automaticamente a partir de conventional commits — o repo não tem hoje verificação de formato de commit nem CI, automatizar agora seria adicionar infraestrutura não pedida.

## Risks / Trade-offs

- [Processo manual de release pode ser esquecido/pulado] → Mitigação: spec define o requisito (tag obrigatória por bump de versão); revisão de PR no `janus-client` cobre isso até existir automação.
- [Sem PyPI, consumidores externos a `xavier` têm fricção extra pra instalar via git+tag] → Mitigação: aceitável no estado atual (1 consumidor conhecido); documentado como Non-Goal, não bloqueia esta change.
- [Ambiguidade do que conta como breaking change na API pública] → Mitigação: spec lista explicitamente os símbolos exportados em `__init__.py` como superfície coberta por SemVer.

## Migration Plan

1. Adicionar `CHANGELOG.md` com entrada retroativa para `0.1.0`.
2. Criar tag `v0.1.0` apontando para o commit atual de HEAD (estabelece baseline sem bump).
3. Documentar no README a convenção de instalação pinada via tag.
4. Próximos bumps de `version` em `pyproject.toml` seguem a regra SemVer definida na spec, cada um seguido da tag correspondente antes do merge ser considerado "released".

## Open Questions

- Quando (se) publicar em PyPI — decisão fica aberta para change futura, não bloqueia esta.

# Catálogo de documentação: url-shortener

[Introdução do projeto](../../README.pt-BR.md) | [Outro idioma](../en/index.md)

Percurso: propósito/setup → arquitetura/contratos → segurança/falhas → testes/evidência → operações. Na biblioteca: catálogo/dossiê → entrevista por projeto → fundamentos → falhas. Marcos/refactors/handoff históricos descrevem datas originais; revisão/checklist explica escopo atual.

## architecture

Componentes, fluxos e fronteiras implementadas.

- [Arquitetura](../pt-br/architecture/overview.md)

## guides

Setup, pré-requisitos e procedimentos de leitura.

- [url-shortener](../pt-br/guides/project-guide.md)

## testing

Estratégia, inventários e evidências datadas.

- [Testes do Projeto](../pt-br/testing/strategy.md)
- [Validação documental — 2026-10-06](../../../engineering-library/docs/pt-br/projects/engineering-library/docs/pt-br/testing/documentation.md)

## docker

Imagens, serviços, mounts e configuração local.

- [Desenvolvimento Docker e recuperação](../pt-br/docker/development.md)
- [Desenvolvimento com Docker](../pt-br/docker/runtime.md)

## database

Modelos, constraints, migrações e consistência.

- [Identidade, mapeamentos e consistência](../pt-br/database/identity-and-consistency.md)

## api

Contratos expostos e comportamento de clientes.

- [Contrato de criação e redirecionamento](../pt-br/api/contracts.md)
- [Collection do Postman](../pt-br/api/postman.md)

## operations

Diagnóstico, recuperação, checklists e registros históricos.

- [url-shortener: Checklist de conclusão do repositório](../pt-br/operations/completion-checklist.md)
- [Implantação e recuperação coordenada](../pt-br/operations/deployment-and-recovery.md)

## security

Autenticação, autorização, dados e recursos.

- [Autenticação, ofuscação e transporte](../pt-br/security/identity-and-transport.md)

Aplicabilidade e omissões estão justificadas no [checklist](../pt-br/operations/completion-checklist.md). Não há categorias vazias.

## Roteiro prático de implementação e entrevista

[Acompanhe uma requisição, examine falhas e pratique respostas](../pt-br/guides/implementation-study.md).

- [Validação documental — 2026-10-06](testing/verification.md)

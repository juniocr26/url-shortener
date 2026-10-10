# Catálogo de documentação: url-shortener

[Introdução do projeto](../../README.pt-BR.md) | [Outro idioma](../en/index.md)

Percurso: propósito/setup → arquitetura/contratos → segurança/falhas → testes/evidência → operações. Na biblioteca: catálogo/dossiê → entrevista por projeto → fundamentos → falhas. Marcos/refactors/handoff históricos descrevem datas originais; revisão/checklist explica escopo atual.

## architecture

Componentes, fluxos e fronteiras implementadas.

- [Arquitetura](architecture/overview.md)

## guides

Setup, pré-requisitos e procedimentos de leitura.

- [url-shortener](guides/project-guide.md)

## testing

Estratégia, inventários e evidências datadas.

- [Testes do Projeto](testing/strategy.md)
- [Validação documental — 2026-10-06](testing/verification.md)

## docker

Imagens, serviços, mounts e configuração local.

- [Desenvolvimento Docker e recuperação](docker/development.md)
- [Desenvolvimento com Docker](docker/runtime.md)

## database

Modelos, constraints, migrações e consistência.

- [Identidade, mapeamentos e consistência](database/identity-and-consistency.md)

## api

Contratos expostos e comportamento de clientes.

- [Contrato de criação e redirecionamento](api/contracts.md)
- [Collection do Postman](api/postman.md)

## operations

Diagnóstico, recuperação, checklists e registros históricos.

- [url-shortener: Checklist de conclusão do repositório](operations/completion-checklist.md)
- [Implantação e recuperação coordenada](operations/deployment-and-recovery.md)

## security

Autenticação, autorização, dados e recursos.

- [Autenticação, ofuscação e transporte](security/identity-and-transport.md)

Aplicabilidade e omissões estão justificadas no [checklist](operations/completion-checklist.md). Não há categorias vazias.

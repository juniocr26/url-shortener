# url-shortener

[English](README.md) | [Português brasileiro](README.pt-BR.md)

Portfólio FastAPI com criação autenticada de URLs e redirecionamentos permanentes públicos. Redis gera IDs; Cassandra persiste associações; Base62 e ofuscação reversível produzem códigos curtos. Explora decisões de sistemas sem alegar capacidade de produção medida.

## Catálogo de documentação e percurso de leitura

- [Catálogo completo por categoria](docs/pt-BR/index.md)
- [Checklist da revisão e lacunas](docs/pt-BR/operations/completion-checklist.md)

Leia propósito/setup, arquitetura e contratos, segurança/falhas, testes/evidência e implantação/recuperação local. Este projeto é independente no portfólio; procedimentos runtime documentados não foram executados na revisão de 2026-10-10.

## Documentação

- [Arquitetura](docs/pt-BR/architecture/overview.md)
- [Dependências de desenvolvimento e recuperação](docs/pt-BR/docker/development.md)
- [Docker e configuração](docs/pt-BR/docker/runtime.md)
- [Guia do projeto](docs/pt-BR/guides/project-guide.md)
- [Coleção Postman](docs/pt-BR/api/postman.md)
- [Testes](docs/pt-BR/testing/strategy.md)
- [Resultados de validação](docs/pt-BR/testing/verification.md)

[Licença](LICENSE)

## Início rápido e escopo

Em clone novo, instale Docker/Compose, copie o exemplo e configure privadamente Basic Auth, ofuscação e credenciais do banco:

```sh
cp .env.example .env
# Configure private local credentials before starting.
docker compose build
docker compose up -d
```

API: http://localhost:8000. Startup inclui três nós Cassandra e bootstrap de roles/schema. POST /urls exige Basic Auth; GET /{short_code} é público. Coordene recuperação de contador e mapeamentos; não há transação conjunta.

Em checkout existente, atualize a configuração deliberadamente sem sobrescrever o arquivo local.

[Instalação, fluxo de execução, limites operacionais e entrevista do projeto](docs/pt-BR/guides/implementation-study.md). Comandos são orientação; esta manutenção documental não executou testes da aplicação.

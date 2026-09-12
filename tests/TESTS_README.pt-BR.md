# Testes do Projeto

Este diretório contém a suíte automatizada do backend implementado do encurtador de URLs.

A suíte usa `pytest` e deve rodar dentro do container da aplicação.

## Rodar Todos os Testes

Rodar a suíte completa:

```bash
docker compose exec app uv run pytest
```

Modo verboso:

```bash
docker compose exec app uv run pytest -v
```

Parar na primeira falha:

```bash
docker compose exec app uv run pytest -x
```

## Rodar Arquivos Individuais

Testes HTTP/API:

```bash
docker compose exec app uv run pytest tests/test_http.py
```

Testes de serviço:

```bash
docker compose exec app uv run pytest tests/test_url_service.py
```

Testes do gerador de IDs Redis:

```bash
docker compose exec app uv run pytest tests/test_redis_id_generator.py
```

Testes do store Cassandra:

```bash
docker compose exec app uv run pytest tests/test_cassandra_url_store.py
```

Testes Base62:

```bash
docker compose exec app uv run pytest tests/test_base62.py
```

Testes de ofuscação:

```bash
docker compose exec app uv run pytest tests/test_obfuscation.py
```

Rodar um teste específico:

```bash
docker compose exec app uv run pytest tests/test_http.py::test_resolve_short_code_is_public_and_redirects_without_auth -v
```

## Estrutura do Diretório

```text
tests/
├── TESTS_README.md
├── TESTS_README.pt-BR.md
├── test_base62.py
├── test_cassandra_url_store.py
├── test_http.py
├── test_obfuscation.py
├── test_redis_id_generator.py
└── test_url_service.py
```

## Cobertura Atual

A cobertura atual inclui:

- disponibilidade do OpenAPI;
- exigência de Basic Authentication em `POST /urls`;
- rejeição de `POST /urls` sem credenciais;
- rejeição de `POST /urls` com usuário incorreto;
- rejeição de `POST /urls` com senha incorreta;
- validação de requisição para corpo ausente e URL inválida;
- contrato de resposta para criação de URL;
- chamada da geração de ID Redis no fluxo de serviço;
- uso de Base62 no fluxo de criação;
- uso de ofuscação reversível no fluxo de criação;
- códigos públicos com sete caracteres;
- uso de `SHORT_URL_BASE`;
- chamada de persistência Cassandra com o ID e a URL original esperados;
- `GET /{short_code}` público, sem header `Authorization`;
- comportamento de redirect `301 Moved Permanently`;
- validação do header `Location`;
- ausência de `WWW-Authenticate` no GET público bem-sucedido;
- tratamento de códigos desconhecidos e malformados;
- mapeamento de falhas Redis e Cassandra para erros de serviço/HTTP;
- exemplos e round trips de Base62;
- round trips de ofuscação/desofuscação;
- inicialização do contador Redis, preservação de contador existente, incrementos sequenciais e uso de `INCR`;
- comportamento do store Cassandra para salvar, buscar e lidar com IDs ausentes.

## Diferença entre Testes Unitários, API e Integração

A suíte padrão é uma suíte unitária/API:

- testes HTTP usam `httpx.AsyncClient` com transporte ASGI;
- testes de serviço usam geradores Redis e stores Cassandra fake;
- testes Redis usam um cliente Redis fake para validar a semântica do contador;
- testes Cassandra usam uma session Cassandra fake para validar o contrato do store;
- testes Base62 e de ofuscação são testes puros de helpers.

A suíte padrão não exige Redis real ou Cassandra real em toda execução. Ela não deve ser descrita como uma suíte completa de integração com Redis ou Cassandra.

Validação Docker Compose e verificações manuais dão confiança na infraestrutura local:

```bash
docker compose config
docker compose up -d
docker compose ps
```

## Variáveis de Ambiente nos Testes

Os testes usam `monkeypatch` para fornecer valores isolados, como:

- `BASIC_AUTH_USERNAME`
- `BASIC_AUTH_PASSWORD`
- `SHORT_URL_BASE`
- `OBFUSCATING_KEY`

Esses valores são exclusivos dos testes. A suíte não usa nem expõe segredos reais do `.env` local.

O alfabeto Base62 esperado é:

```text
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

## Cobertura Planejada

Coberturas úteis que ainda não fazem parte da suíte padrão:

- testes de integração com Redis real no Docker;
- testes de integração com Cassandra real no cluster Docker;
- testes HTTP end-to-end passando pelo container Uvicorn em execução;
- testes de modos de falha após restart de serviços Docker.

Esses itens só devem ser documentados como implementados depois que os testes correspondentes forem adicionados.

# url-shortener

[English](../en/guide.md) | [Português](guide.md)

`url-shortener` é um projeto de portfólio de Backend/System Design com abordagem Docker-first que implementa a criação de URLs encurtadas e a resolução pública de redirecionamentos utilizando FastAPI, Redis, Cassandra, codificação Base62 e ofuscação reversível de códigos curtos.

O projeto foi intencionalmente mantido pequeno o suficiente para ser explicado em uma entrevista, ao mesmo tempo em que aborda preocupações reais de backend: operações de escrita autenticadas, leituras públicas, geração atômica de IDs, armazenamento persistente, infraestrutura conteinerizada e testes automatizados.

## Stack de Tecnologias

- Python 3.14
- FastAPI e Uvicorn
- Redis 7 com persistência AOF
- Apache Cassandra 5.0, três nós locais, datacenter `datacenter1`
- Codificação Base62 utilizando `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz`
- Ofuscação reversível de códigos curtos de sete caracteres
- Pytest
- `uv`
- Docker e Docker Compose

## API

### `POST /urls`

Cria uma URL encurtada. Este endpoint requer HTTP Basic Authentication utilizando `BASIC_AUTH_USERNAME` e `BASIC_AUTH_PASSWORD`.

Requisição:

```json
{
  "url": "https://example.com/docs"
}
```

Resposta bem-sucedida: `201 Created`

```json
{
  "short_code": "Ab3xZ90",
  "short_url": "http://localhost:8000/Ab3xZ90"
}
```

### `GET /{short_code}`

Resolve um código curto público. Este endpoint é intencionalmente público e não requer um header `Authorization`.

Resposta bem-sucedida: `301 Moved Permanently`

```text
Location: https://example.com/docs
```

Códigos curtos desconhecidos ou malformados retornam `404 Not Found`. Falhas de infraestrutura retornam `503 Service Unavailable` sem expor hostnames internos, credenciais ou stack traces.

A documentação OpenAPI permanece disponível em:

```text
http://localhost:8000/docs
```

## Configuração

Copie o contrato público de variáveis de ambiente e preencha os valores dos secrets locais:

```sh
if [ ! -e .env ]; then cp .env.example .env; fi
```

O arquivo `.env` é ignorado pelo Git. Não faça commit de senhas reais do Redis, Cassandra, Basic Auth ou valores de `OBFUSCATING_KEY`.

Variáveis importantes:

- `SHORT_URL_BASE`: URL base utilizada para construir `short_url`.
- `URL_ID_START`: valor inicial usado como referência para a geração de IDs. O padrão é `14776336`, equivalente a `62^4`.
- `BASIC_AUTH_USERNAME` / `BASIC_AUTH_PASSWORD`: obrigatórios para `POST /urls`.
- `OBFUSCATING_KEY`: chave privada utilizada pela ofuscação reversível dos códigos curtos.
- `REDIS_*`: configurações de conexão com o Redis.
- `CASSANDRA_*`: configurações de conexão, keyspace, role e datacenter do Cassandra.

Startup pode criar/alterar roles, keyspaces e tabelas Cassandra. Não o execute contra dados existentes numa revisão que exige preservação. Use ambiente descartável verificado para escritas. Compose lê `.env`, mas curl no host não herda esses valores automaticamente: configure variáveis Basic Auth no shell sem imprimir credenciais. Substitua o placeholder de código curto entre aspas antes do GET.

## Executando Localmente

Valide a configuração do Compose:

```sh
docker compose config --quiet
```

Inicie todo o ambiente:

```sh
docker compose up -d
```

Verifique o status dos serviços:

```sh
docker compose ps
```

A API é disponibilizada em:

```text
http://localhost:8000
```

Crie uma URL:

```sh
curl -i \
  -u "$BASIC_AUTH_USERNAME:$BASIC_AUTH_PASSWORD" \
  -X POST http://localhost:8000/urls \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com/docs"}'
```

Resolva uma URL sem autenticação:

```sh
curl -i --max-redirs 0 "http://localhost:8000/REPLACE_WITH_SHORT_CODE"
```

Encerre os containers sem excluir os dados do Redis ou Cassandra:

```sh
docker compose stop
```


[Testes](testing.md) · [Arquitetura e trade-offs](architecture.md) · [Docker](docker.md) · [Postman](postman.md)

## Autor

Júnio Rosa

[LinkedIn](https://www.linkedin.com/in/j%C3%BAnio-rosa-94b5731b2/)

## Licença

Este projeto está licenciado sob a MIT License. Consulte o arquivo `LICENSE` para mais detalhes.

# Desenvolvimento com Docker

## Filosofia

Este projeto segue um fluxo Docker-first. O host deve fornecer principalmente:

- Git
- Docker
- Docker Compose

Python 3.14, `uv`, FastAPI, Redis, Cassandra e comandos do projeto devem rodar dentro dos containers sempre que possível.

## Arquivos de Ambiente

`.env.example` é o contrato público de configuração. `.env` é local, privado, ignorado pelo Git e consumido pelo Docker Compose.

Crie o arquivo local:

```sh
cp .env.example .env
```

Preencha valores locais para:

- `BASIC_AUTH_USERNAME`
- `BASIC_AUTH_PASSWORD`
- `OBFUSCATING_KEY`
- `CASSANDRA_USERNAME`
- `CASSANDRA_PASSWORD`
- `REDIS_PASSWORD`, se quiser proteger o Redis local

Não faça commit de `.env` nem de valores reais de segredo.

## Build e Start

Valide a interpolação e a definição dos serviços:

```sh
docker compose config
```

Construa a imagem da aplicação:

```sh
docker compose build
```

Suba o stack completo:

```sh
docker compose up -d
```

O serviço `app` depende de:

- Redis saudável;
- bootstrap Cassandra concluído.

O bootstrap Cassandra espera os três nós ficarem saudáveis, cria ou atualiza a role e o keyspace configurados, e cria a tabela `urls_by_id` se ela ainda não existir.

Verifique o health dos serviços:

```sh
docker compose ps
```

## Aplicação

A aplicação roda Uvicorn com reload habilitado para desenvolvimento local. O código fonte é montado em `/app`.

URL padrão:

```text
http://localhost:8000
```

OpenAPI:

```text
http://localhost:8000/docs
```

Criar uma URL:

```sh
curl -i \
  -u "$BASIC_AUTH_USERNAME:$BASIC_AUTH_PASSWORD" \
  -X POST http://localhost:8000/urls \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com/docs"}'
```

Resolver uma URL sem autenticação:

```sh
curl -i --max-redirs 0 http://localhost:8000/<short_code>
```

`GET /{short_code}` não deve enviar nem exigir Basic Auth.

## Testes

Rodar todos os testes dentro do container da aplicação:

```sh
docker compose exec app uv run pytest
```

Saída detalhada:

```sh
docker compose exec app uv run pytest -v
```

Parar na primeira falha:

```sh
docker compose exec app uv run pytest -x
```

Rodar um arquivo específico:

```sh
docker compose exec app uv run pytest tests/test_http.py
```

A suíte padrão usa fakes para os comportamentos de Redis e Cassandra. Ela não exige infraestrutura real em todos os casos de teste.

## Redis

Redis usa:

- imagem `redis:7-alpine`;
- diretório de dados `.dockerized-redis/`;
- AOF habilitado;
- `appendfsync everysec`;
- senha opcional via `REDIS_PASSWORD`;
- porta no host `127.0.0.1:6379`.

Verificar Redis:

```sh
docker compose exec redis sh -c 'if [ -n "$REDIS_PASSWORD" ]; then REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli ping; else redis-cli ping; fi'
```

Resultado esperado:

```text
PONG
```

O Redis gera IDs de URL com `INCR` atômico. A aplicação inicializa o contador com `SET ... NX`, sem sobrescrever estado persistido.

AOF melhora a durabilidade, mas não é failover nem alta disponibilidade.

## Cassandra

O cluster Cassandra local tem três nós peer-to-peer:

- `cassandra-1`
- `cassandra-2`
- `cassandra-3`

`cassandra-1` é o seed node para descoberta. Seed não significa líder.

A autenticação usa `PasswordAuthenticator` do Cassandra. A role, o keyspace e a tabela de URLs são inicializados de forma idempotente pelo `cassandra-init`.

O keyspace usa `NetworkTopologyStrategy` com fator de replicação 3 no datacenter configurado, por padrão `datacenter1`.

Apenas `cassandra-1` é publicado no host:

```text
127.0.0.1:9042:9042
```

Verificar prontidão CQL:

```sh
docker compose exec cassandra-1 bash /usr/local/bin/url-shortener-cassandra-healthcheck
```

Verificar membros do cluster:

```sh
docker compose exec cassandra-1 nodetool status
```

Cada nó tem seu próprio diretório local de dados, ignorado pelo Git:

- `.dockerized-cassandra/cassandra-1/`
- `.dockerized-cassandra/cassandra-2/`
- `.dockerized-cassandra/cassandra-3/`

Nenhum diretório de dados Cassandra é compartilhado entre os nós.

## Parar e Resetar

Parar serviços sem apagar dados:

```sh
docker compose down
```

Apagar containers e volumes Docker locais:

```sh
docker compose down --volumes
```

Os diretórios bind-mounted de Redis e Cassandra não são apagados por um `docker compose down` normal. Remova esses diretórios apenas quando a intenção for resetar dados locais.

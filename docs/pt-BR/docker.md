# Desenvolvimento com Docker

## Filosofia

Este projeto usa um fluxo Docker-first. O host deve fornecer principalmente:

- Git
- Docker
- Docker Compose

Python 3.14, `uv`, FastAPI, Uvicorn, Redis, Cassandra e comandos específicos do projeto devem rodar dentro dos containers sempre que isso for tecnicamente aplicável.

Isso evita transformar a instalação Python do host em requisito operacional do projeto.

## Arquivos de Ambiente

`.env.example` é o contrato público de configuração. `.env` é local, privado, ignorado pelo Git e consumido pelo Docker Compose através de interpolação de variáveis.

Crie um `.env` local a partir do exemplo público:

```sh
cp .env.example .env
```

Não faça commit de `.env`, credenciais, tokens ou chaves privadas.

`POST /urls` exige `BASIC_AUTH_USERNAME` e `BASIC_AUTH_PASSWORD` no `.env` local. Mantenha os valores reais privados e fora da documentação.

## Build

```sh
docker compose build
```

A imagem da aplicação usa um Dockerfile multi-stage:

- stage `uv`: fornece os binários `uv` e `uvx`.
- stage `build`: resolve e instala dependências do projeto em `/opt/venv`.
- stage `runtime`: contém Python, `uv`, o ambiente virtual e os arquivos do projeto, sem carregar camadas de build desnecessárias.

Os arquivos de dependência são copiados antes do restante do projeto para evitar invalidar a camada de dependências quando apenas o código muda.

## Start e Stop

Subir todos os serviços:

```sh
docker compose up -d
```

Os serviços de longa duração usam `restart: unless-stopped`, então devem voltar depois de uma reinicialização do Docker Desktop quando o Docker estiver rodando.

Parar serviços sem apagar dados:

```sh
docker compose down
```

Apagar containers e dados locais:

```sh
docker compose down --volumes
```

Redis e Cassandra persistem dados em bind mounts locais ignorados pelo Git:

```text
.dockerized-redis/
.dockerized-cassandra/cassandra-1/
.dockerized-cassandra/cassandra-2/
.dockerized-cassandra/cassandra-3/
```

Não remova esses diretórios a menos que a intenção seja resetar os dados locais.

## Rebuild

Recriar imagens e subir o stack:

```sh
docker compose up -d --build
```

Recriar a imagem da aplicação sem cache:

```sh
docker compose build --no-cache app
```

## Container da Aplicação

O serviço `app` executa o esqueleto FastAPI com Uvicorn. No Docker Compose ele usa `--reload` para desenvolvimento local, com o código fonte montado dentro do container.

A API é publicada no host usando `APP_PORT`, que por padrão é `8000`:

```text
http://localhost:8000
```

A documentação OpenAPI automática fica disponível em:

```text
http://localhost:8000/docs
```

Executar Python:

```sh
docker compose run --rm --no-deps app python --version
```

Executar `uv`:

```sh
docker compose run --rm --no-deps app uv --version
```

Sincronizar dependências dentro do Docker:

```sh
docker compose run --rm --no-deps app uv sync --frozen
```

Executar testes:

```sh
docker compose run --rm --no-deps app uv run pytest
```

Abrir shell:

```sh
docker compose run --rm --no-deps app sh
```

Se o stack já estiver rodando:

```sh
docker compose exec app sh
```

Verificar o placeholder público:

```sh
curl -i http://localhost:8000/abc123
```

Verificar `POST /urls` sem autenticação:

```sh
curl -i -X POST http://localhost:8000/urls -H 'Content-Type: application/json' -d '{"url":"https://example.com"}'
```

Verificar `POST /urls` autenticado com credenciais privadas locais:

```sh
curl -i -u "$BASIC_AUTH_USERNAME:$BASIC_AUTH_PASSWORD" -X POST http://localhost:8000/urls -H 'Content-Type: application/json' -d '{"url":"https://example.com"}'
```

## Logs e Health

Ver status e health dos containers:

```sh
docker compose ps
```

Acompanhar todos os logs:

```sh
docker compose logs -f
```

Acompanhar um serviço específico:

```sh
docker compose logs -f app
```

## Redis

Redis usa:

- imagem: `redis:7-alpine`
- diretório de dados: `.dockerized-redis/`
- AOF: habilitado
- política de fsync: `everysec`
- porta no host: `127.0.0.1:6379`

Verificar Redis:

```sh
docker compose exec redis sh -c 'if [ -n "$REDIS_PASSWORD" ]; then REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli ping; else redis-cli ping; fi'
```

Resultado esperado:

```text
PONG
```

Verificar Redis a partir do host quando `redis-cli` estiver disponível localmente:

```sh
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h 127.0.0.1 -p 6379 ping
```

Redis será usado futuramente para gerar IDs com `INCR url:id`, mas esta etapa não inicializa nem altera o contador.

## Cassandra

O cluster Cassandra local usa três nós peer-to-peer:

- `cassandra-1`
- `cassandra-2`
- `cassandra-3`

`cassandra-1` é o seed node para descoberta de topologia. Seed não significa leader.

Autenticação está habilitada com `PasswordAuthenticator` do Cassandra. A role configurada e o keyspace configurado são criados de forma idempotente pelo `cassandra-init`. O keyspace usa `NetworkTopologyStrategy` com replication factor 3 no datacenter configurado.

Apenas `cassandra-1` é publicado no host, e somente em loopback:

```text
127.0.0.1:9042:9042
```

Verificar prontidão CQL usando o mesmo health check do Docker:

```sh
docker compose exec cassandra-1 bash /usr/local/bin/url-shortener-cassandra-healthcheck
```

Verificar membros do cluster:

```sh
docker compose exec cassandra-1 nodetool status
```

Cada nó Cassandra possui seu próprio volume:

- `.dockerized-cassandra/cassandra-1/`
- `.dockerized-cassandra/cassandra-2/`
- `.dockerized-cassandra/cassandra-3/`

Nenhum diretório de dados do Cassandra é compartilhado entre os nós.

Para o DBeaver, use:

```text
Host: localhost
Port: 9042
Datacenter: datacenter1
Keyspace: valor de CASSANDRA_KEYSPACE
Authentication: username/password do ambiente local
```

O Cassandra ainda anuncia endereços internos Docker dos peers para os drivers. Um cliente no host consegue conectar por `localhost:9042`, mas a descoberta de topologia pode exibir peers acessíveis apenas dentro da rede Docker.

O health check usa `cqlsh` contra o próprio nó. Isso verifica se o native transport CQL está aceitando requisições, mas uma checagem mais profunda da topologia deve usar `nodetool status`.

## Network Docker

Todos os serviços entram na mesma bridge network do Compose e se comunicam por nome de serviço. Nenhum IP de container é hardcoded.

A aplicação, Redis e `cassandra-1` publicam portas apenas em loopback para desenvolvimento e administração local. `cassandra-2` e `cassandra-3` não são publicados no host.

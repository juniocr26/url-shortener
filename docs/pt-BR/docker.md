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

Parar serviços sem apagar dados:

```sh
docker compose down
```

Apagar containers e volumes:

```sh
docker compose down --volumes
```

O comando com `--volumes` remove os dados locais de Redis e Cassandra. Use apenas quando a intenção for resetar o ambiente local.

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
- volume de dados: `redis_data`
- AOF: habilitado
- política de fsync: `everysec`

Verificar Redis:

```sh
docker compose exec redis sh -c 'if [ -n "$REDIS_PASSWORD" ]; then REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli ping; else redis-cli ping; fi'
```

Resultado esperado:

```text
PONG
```

Redis será usado futuramente para gerar IDs com `INCR url:id`, mas esta etapa não inicializa nem altera o contador.

## Cassandra

O cluster Cassandra local usa três nós peer-to-peer:

- `cassandra-1`
- `cassandra-2`
- `cassandra-3`

`cassandra-1` é o seed node para descoberta de topologia. Seed não significa leader.

Verificar prontidão CQL:

```sh
docker compose exec cassandra-1 cqlsh 127.0.0.1 9042 -e "DESCRIBE KEYSPACES;"
```

Verificar membros do cluster:

```sh
docker compose exec cassandra-1 nodetool status
```

Cada nó Cassandra possui seu próprio volume:

- `cassandra_data_1`
- `cassandra_data_2`
- `cassandra_data_3`

O health check usa `cqlsh` contra o próprio nó. Isso verifica se o native transport CQL está aceitando requisições, mas uma checagem mais profunda da topologia deve usar `nodetool status`.

## Network Docker

Todos os serviços entram na mesma bridge network do Compose e se comunicam por nome de serviço. Nenhum IP de container é hardcoded.

O Compose não publica portas no host por padrão. Os comandos são executados através dos containers para preservar o fluxo Docker-first.

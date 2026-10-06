# Desenvolvimento Docker e recuperação

Execute no diretório `url-shortener/` do host. Docker Engine/Desktop, Compose (auditoria anterior: v5.1.4), acesso aos registries e espaço para wheels são necessários. Python/uv no host não são exigidos. Args padrão: Python 3.14 e uv 0.8.17; manifest exige Python >=3.14. Redis usa redis:7-alpine e Cassandra cassandra:5.0. Tags flutuantes podem alterar patches: registre versões observadas com os comandos seguros abaixo. uv instala dependências/ferramentas de pyproject.toml/uv.lock; Uvicorn não é instalador.

## Serviços e efeitos de startup

Projeto Compose `url-shortener`: `app` executa FastAPI/Uvicorn com reload, `redis` persiste contador e `cassandra-1/2/3` formam cluster. `cassandra-init` inicializa autenticação/schema. Portas loopback: APP_PORT (8000), REDIS_PORT (6379) e cassandra-1 fixa em 9042.

Entrypoints Cassandra alteram authenticator/authorizer em `/etc/cassandra/cassandra.yaml` no container. Bootstrap pode criar/alterar roles, alterar replicação de system_auth, criar/alterar keyspace da aplicação e criar tabela. Lifespan FastAPI conecta e executa CREATE TABLE IF NOT EXISTS. Redis escreve na geração de URLs. Não há worker/scheduler separado. `up` comum não é auditoria segura de dependências, mesmo com recursos existentes. Esses startups não foram realizados na auditoria anterior; a revisão documental posterior usa armazenamento descartável isolado, conforme [verificação](verification.md).

## Clone novo sem iniciar bancos

```sh
if [ ! -e .env ]; then cp .env.example .env; fi
# Edite credenciais/configuração local; não imprima nem faça commit.
mkdir -p .venv .cache/uv
docker ps --format '{{.Names}} {{.Ports}}'
docker compose -f compose.yaml -f compose.development.yaml config --quiet
docker compose -f compose.yaml -f compose.development.yaml build app
docker compose -f compose.yaml -f compose.development.yaml run --rm --no-deps -T --entrypoint sh app -c 'uv sync --frozen --no-install-project'
docker compose -f compose.yaml -f compose.development.yaml run --rm --no-deps -T --entrypoint sh app -c 'python --version; uv --version; python -c "import sys,fastapi,uvicorn,redis,cassandra.cluster; print(sys.prefix); print(fastapi.__file__)"'
```

Compose exige CASSANDRA_USERNAME/CASSANDRA_PASSWORD para interpolar mesmo selecionando só app. Configure valores locais corretos, não credenciais inventadas para banco existente. Auth/ofuscação seguem `.env.example`. `--no-deps` evita Redis/nós/init; `--entrypoint sh` evita Uvicorn. Comandos executam em `/app`, sem portas. Frozen sync inclui grupo dev; não há necessidade de build de pacote do projeto. `--no-dev` só quando quiser omitir ferramentas, como produção. Não execute uv lock/upgrades para reparar dependências excluídas.

## Dependências físicas no host

| Componente | Caminho no container | Caminho no host | Montagem / finalidade |
| --- | --- | --- | --- |
| Python/uv | `/opt/venv` | `.venv` | Bind; ambiente instalado |
| Pacotes Python | `/opt/venv/lib/python3.14/site-packages` | `.venv/lib/python3.14/site-packages` | Mesmo bind; runtime/dev |
| Cache uv | `/home/app/.cache/uv` | `.cache/uv` | Bind; wheels/fontes/metadados |
| Fontes | `/app` | Raiz do projeto | Bind; expõe .venv também em `/app/.venv` |

Override substitui app_uv_cache no mesmo target. UV_PROJECT_ENVIRONMENT continua `/opt/venv` e PATH começa em `/opt/venv/bin`: instalação/Uvicorn usam o mesmo ambiente do host. Caches nomeados existentes não foram excluídos. Bind de fontes sozinho não persistia `/opt/venv`, antes copiado na imagem. Development tem Python/uv/usuário sem dependências embarcadas; runtime base instala no-dev congelado e mantém comando normal.

Cache de downloads não é ambiente instalado: limpar cache custa downloads sem desinstalar .venv. Bytecode, pytest/cobertura e artefatos não são backups. Não há node_modules/vendor/Maven/Go. .venv/.cache são ignorados e excluídos dos builds.

## Startup e parada

Preparação segura é o fluxo one-off acima. Startup completo foi bloqueado na auditoria anterior por escritas de bootstrap/lifespan. Comando normal `docker compose -f compose.yaml -f compose.development.yaml up -d` inicia bancos/schema e só deve ser operação intencional com conexão correta, fora da verificação de dependências. Clone novo exige inicialização explícita; instalação não cria schema. `--no-deps app` não desabilita inicialização própria da aplicação.

Pare somente serviços que iniciou:

```sh
docker compose -f compose.yaml -f compose.development.yaml stop app
# Apenas se VOCÊ iniciou estes serviços:
docker compose -f compose.yaml -f compose.development.yaml stop redis cassandra-1 cassandra-2 cassandra-3 cassandra-init
```

One-off `run --rm` encerra/remove seu próprio container. Não remova volumes, diretórios de banco nem execute pruning para recuperar dependências.

## Recuperação após exclusão acidental

Pare app antes de sincronizar .venv; bancos podem permanecer ativos para instalar dependências. Recrie diretórios ausentes e repita frozen sync one-off, sem depender de app ativo ou rebuild. .cache/uv excluído mantém pacotes instalados; uv repopula downloads quando necessário. .venv excluído exige sync para recriar pyvenv.cfg/scripts/site-packages; isso não recupera configurações personalizadas.

Mount obsoleto após recriação de diretório exige recriar somente app, apenas quando escritas de startup forem aceitáveis:

```sh
docker compose -f compose.yaml -f compose.development.yaml up -d --no-deps --force-recreate app
```

Esse comando inicia lifespan/schema e não foi executado na auditoria anterior. Rebuild só para mudanças Python/uv/imagem de sistema.

## Recuperação de configuração

Para `.env` ausente, copie template somente se não existir e recupere valores personalizados de backup/fonte de segredos. Preserve OBFUSCATING_KEY original para links existentes e credenciais de banco/auth. Template não recupera esses valores; não os altere/invente como reparo de dependências.

Para Compose, Dockerfile, `docker/cassandra/*.sh`, manifests/lockfile/configuração versionados ausentes, confirme ausência e restaure caminho específico com `git restore --source=HEAD -- path/to/missing-file`. Arquivos/alterações não commitados exigem backup. Não restaure diretórios sobre alterações existentes; nenhum gerador recupera configurações personalizadas.

uv sync recria metadados de ambiente ausente. Para pyvenv.cfg excluído em ambiente intacto, pare app e use reparo testado que preserva os arquivos existentes:

```sh
docker compose -f compose.yaml -f compose.development.yaml run --rm --no-deps -T --entrypoint sh app -c 'uv venv --allow-existing --python /usr/local/bin/python3 /opt/venv && uv sync --frozen --no-install-project'
```

Isso repara metadados/scripts gerados, não configurações personalizadas. Outras corrupções parciais não foram testadas. Cache uv é regenerável; dados personalizados guardados ali precisam de backup.

`/etc/cassandra` vem da imagem/entrypoints, não é configuração persistida no host. Recriar nó regenera defaults da imagem/ambiente mas inicia banco e não foi testado naquela auditoria. Configuração manual perdida exige backup, não uv sync. `.dockerized-cassandra/cassandra-*` e `.dockerized-redis` contêm estado persistente, inclusive metadados/AOF: recupere somente por procedimentos de backup. Inicializar diretório vazio não recupera registros/contador antigos. Não foi identificado outro diretório gerado de configuração da aplicação.

## Diagnóstico

Use ambos os arquivos: base sozinho usa `/opt/venv` da imagem/cache nomeado. Confira mounts com `docker inspect CONTAINER --format '{{json .Mounts}}'`; ambos os targets devem ser binds. `python -c 'import sys; print(sys.prefix)'` deve mostrar `/opt/venv`. `uvicorn --version` não inicia FastAPI; não use app/testes dependentes do banco para diagnosticar pacotes.

UID/GID app padrão 1000 precisam escrever nos binds. Docker Desktop funcionou na auditoria anterior. Linux pode usar APP_UID/APP_GID do proprietário ou somente setup com `--user "$(id -u):$(id -g)" -e HOME=/tmp`, preservando UV_CACHE_DIR/UV_PROJECT_ENVIRONMENT. Inspecione/corrija somente diretórios gerados afetados; sem chmod 777 nem alterações recursivas amplas.

Confira listeners antes de startup. APP_PORT/REDIS_PORT são configuráveis; Cassandra 9042 é fixa e pode bloquear inicialização ou exigir override pontual. Não pare serviços alheios. APP_PORT muda também porta interna app; alterar REDIS_PORT merece revisar conexão app porque Redis continua em 6379 internamente. Mudanças de rede não fazem parte desta revisão.

.venv persistido tem links/scripts `/opt/venv` e wheels nativos Linux. Não ative diretamente no macOS/Windows. Reinstale na plataforma correspondente após mudança Python/arquitetura; ambiente nativo do host deve ser separado. Persistência não dá portabilidade de binários.

## Auditoria anterior — 2026-10-06

Manifests, lockfile, Cassandra startup/health e lifespan/adapters revisados. Configuração resolveu binds de ambiente/cache, preservando mounts de banco. Target development de dependências construído; produção mantida. Não havia containers/listeners conflitantes na 8000/6379/9042. Startup completo, conexão/schema e testes não foram executados naquela auditoria por efeitos de escrita.

Frozen sync instalou 32 pacotes com dev. Versões: CPython 3.14.8, uv 0.8.17 e Uvicorn 0.52.4 Linux. FastAPI físico no host, pyvenv.cfg e cache conferidos. Containers de instalação e novo mostraram sys.prefix `/opt/venv` e pacote naquele ambiente; container novo executou sync offline/version check. Nenhum lifespan/recurso de banco foi instanciado.

Recuperação com diretórios vazios passou em binds temporários separados de ambiente/cache: 32 pacotes/imports conferidos. Nesse ambiente isolado, somente pyvenv.cfg foi excluído; uv venv --allow-existing, sync offline e imports o restauraram. Dependências/configurações normais nunca foram excluídas/renomeadas. Temporários removidos após saída dos containers; nenhum container de auditoria ficou rodando.

## Conferência física e recuperação versionada

```sh
test -f .venv/lib/python3.14/site-packages/fastapi/__init__.py
test -f .venv/pyvenv.cfg
test -d .cache/uv/wheels-v5
for path in .env.example compose.yaml docker/Dockerfile docker/cassandra/entrypoint.sh docker/cassandra/bootstrap.sh docker/cassandra/healthcheck.sh pyproject.toml uv.lock app/core/config.py; do
  if [ ! -e "$path" ]; then git restore --source=HEAD -- "$path"; fi
done
```

Só recupera arquivos versionados ausentes; configuração não versionada requer backup. Confira versionamento do override/guia e preserve alterações locais. Build de produção não foi reexecutado; estágio revisado pelo Dockerfile.

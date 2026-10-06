# Validação documental — 2026-10-06

## Isolamento antes do startup

Não havia containers rodando antes deste projeto. Compose/bootstrap e lifespan FastAPI revisados: podem alterar roles/keyspaces/tabelas. `.dockerized-redis` e `.dockerized-cassandra` existentes foram excluídos da validação. O projeto Compose separado `portfolio-url-doc-validation` usou `compose.yaml` e `compose.development.yaml` existentes mais override de segurança temporário fora do repositório.

Cada target de dados Redis/Cassandra foi substituído por diretório novo e vazio verificado sob `/private/tmp/portfolio-url-doc-*`. Conexões app foram fixadas em redis:6379 e cassandra-1/2/3:9042 com credenciais fictícias descartáveis e keyspace `documentation_isolated`. Rede backend interna exclusiva impediu conexões externas. JSON Compose resolvido comprovou isolamento antes de `up -d`; mounts/rede reais foram conferidos novamente antes do POST. Isolamento de storage/conexão, não apenas nome de banco test. Ambientes existentes e dados persistidos não foram alterados.

## Comandos e resultados

Os comandos usaram este prefixo, com `TEMP_OVERRIDE` apontando apenas à configuração temporária verificada:

```sh
docker compose -p portfolio-url-doc-validation -f compose.yaml -f compose.development.yaml -f "$TEMP_OVERRIDE"
```

| Comando ou verificação | Resultado real |
| --- | --- |
| `config --format json` e asserções de mounts/conexões/rede | Passou antes de startup; nenhum target de dados existente |
| `up -d` | Passou; app, Redis e três Cassandra saudáveis; bootstrap saiu 0 |
| `run --rm --no-deps -T --entrypoint sh app -c 'uv run --no-sync pytest -p no:cacheprovider'` | 82 passaram em 0,54 s; testes existentes usam fakes e não executam lifespan |
| Mounts/rede Docker reais | Isolamento reconfirmado |
| `exec -T cassandra-1 nodetool status` | Três nós Up/Normal em datacenter1 |
| GET `/openapi.json` por Python/urllib no container | HTTP 200 |
| POST `/urls` sem credenciais | HTTP 401 |
| POST `/urls` com credenciais descartáveis | HTTP 201 e código de sete caracteres |
| GET público do código gerado, sem seguir redirect | HTTP 301 e Location esperado |
| GET `/abc` | HTTP 404 |
| Linhas Cassandra/contador Redis isolados antes | Tabela vazia e contador ausente |
| Linhas isoladas após smoke | Exatamente um mapping temporário |

Script temporário Python usou configuração/adapters Cassandra/Redis da aplicação para conferir alvos/vazio antes da única escrita. Não seguiu redirect externo example.com. São smoke checks reais isolados adicionais aos testes com fakes, não suíte completa existente de integração/falhas. Build/pulls usaram targets Docker existentes; manifests/lockfiles não mudaram. Rede interna não expôs listeners utilizáveis no host; HTTP executou dentro de app.

## Parada e limpeza

Com mesmo prefixo, `stop app redis cassandra-1 cassandra-2 cassandra-3 cassandra-init` parou somente serviços criados nesta tarefa. Só containers/rede desse projeto descartável foram removidos depois. Diretórios novos, mapping, contador e provisionamento fictício foram removidos após parada. Containers/volumes/diretórios originais e registros/schema existentes foram preservados. Não houve down -v, pruning, reset, truncate ou migração destrutiva.

## Limites e conferência documental

Nenhum check real usou bancos existentes. Deploy de produção, navegador/Postman, carga, failover, restart/recuperação e isolamento físico entre hosts não foram testados. JSON Postman inspecionado: `url-shortener.local.postman_environment.json` declara collection v2.1, contém duas requisições e defaults Basic Auth vazios. Documentação aponta ao nome real. Pares de idiomas, links/âncoras, caminhos e whitespace passaram; não restam exceções de documentação em localização obrigatória.

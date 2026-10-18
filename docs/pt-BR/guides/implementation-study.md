# Acompanhe uma URL curta e explique seus limites de consistência

Revisão estática: 2026-10-18 em `40e4ea05d6e4d2d5ae81d2020ec6ea7936330d44`. Esta aplicação independente em FastAPI serve ao estudo de identidade numérica, códigos reversíveis e falhas entre dois armazenamentos. Implementa criação autenticada e redirects permanentes públicos; não possui frontend móvel, broker, provedor de pagamentos ou integração com outra aplicação do portfólio.

## Instale e acompanhe

Use o [setup Docker](../docker/runtime.md) e `.env.example`; configure privadamente credenciais Basic, chave de ofuscação e credenciais Cassandra. `docker compose up -d` depende das etapas documentadas de imagem/build e inicia um Redis, três nós Cassandra e bootstrap. O bootstrap altera roles/schema e a aplicação também cria sua tabela. É orientação operacional, não ação executada aqui. API padrão localhost:8000. [Recuperação de desenvolvimento](../docker/development.md) separa reparo de dependências de destruição de dados.

`app/api/routes.py` → controller → `UrlShortenerService` → infraestrutura. POST `/urls` valida URL HTTP(S), verifica Basic Auth, obtém ID via Redis `SET NX`/`INCR`, codifica Base62, aplica permutação afim reversível de sete caracteres e grava `id → original_url` no Cassandra. Retorna então 201. GET `/{short_code}` inverte a transformação e retorna 301; não consulta Redis nem exige Basic Auth. Lifespan reutiliza e fecha o cliente Redis e sessão/cluster Cassandra.

## Consistência e segurança

Inicializar Redis preserva chave existente, mas `_initialized` fica na memória do processo. Apagar o contador depois pode reiniciar `INCR` abaixo da faixa esperada. AOF `everysec` não fornece HA nem prova a sobrevivência de todo ID confirmado. INSERT comum no Cassandra é upsert; rollback do contador pode sobrescrever mapeamento. Lacunas após falhas são aceitáveis; reutilização de IDs compromete correção. Não há transação entre armazenamentos ou POST idempotente. Timeout de escrita pode ocultar persistência; retry aloca outro ID.

RF=3 e três nós locais não demonstram domínios de falha independentes. O perfil do driver define roteamento no DC local, sem nível explícito de consistência. Raciocínio de quorum é teoria até configurar e testar uma política. Restaurar contador e mapeamentos exige planejamento coordenado; nenhum exercício de recuperação foi executado aqui.

A transformação afim é ofuscação, não criptografia, autorização ou TLS. Mudar chave/alfabeto quebra links sem decodificação versionada. Padding com `0` literal e validação apenas de tamanho/unicidade deixam a preocupação conhecida com alfabetos personalizados. Preserve o alfabeto padrão e chave estável; este achado documental não é correção de runtime. Respostas 301 públicas podem ser cacheadas, limitando futura edição de destino. `HttpUrl` valida sintaxe, não segurança do destino; o backend não busca a URL. Basic Auth exige transporte protegido além de loopback. Privilégios de superuser no bootstrap, controles de abuso e TLS público permanecem lacunas de produção.

## Preparação para entrevista

**Introdutória — Por que redirects podem sobreviver à falha do Redis?** Resolução lê Cassandra após decodificar; Redis apenas aloca na criação. Aprofundamento: uma aplicação recém-iniciada ainda exige dependências de startup; independência por operação não prova disponibilidade de cold start.

**Intermediária — Perder um ID é falha transacional?** Não há transação conjunta. Lacuna é inofensiva com IDs únicos; perder a resposta HTTP após commit no Cassandra deixa resultado desconhecido. Aprofundamento: sequência e mapeamento no mesmo banco relacional simplificam coordenação; códigos aleatórios exigem tratamento condicional de colisão.

**Desafiadora — RF=3 e INCR provam recuperação segura de desastre?** Não. Replicação não coordena histórico Redis, protege upserts nem substitui backups. Aprofundamento: especifique consistência e ordem de recuperação, teste perda de contador e concorrência em recursos isolados e rejeite reutilização antes de prometer recuperação segura. São requisitos propostos, não controles implementados.

[API](../api/contracts.md), [identidade](../database/identity-and-consistency.md), [segurança](../security/identity-and-transport.md) e [estratégia de testes](../testing/strategy.md) detalham os contratos. Fakes existentes cobrem HTTP, helpers e chamadas dos adaptadores; não demonstram partições/failover reais. Nenhuma suíte da aplicação ou cluster foi executado nesta revisão.

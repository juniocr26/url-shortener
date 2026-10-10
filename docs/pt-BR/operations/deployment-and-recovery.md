# Implantação e recuperação coordenada

[English](../../en/operations/deployment-and-recovery.md) | [Português brasileiro](deployment-and-recovery.md)

Revisão estática do código: 2026-10-10. Fatos implementados, teoria geral e mudanças hipotéticas são separados abaixo. Comandos runtime não foram executados.

Lifespan cria recursos Redis/Cassandra, assegura a tabela e expõe adapters no estado da aplicação. Cassandra é inicializado antes de servir; o contador Redis é inicializado sob demanda. `finally` fecha Cassandra e Redis; falha ao criar conexão Cassandra encerra o cluster. O comando Compose padrão usa Uvicorn com reload para desenvolvimento local. Três nós Cassandra, armazenamento AOF Redis e bind mounts são topologia de estudo, não release HA produtivo verificado.

A revisão de atualização/rollback precisa preservar dados e contrato do espaço de códigos. Nunca reinicie Redis independentemente dos mapeamentos Cassandra nem presuma que recriar contêineres recria credenciais em volumes inicializados. Backup/restauração precisam coordenar ambos os bancos e conservar a configuração de ofuscação; persistência de volume não é backup. São requisitos de procedimento, não ensaio de restore realizado aqui. Não há ferramenta de recuperação coordenada, pipeline de releases ou RTO/RPO medido. Não há ciclo versionado de edição de destino.

Testes fake isolam codificação, alocação, ordem do serviço e mapeamento de erros HTTP sem provar consistência, autenticação ou failover reais do cluster. Instruções Docker/Postman existentes não foram executadas nesta revisão. OpenAPI acessível prova startup HTTP, não prontidão das dependências na requisição. Custos potenciais são chamadas de rede síncronas, serialização Redis, trabalho de rede/réplicas Cassandra e capacidade de threads do cliente; topologia não fornece gráfico de vazão. Lacunas incluem injeção real de falhas, recuperação de perda do contador, carga concorrente, escolha de política quorum e ensaios de implantação/rollback.

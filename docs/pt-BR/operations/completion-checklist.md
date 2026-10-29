# Manutenção documental — 2026-10-18

Base `40e4ea05d6e4d2d5ae81d2020ec6ea7936330d44`; árvore inicialmente limpa. Esta é manutenção documental estática. Contagens históricas de testes abaixo pertencem à data/revisão original e não foram reexecutadas.

- [x] Inventário e revisão de código
- [x] Estrutura e conteúdo da implementação
- [x] Cobertura equivalente em inglês/português
- [x] Navegação e links locais
- [x] Entrevista do projeto e cobertura na Engineering Library
- [x] Lacunas de evidência e exceções justificadas

[Revisão atual e limites de evidência](../../pt-br/guides/implementation-study.md).

A conclusão diz respeito à cobertura documental, não à prontidão de produção, certificação de runtime ou resolução das lacunas de evidência. Resultados do validador estão na revisão da biblioteca.

## Checklists históricos (datas e escopo originais)

# url-shortener: Checklist de conclusão do repositório

Revisão estática em 2026-10-10; sem execução runtime. Itens marcados indicam documentação concluída, não funcionalidades entregues ou lacunas encerradas.

- [x] Inventário: documentação e código/configuração/testes inspecionados; inventário original no manifest da biblioteca.
- [x] Reestruturação: categorias equivalentes por idioma; IDs/histórico ADR preservados; arquivos exigidos por ferramentas mantidos.
- [x] Revisão de conteúdo: mecanismos, contratos, alternativas, falhas e limites de evidência explicados.
- [x] Cobertura bilíngue: páginas mantidas equivalentes en/pt-BR; históricos identificados explicitamente.
- [x] Navegação: README e catálogo por idioma alcançam cada documento mantido.
- [x] Cobertura Engineering Library: explicações completas e respostas substanciais preservadas/ampliadas.
- [x] Validação de links/anchors/numeração: verificação final sem erros; 18 warnings de links restritos de fixtures registrados no relatório da biblioteca.

## Evidência inspecionada

- [app/main.py](../../../app/main.py)
- [app/api/routes.py](../../../app/api/routes.py)
- [app/core/security.py](../../../app/core/security.py)
- [app/services/url_service.py](../../../app/services/url_service.py)
- [app/infrastructure/redis_id_generator.py](../../../app/infrastructure/redis_id_generator.py)
- [app/infrastructure/cassandra_url_store.py](../../../app/infrastructure/cassandra_url_store.py)
- [app/helpers/base62.py](../../../app/helpers/base62.py)
- [app/helpers/obfuscation.py](../../../app/helpers/obfuscation.py)
- [compose.yaml](../../../compose.yaml)

## Cobertura de entrevista e contraparte na biblioteca

Contratos POST/301; Basic versus TLS; matemática Base62/afim; falhas entre bancos; inicialização/perda Redis; modelo Cassandra/RF/consistência; lifecycle, testes e recuperação.

[Self-contained dossier / Dossiê](../../../../engineering-library/docs/pt-br/projects/url-shortener/docs/pt-br/architecture/overview.md) | [Interview / Entrevista](../../../../engineering-library/docs/pt-br/projects/url-shortener/docs/pt-br/faq/index.md)

## Aplicabilidade das categorias

| Categoria | Tratamento / justificativa |
| --- | --- |
| payments | Não aplicável: pagamentos ausentes. No Payment Lab, conciliação/Stripe são apenas direção futura. |
| integrations | Chamadores Redis/Cassandra, contratos/falhas em database/api/architecture; sem parceiro runtime do portfólio. |
| deployment | Topologia reload local e limites de recuperação em operations/docker. |
| observability | Probe OpenAPI e limites diagnósticos em operations. |
| adr | Sem série ADR histórica; escolhas/trade-offs observados ficam junto à arquitetura ou explicações do validador, sem inventar histórico. |
| benchmarks | Não aplicável: sem medições de desempenho verificadas adequadas a gráficos; nenhuma executada. |

Categorias presentes no índice contêm conteúdo mantido; categorias tratadas em outros locais não recebem pastas vazias. ADR/comparações conservam histórico; nenhuma motivação ou data histórica nova foi inventada.

## Lacunas restantes dependentes de evidência

Padding de alfabeto personalizado, recuperação coordenada, consistência explícita do driver, failover/carga, abuso/TLS e rollback produtivo.

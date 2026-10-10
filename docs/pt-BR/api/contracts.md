# Contrato de criação e redirecionamento

[English](../../en/api/contracts.md) | [Português brasileiro](contracts.md)

Revisão estática do código: 2026-10-10. Fatos implementados, teoria geral e mudanças hipotéticas são separados abaixo. Comandos runtime não foram executados.

`POST /urls` exige credenciais HTTP Basic e o campo JSON `url` como `HttpUrl` do Pydantic; sucesso retorna 201 com `short_code` e `short_url`. A rota chama um controller que delega a `UrlShortenerService`. O serviço aloca inteiro, codifica Base62, aplica ofuscação reversível, armazena `(id, original_url)` no Cassandra e constrói a URL pública com `SHORT_URL_BASE`. A validação verifica sintaxe HTTP/HTTPS; não busca o destino, não prova disponibilidade nem classifica abuso. URLs repetidas geram IDs diferentes, sem deduplicação.

`GET /{short_code}` é público. A desofuscação exige exatamente sete caracteres, recupera o inteiro, consulta Cassandra e retorna 301 com Location. Código inválido e mapeamento ausente viram 404. Erros de configuração viram 500; erros de adapters Redis/Cassandra viram 503 sanitizado. Redis não participa da resolução, portanto uma aplicação inicializada pode resolver enquanto Redis está indisponível. Cassandra é necessário nos dois caminhos. O startup cria sessão Cassandra e assegura a tabela; health contra OpenAPI não testa uma nova consulta de mapeamento ou incremento do contador.

A API e clientes são síncronos; declarar rota async não tornaria essas chamadas não bloqueantes. Redirecionamentos permanentes podem ser armazenados por navegadores/intermediários, desviando acessos posteriores da aplicação; uma futura análise de cliques não necessariamente veria todas as visitas. Não há expiração, destino editável, moderação de abuso, rate limit, chave de idempotência ou endpoint analítico. Alterar esses contratos exige projeto e testes, não inferências a partir do nome do domínio.

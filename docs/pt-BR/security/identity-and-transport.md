# Autenticação, ofuscação e transporte

[English](../../en/security/identity-and-transport.md) | [Português brasileiro](identity-and-transport.md)

Revisão estática do código: 2026-10-10. Fatos implementados, teoria geral e mudanças hipotéticas são separados abaixo. Comandos runtime não foram executados.

HTTP Basic verifica usuário e senha configurados com `secrets.compare_digest`. Credenciais inválidas retornam 401 com desafio Basic; configuração ausente retorna 500. Credenciais Basic são codificação, não cifra de transporte. A aplicação local não configura terminação TLS. A rota pública de redirect é intencionalmente não autenticada e possuir código curto não é verificação de autorização. CORS ou rede Compose privada não substituiriam autenticação da API.

A transformação afim é ofuscação reversível, mesmo usando SHA-256 para derivar parâmetros. Não é cifra autenticada, hash de senha ou fronteira de sigilo. Pares conhecidos de entrada/saída e sua estrutura algébrica tornam inadequadas alegações de segurança criptográfica. Alterar chave ou alfabeto muda a decodificação de links existentes; não há prefixo de versão ou consulta de migração. Código aleatório armazenado evitaria acoplamento a uma chave global, mas exigiria colisões e outra chave de consulta; cifra autenticada introduziria outros requisitos de tamanho e gestão de chaves. Nenhuma está implementada.

A sintaxe do destino é validada, mas não há allowlist ou reputação. A aplicação redireciona em vez de buscar URLs, portanto a criação atual não é fetch de URL no servidor; um futuro preview/fetch criaria novas preocupações de SSRF. Evite logs de credenciais e destinos sensíveis completos. Arquivos reais de ambiente e conteúdo dos bancos não foram lidos. Lacunas incluem implantação TLS, controle de abuso, rotação de credenciais e migração testada de código/chave.

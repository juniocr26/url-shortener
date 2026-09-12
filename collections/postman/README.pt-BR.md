# Collection do Postman

Este diretório contém a collection do Postman utilizada para interagir com a API do URL Shortener durante o desenvolvimento local.

## Collection

```text
url-shortener.postman_collection.json
```

A collection contém requisições para os principais fluxos da API:

- criação de uma URL encurtada através de `POST /urls`;
- resolução de um short code através de `GET /{short_code}`.

## Importando a Collection

1. Abra o Postman.
2. Selecione **Import**.
3. Selecione `url-shortener.postman_collection.json`.
4. Importe a collection.

Não é necessário utilizar um arquivo de environment separado do Postman.

## Variáveis da Collection

A collection utiliza as seguintes variáveis:

| Variável              | Descrição                                      | Valor padrão            |
| --------------------- | ---------------------------------------------- | ----------------------- |
| `base_url`            | Endereço local da API do URL Shortener         | `http://localhost:8000` |
| `basic_auth_username` | Usuário utilizado pelo endpoint POST protegido | Vazio                   |
| `basic_auth_password` | Senha utilizada pelo endpoint POST protegido   | Vazio                   |
| `short_code`          | Short code utilizado pelo endpoint GET público | Vazio                   |

Configure localmente no Postman as credenciais de Basic Authentication antes de utilizar o endpoint de criação.

As credenciais não são armazenadas na collection versionada.

## Criando uma URL Encurtada

Requisição:

```http
POST /urls
```

Este endpoint exige Basic Authentication.

Exemplo de body:

```json
{
  "url": "https://example.com"
}
```

Uma requisição bem-sucedida retorna `201 Created` com o short code e a URL encurtada gerados.

A collection armazena o `short_code` retornado na variável `short_code`, permitindo que ele seja reutilizado pela requisição de resolução.

## Resolvendo uma URL Encurtada

Requisição:

```http
GET /{short_code}
```

Este endpoint é público e não exige autenticação.

A requisição utiliza o valor atual de:

```text
{{short_code}}
```

Quando o short code é encontrado, a API retorna:

```text
301 Moved Permanently
```

com a URL original no header `Location`.

Dependendo das configurações de redirecionamento do Postman, o cliente pode seguir automaticamente o redirect em vez de exibir a resposta `301` inicial.

## Fluxo de Uso

```text
POST /urls
    ↓
Cria a URL encurtada
    ↓
Armazena o short_code retornado
    ↓
GET /{short_code}
    ↓
301 Moved Permanently
    ↓
URL original
```

## Segurança

Não faça commit de credenciais reais nesta collection.

Os seguintes valores devem permanecer locais:

- credenciais de Basic Authentication;
- credenciais do Redis;
- credenciais do Cassandra;
- `OBFUSCATING_KEY`;
- qualquer outro segredo presente no `.env`.

A collection versionada deve conter apenas valores seguros, placeholders e configurações de desenvolvimento que não sejam sensíveis.

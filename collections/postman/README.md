# Postman Collection

This directory contains the Postman collection for interacting with the URL Shortener API during local development.

## Collection

```text
url-shortener.postman_collection.json
```

The collection provides requests for the main API flows:

- creating a shortened URL through `POST /urls`;
- resolving a short code through `GET /{short_code}`.

## Importing the Collection

1. Open Postman.
2. Select **Import**.
3. Select `url-shortener.postman_collection.json`.
4. Import the collection.

No separate Postman environment file is required.

## Collection Variables

The collection uses the following variables:

| Variable              | Description                                  | Default                 |
| --------------------- | -------------------------------------------- | ----------------------- |
| `base_url`            | Local URL Shortener API address              | `http://localhost:8000` |
| `basic_auth_username` | Username used by the protected POST endpoint | Empty                   |
| `basic_auth_password` | Password used by the protected POST endpoint | Empty                   |
| `short_code`          | Short code used by the public GET endpoint   | Empty                   |

Set the Basic Authentication credentials locally in Postman before using the creation endpoint.

Credentials are intentionally not stored in the version-controlled collection.

## Create a Short URL

Request:

```http
POST /urls
```

This endpoint requires Basic Authentication.

Example request body:

```json
{
  "url": "https://example.com"
}
```

A successful request returns `201 Created` with the generated short code and short URL.

The collection stores the returned `short_code` in the `short_code` collection variable so it can be reused by the resolution request.

## Resolve a Short URL

Request:

```http
GET /{short_code}
```

This endpoint is public and does not require authentication.

The request uses the current value of:

```text
{{short_code}}
```

A successfully resolved short code returns:

```text
301 Moved Permanently
```

with the original URL in the `Location` response header.

Depending on Postman redirect settings, the client may automatically follow the redirect instead of displaying the initial `301` response.

## Typical Workflow

```text
POST /urls
    ↓
Create short URL
    ↓
Store returned short_code
    ↓
GET /{short_code}
    ↓
301 Moved Permanently
    ↓
Original URL
```

## Security

Do not commit real credentials to this collection.

The following values must remain local:

- Basic Authentication credentials;
- Redis credentials;
- Cassandra credentials;
- `OBFUSCATING_KEY`;
- any other secrets from `.env`.

The version-controlled collection should contain only safe defaults, placeholders, and non-sensitive development values.

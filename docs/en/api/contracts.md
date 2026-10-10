# Creation and redirect contract

[English](contracts.md) | [Português brasileiro](../../pt-BR/api/contracts.md)

Static source review: 2026-10-10. Implemented facts, general theory and hypothetical changes are distinguished below. Runtime commands were not executed.

`POST /urls` requires HTTP Basic credentials and a Pydantic `HttpUrl` JSON field `url`; success is 201 with `short_code` and `short_url`. The route calls a controller, which delegates to `UrlShortenerService`. The service allocates an integer, encodes Base62, applies reversible obfuscation, stores `(id, original_url)` in Cassandra, and constructs the public URL from `SHORT_URL_BASE`. Input validation checks HTTP/HTTPS syntax; it does not fetch the destination, prove it is reachable or classify abuse. Repeated URLs produce distinct IDs rather than deduplicated records.

`GET /{short_code}` is public. It requires exactly seven characters for deobfuscation, reverses to the integer, looks up Cassandra and returns 301 with Location. Invalid code and absent mapping both become 404. Configuration errors become 500; Redis/Cassandra adapter errors become sanitized 503. Redis is absent from the resolution path, so a healthy initialized app may still resolve while Redis is down. Cassandra is required for both paths. Startup creates a Cassandra session and ensures the mapping table; a running health probe against OpenAPI does not test a fresh mapping lookup or counter increment.

This is a synchronous API with synchronous dependency clients; declaring an async route would not make those calls nonblocking. Permanent redirects may be cached by browsers/intermediaries and later redirects can bypass the application, so future click analytics would not necessarily see every visit. There is no expiration, editable destination, abuse moderation, rate limit, idempotency key or analytics endpoint. Changing these contracts requires design and tests rather than inferring them from the domain name.

# Trace a short URL and defend its consistency limits

Static review: 2026-10-18 at `40e4ea05d6e4d2d5ae81d2020ec6ea7936330d44`. This independent FastAPI application is for studying numeric identity, reversible codes and two-store failures. It implements authenticated creation and public permanent redirects; it has no mobile frontend, broker, payment provider or integration with another portfolio application.

## Install and trace

Use [Docker setup](../docker/runtime.md) and the safe `.env.example`; configure local Basic credentials, obfuscation key and Cassandra credentials privately. `docker compose up -d` builds on the documented image/build prerequisites and starts one Redis, three Cassandra nodes and bootstrap. Bootstrap changes roles/schema and the app also creates its table. This is operational guidance, not an action executed here. API defaults to localhost:8000. [Development recovery](../docker/development.md) separates dependency repair from data destruction.

`app/api/routes.py` → controller → `UrlShortenerService` → infrastructure. POST `/urls` validates an HTTP(S) URL, checks Basic Auth, obtains an ID through Redis `SET NX`/`INCR`, Base62-encodes it, applies the reversible seven-character affine permutation and writes `id → original_url` to Cassandra. It then returns 201. GET `/{short_code}` reverses that mapping and returns 301; it does not query Redis or require Basic Auth. Lifespan reuses and closes the Redis client and Cassandra session/cluster.

## Consistency and security

Redis initialization is non-destructive when the key exists, but `_initialized` is process memory. Deleting a counter after initialization can restart `INCR` below the intended range. Redis AOF `everysec` is neither HA nor a proof that every acknowledged ID survives recovery. Cassandra ordinary INSERT is an upsert, so counter rollback can overwrite a mapping. Allocated gaps after failed writes are acceptable; reused IDs are a correctness risk. No cross-store transaction or idempotent POST contract exists. A timed-out write might have persisted; retry allocates another ID.

RF=3 and three local nodes do not establish independent failure domains. The driver profile sets local-DC routing but no explicit consistency level. Quorum reasoning is theory until a policy is configured and tested. Restore of counter and mappings requires coordinated planning; no recovery exercise was performed here.

The affine transform is obfuscation, not encryption, authorization or TLS. Changing key/alphabet breaks issued links without versioned decoding. Literal `0` padding and length/uniqueness-only alphabet validation leave a known custom-alphabet concern. Keep the default alphabet and stable key; this documentation finding is not a runtime fix. Public 301 responses may be cached, constraining future destination editing. `HttpUrl` validates syntax, not destination safety; the backend does not fetch targets. Basic Auth needs protected transport beyond loopback. Bootstrap superuser privileges, abuse controls and public TLS remain production gaps.

## Interview rehearsal

**Introductory — Why can redirects survive Redis failure?** Resolution reads Cassandra after decoding the code; Redis only allocates creates. Follow-up: a cold application still needs startup dependencies, so operation-level independence does not prove cold-start availability.

**Intermediate — Is a lost ID a failed transaction?** There is no joint transaction. A gap is harmless if IDs remain unique; a lost HTTP response after Cassandra commit leaves an unknown outcome. Follow-up: a relational sequence and mapping in one database simplify coordination, while random codes need conditional collision handling.

**Challenging — Can RF=3 plus INCR prove safe disaster recovery?** No. Replication does not coordinate Redis history, guard Cassandra upserts or replace backups. Follow-up: specify consistency and recovery ordering, test counter loss and concurrent writers in isolated resources, and reject reused IDs before claiming recovery safety. These are proposed requirements, not implemented controls.

[API contract](../api/contracts.md), [identity analysis](../database/identity-and-consistency.md), [security](../security/identity-and-transport.md) and [test strategy](../testing/strategy.md) supply details. Existing fake tests cover HTTP, helpers and adapter calls; they do not establish live cluster partition/failover behavior. No application suite or cluster was executed in this review.

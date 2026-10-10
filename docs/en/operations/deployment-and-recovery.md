# Deployment and coordinated recovery

[English](deployment-and-recovery.md) | [Português brasileiro](../../pt-BR/operations/deployment-and-recovery.md)

Static source review: 2026-10-10. Implemented facts, general theory and hypothetical changes are distinguished below. Runtime commands were not executed.

Lifespan creates Redis and Cassandra resources, ensures the table and exposes adapters on application state. Cassandra initialization occurs before serving; Redis counter initialization is lazy. `finally` closes Cassandra resources and Redis; failed Cassandra connection creation shuts down the cluster. The default Compose command is Uvicorn with reload, intended for local development. Three Cassandra nodes, Redis AOF storage and bind mounts are a learning topology, not a verified production HA release.

Update/rollback review must preserve database contents and the code-space contract. Never reset Redis independently of Cassandra mappings or assume recreating containers recreates credentials in initialized volumes. Back up and restore both stores coherently and retain obfuscation settings; volume persistence is not backup. These are procedure requirements, not a restore rehearsal performed here. No coordinated recovery tool, application release pipeline or measured RTO/RPO is present. There is no schema-versioned destination-edit lifecycle.

Fake tests isolate encoding, allocation, service ordering and HTTP error mapping without proving real cluster consistency, authentication or failover. Existing Docker/Postman instructions are unexecuted during this review. OpenAPI reachability proves HTTP startup, not dependency readiness at request time. Potential performance costs are synchronous network calls, Redis serialization, Cassandra replica/network work and client thread capacity; no throughput chart can be derived from topology. Remaining gaps include real failure injection, counter-loss recovery, concurrent load, quorum policy selection and deployment/rollback exercises.

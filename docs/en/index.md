# Documentation catalog: url-shortener

[Project introduction](../../README.md) | [Other language](../pt-BR/index.md)

Reading path: purpose/setup → architecture/contracts → security/failures → testing/evidence → operations. For the library, use catalog/dossier → project interview → foundations → failure follow-ups. Historical milestone/refactor/handoff records describe their original dates; current review/checklist explains present scope.

## architecture

Components, flows and implemented boundaries.

- [Architecture](architecture/overview.md)

## guides

Setup, prerequisites and reading procedures.

- [url-shortener](guides/project-guide.md)

## testing

Test strategy, inventories and dated evidence.

- [Project Tests](testing/strategy.md)
- [Documentation validation — 2026-10-06](testing/verification.md)

## docker

Local images, services, mounts and configuration.

- [Docker development setup and recovery](docker/development.md)
- [Docker Development](docker/runtime.md)

## database

Models, constraints, migrations and consistency.

- [Identity, mappings and consistency](database/identity-and-consistency.md)

## api

Exposed contracts and client behavior.

- [Creation and redirect contract](api/contracts.md)
- [Postman Collection](api/postman.md)

## operations

Diagnosis, recovery, review checklists and historical records.

- [url-shortener: Repository completion checklist](operations/completion-checklist.md)
- [Deployment and coordinated recovery](operations/deployment-and-recovery.md)

## security

Authentication, authorization, data and resource boundaries.

- [Authentication, obfuscation and transport](security/identity-and-transport.md)

Category applicability and omissions are justified in the [completion checklist](operations/completion-checklist.md). No empty category is created.

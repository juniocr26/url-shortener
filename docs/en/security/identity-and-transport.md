# Authentication, obfuscation and transport

[English](identity-and-transport.md) | [Português brasileiro](../../pt-BR/security/identity-and-transport.md)

Static source review: 2026-10-10. Implemented facts, general theory and hypothetical changes are distinguished below. Runtime commands were not executed.

HTTP Basic checks configured username and password using `secrets.compare_digest`. Invalid credentials return 401 with a Basic challenge; missing configuration returns 500. Basic credentials are an encoding, not transport encryption. The local application does not configure TLS termination. The public redirect route is intentionally unauthenticated, and possession of a short code is not an authorization check. CORS or a private Compose network would not substitute for API authentication.

The affine transformation is reversible obfuscation, even though SHA-256 derives its parameters. It is not authenticated encryption, a password hash or a secrecy boundary. Known input/output pairs and its algebraic structure make cryptographic-security claims inappropriate. Changing the key or alphabet changes decoding of existing links; there is no version prefix or migration lookup. A random stored code would avoid coupling decoding to one global key but require collision handling and another query key; authenticated encryption would introduce different length/key-management requirements. Neither is implemented.

Destination syntax is validated, but no allowlist or reputation check exists. The app redirects rather than fetching URLs, so its current creation path is not a server-side URL fetcher; a future preview/fetch feature would create new SSRF concerns. Avoid logging credentials or full sensitive destinations. Real environment files and datastore contents were not read. Security gaps include TLS deployment, abuse controls, credential rotation procedures and tested code/key migration.

# Threat model

Untrusted: model output, retrieved document text and exploratory SQL requests.
Trusted for this prototype: Python source, synthetic fixture generator, SQLite runtime and local operator.

| Risk | Enforced control | Remaining limit |
|---|---|---|
| SQL writes, attachment or extension loading | SQLite authorizer allows SELECT/READ and an explicit function set | Not a general untrusted-code sandbox |
| Expensive queries | VM instruction callback; 200 returned rows; query length cap | Bounds are approximate instruction limits, not a hard process memory cap |
| Endless agent loop | 1–40 configurable steps; default 12 | Inference call may take up to its timeout |
| Forged citations | Exact recorded evidence IDs required | References alone do not prove semantic entailment of prose |
| Unsupported pilot | Valid comparison plus positive-net cited scenario required | Assumed lift may still be unrealistic |
| Prompt injection | Documents marked untrusted; no write/network tools; runtime gates | Real-model resistance not evaluated |
| Network redirection | Fixed loopback model endpoint, proxies disabled | Local model server itself must be trusted |
| Source corruption | Duplicate/missing/schema checks fail closed | General source ingestion is not implemented |
| Unverified revenue claims | Structured scenario labels; no realized-impact field | Operators could misrepresent outputs outside the application |

No credentials, customer data, telemetry or external service integrations are bundled. The static replay executes no model and sends no requests. Do not expose the local inference service publicly without a separate security review.

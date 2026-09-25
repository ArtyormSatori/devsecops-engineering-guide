# Secure Code Review Checklist

For reviewers. Ordered by how often each category actually causes breaches, not by how interesting it is.

Scanners find *known patterns*. Reviewers find *missing logic*. Spend your attention on what the scanner cannot see: authorization decisions, trust boundaries, and design.

---

## Before you read a line of code

- [ ] What trust boundary does this change cross? (Internet → app, app → database, tenant → tenant, user → admin)
- [ ] Does it handle data from an untrusted source?
- [ ] Does it change authentication or authorization logic?
- [ ] Does it touch secrets, cryptography, or sessions?
- [ ] Does it add a new dependency, a new external call, or a new public endpoint?

If the answer to all five is no, this is a routine review.

---

## Access control — A01:2025, the #1 cause of real breaches

- [ ] **Every** endpoint that returns or modifies data enforces authorization, not just authentication
- [ ] Object-level authorization: the code verifies *this user* may access *this specific record* — not just that they are logged in
- [ ] Authorization is enforced server-side; UI hiding is not a control
- [ ] IDs from user input are never trusted to imply ownership
- [ ] Multi-tenant queries are scoped by tenant at the data layer, not by hoping the caller passes the right filter
- [ ] Privilege escalation paths considered: can a user set their own role, org, or permission fields via mass assignment?
- [ ] New admin functionality is behind the same authorization checks as existing admin functionality
- [ ] Default is deny — a new route without an explicit policy should fail closed

## Input handling & injection — A05:2025

- [ ] All external input is validated against an **allow-list**, at the boundary
- [ ] SQL uses parameterized queries or a well-used ORM API — no string concatenation, including in `ORDER BY` and dynamic table names
- [ ] NoSQL queries do not interpolate user objects directly (operator injection)
- [ ] OS commands avoid shell invocation; arguments passed as arrays, never interpolated strings
- [ ] Template engines are not fed user input as templates (SSTI)
- [ ] Deserialization of untrusted data is avoided; if unavoidable, restricted to safe types
- [ ] File paths derived from input are canonicalised and confined to an intended directory
- [ ] File uploads: type verified by content, size limited, stored outside the web root, served with a safe content type
- [ ] XML parsers have external entity resolution disabled (XXE)
- [ ] Regexes on user input cannot backtrack catastrophically (ReDoS)

## SSRF — now folded into A01:2025

- [ ] Outbound requests to user-supplied URLs are blocked, or restricted to an allow-list of hosts
- [ ] Redirects are not followed to unvalidated destinations
- [ ] Link-local and private ranges are blocked (`169.254.169.254`, `127.0.0.0/8`, `10/8`, `172.16/12`, `192.168/16`, `::1`, `fd00::/8`)
- [ ] DNS rebinding considered — resolve once, then connect to the resolved IP

## Output & rendering

- [ ] Output encoding is context-appropriate (HTML body, attribute, JavaScript, URL, CSS)
- [ ] Framework auto-escaping is not disabled (`dangerouslySetInnerHTML`, `|safe`, `v-html`, `Html.Raw`)
- [ ] User-controlled HTML is sanitised with a maintained library, not a regex
- [ ] Content-Security-Policy is set and not weakened by `unsafe-inline`/`unsafe-eval`
- [ ] Errors returned to users contain no stack traces, SQL, internal paths, or version strings

## Authentication & session — A07:2025

- [ ] Passwords hashed with Argon2id / scrypt / bcrypt — never SHA-256, never unsalted
- [ ] No credentials, tokens, or session IDs in URLs or logs
- [ ] Session tokens are regenerated on privilege change and invalidated on logout
- [ ] Cookies: `HttpOnly`, `Secure`, `SameSite`, appropriate scope and expiry
- [ ] JWT: algorithm is pinned server-side (`alg: none` and confusion attacks rejected), signature verified, `exp`/`aud`/`iss` validated, revocation strategy exists
- [ ] Rate limiting and lockout on authentication and password reset
- [ ] Password reset tokens are single-use, short-lived, and cryptographically random
- [ ] MFA cannot be bypassed by an alternate flow (API, legacy endpoint, remember-me)
- [ ] Timing-safe comparison for secrets and tokens

## Cryptography — A04:2025

- [ ] No custom cryptography
- [ ] Randomness from a CSPRNG (`secrets`, `crypto.randomBytes`, `SecureRandom`) — never `Math.random`/`rand()`
- [ ] AES-GCM or ChaCha20-Poly1305 for symmetric encryption; never ECB; IV/nonce never reused
- [ ] TLS certificate verification is never disabled ("just for dev" ships to prod)
- [ ] Keys come from a key management service, not from source or config files
- [ ] Deprecated algorithms absent: MD5, SHA-1, DES, RC4, RSA PKCS#1v1.5 encryption

## Secrets

- [ ] No credentials, API keys, private keys, or connection strings in the diff — including in tests, fixtures, comments, and example files
- [ ] Secrets are read from a secret manager or injected environment, not committed config
- [ ] Nothing sensitive is written to logs (tokens, PII, full request bodies, authorization headers)
- [ ] Debug/verbose logging cannot be enabled in production by an untrusted input

## Dependencies & supply chain — A03:2025

- [ ] New dependencies are justified — is a 3-line utility worth a new transitive tree?
- [ ] The package is maintained, widely used, and the name is not a typosquat of what was intended
- [ ] Lockfile updated; versions pinned
- [ ] No install-time scripts from an unfamiliar package
- [ ] License is compatible

## Error handling — A10:2025 (new)

- [ ] Failure paths **fail closed** — an exception in an authorization check must deny, not allow
- [ ] Exceptions are not swallowed silently
- [ ] Resources are released on the error path (no leaked locks, transactions, file handles)
- [ ] Partial failures leave consistent state (transactions, idempotency)
- [ ] Timeouts and retries are bounded; retries cannot amplify load into a self-inflicted DoS

## Logging & detection — A09:2025

- [ ] Security-relevant events are logged: authn success/failure, authz denial, privilege change, data export, config change
- [ ] Logs carry enough context to investigate (who, what, when, from where, correlation ID)
- [ ] Log injection prevented (newlines in user input do not forge log entries)

## Business logic

- [ ] Race conditions considered — can two concurrent requests double-spend, double-redeem, or double-provision?
- [ ] Numeric limits enforced server-side (quantity, price, discount, negative values)
- [ ] Workflow steps cannot be skipped or reordered by calling endpoints directly
- [ ] Rate limits exist on anything expensive or abusable

## Tests

- [ ] Security-relevant behaviour has tests, especially the **negative** cases (unauthorized access is denied)
- [ ] Each fixed vulnerability gets a regression test
- [ ] Tests do not disable security controls to pass

---

## Review anti-patterns

| Anti-pattern | Do instead |
|---|---|
| "LGTM" on a 2,000-line diff | Ask for it to be split; you cannot review what you cannot hold in your head |
| Only reading the added lines | Read the surrounding function — deleted checks are invisible in a green diff |
| Trusting the scanner's silence | Scanners cannot see authorization or business logic |
| Nitpicking style in a security review | Separate the concerns; style comments dilute the security signal |
| Approving "it's behind the VPN" | Assume the attacker is already inside |

## Further reading

- [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)
- [OWASP ASVS 5.0](https://asvs.dev/) — turn these into acceptance criteria
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security) — see each of these exploited

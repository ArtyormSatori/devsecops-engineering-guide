# Secrets Management & Workload Identity Checklist

**The goal is not "secrets stored safely". It is no long-lived secrets at all.**

Storing a static credential well is a mitigation. Removing the need for it is a fix. This checklist is ordered so that the top of it makes the rest of it smaller: every secret you eliminate is a secret you never have to scan for, rotate, audit, or clean out of Git history.

Work out which rung you are on before you start:

| Level | State | Reality |
|---|---|---|
| 0 | Secrets in code / committed `.env` | Compromised; you just do not know yet |
| 1 | Secrets in CI variables | Long-lived, broadly readable, rarely rotated |
| 2 | Central secret manager | Auditable, rotatable, access-controlled |
| 3 | Dynamic, short-lived secrets | Generated on demand, expire in minutes |
| 4 | **Workload identity — no secret exists** | The identity *is* the credential |

Most teams try to jump from 1 to 4 for everything at once and stall. Move one credential class at a time, starting with the one with the largest blast radius — which is almost always your cloud deploy key.

---

## 1. Eliminate before you protect

- [ ] CI/CD authenticates to cloud providers via **OIDC federation**, not static access keys ([`examples/terraform-oidc/`](../examples/terraform-oidc/))
- [ ] Every remaining static cloud key in CI has a ticket to remove it, with an owner and a date
- [ ] Database credentials are **generated dynamically** with a short lease (Vault/OpenBao dynamic secrets) rather than shared and static
- [ ] Cloud service-to-service auth uses the platform identity (IAM roles for service accounts, managed identities, Workload Identity Federation) — not a key file
- [ ] Service-to-service auth inside the cluster uses **SPIFFE/SPIRE or mTLS identities**, not a shared bearer token in an environment variable
- [ ] Human access to production is via SSO with short-lived sessions, not a shared credential in a password manager
- [ ] Third-party integrations use scoped, revocable tokens with an expiry — and someone owns each one
- [ ] A written answer exists for every remaining long-lived secret: *why can this not be short-lived?*

> The single highest-value change in this document is replacing static cloud keys in CI with OIDC. It removes the most valuable, most widely readable, longest-lived secret you own, and it is usually a day of work.

## 2. Know what you have

- [ ] An inventory exists of every secret: what it is, where it lives, who can read it, what it grants, when it was last rotated
- [ ] Each secret has a named owner — not a team alias nobody reads
- [ ] Secrets are classified by blast radius, and the top ten are known by name
- [ ] Orphaned credentials are found and revoked on a schedule (unused IAM keys, expired integrations, ex-employee tokens)
- [ ] Cloud provider "unused credential" reports are actually reviewed
- [ ] Every secret has an expiry, even if the expiry is enforced by a calendar reminder

## 3. Detection

*Assume something has already leaked. Detection is how you find out from your tooling rather than from an attacker.*

- [ ] Secret scanning runs **pre-commit** — cheapest possible place to catch it ([`examples/pre-commit/`](../examples/pre-commit/.pre-commit-config.yaml))
- [ ] Secret scanning runs in **CI on every PR**, and blocks
- [ ] **Full Git history** has been scanned at least once — the current tree being clean means nothing
- [ ] Platform push protection is enabled (GitHub Secret Scanning + Push Protection, GitLab equivalent) — it blocks the push before the secret exists
- [ ] A verifying scanner is used somewhere in the chain (TruffleHog) so triage is about live credentials, not entropy noise
- [ ] Container images, build logs, and artifacts are scanned — secrets leak into layers and log output constantly
- [ ] IaC state files, Helm values, and Kubernetes manifests are in scope
- [ ] Custom detectors exist for **your** internal credential formats — generic rules do not know what your tokens look like
- [ ] Public paste sites and public repos are monitored for your identifiable token prefixes
- [ ] Findings route to a human with an SLA, not to a dashboard nobody opens

## 4. Storage and access

- [ ] A central secret manager is the single source of truth (Vault/OpenBao, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager)
- [ ] Access is **per-workload and per-environment**, not one policy granting the whole tree
- [ ] Production secrets are not readable from non-production environments, and not readable by developers by default
- [ ] Break-glass access exists, is time-boxed, alerts on use, and is reviewed afterwards
- [ ] Encryption at rest uses a KMS key with its own access policy and audit trail
- [ ] Every secret read is **logged with the identity that read it**, and the logs are queryable
- [ ] Alerts fire on anomalous access: bulk reads, reads from a new identity, reads outside deployment windows
- [ ] Secrets are versioned, so rotation can roll back
- [ ] For GitOps, secrets are encrypted in the repo with SOPS+age or delivered by External Secrets Operator — **never base64 in a manifest, which is encoding, not encryption**

## 5. Runtime handling

- [ ] Secrets are injected as **mounted files or fetched at startup**, not baked into images
- [ ] Environment variables are understood as a weaker option: they leak into `/proc`, crash dumps, child processes, and debug endpoints — acceptable for low-value secrets, not for the crown jewels
- [ ] Secrets never appear in command-line arguments (`ps` shows them to every user on the host)
- [ ] Logging redacts known secret patterns, and the redaction is tested
- [ ] Error pages, stack traces, and debug endpoints do not echo configuration
- [ ] Secrets are not written to temporary files that outlive the process
- [ ] Application memory handling is considered for the highest-value secrets (zeroing, no swap)
- [ ] Kubernetes: `Secret` objects are encrypted at rest with a KMS provider (etcd encryption is **not** on by default), RBAC restricts `get`/`list` on secrets, and service account tokens are projected with a short audience-scoped TTL
- [ ] `automountServiceAccountToken: false` where the workload does not call the API server

## 6. Rotation

- [ ] Rotation is **automated** — a documented manual procedure that requires a person will not happen
- [ ] Rotation is tested regularly rather than first attempted during an incident
- [ ] Applications reload credentials without a restart, or the restart is part of the automated flow
- [ ] Overlapping validity windows exist so rotation is not an outage
- [ ] Maximum credential lifetime is defined per class, and enforced by tooling rather than policy documents
- [ ] Revocation is possible immediately and independently of expiry
- [ ] Rotation on personnel change is part of the offboarding checklist

## 7. CI/CD specifics

*Your pipeline holds the credentials for everything it deploys to. It is the most valuable secret store in the company and it is usually the least protected one.*

- [ ] Secrets are scoped to the **job that needs them**, not available to every job in the workflow
- [ ] Fork pull requests cannot access secrets — and `pull_request_target` with a checkout of untrusted code is treated as the credential-theft primitive it is
- [ ] Third-party actions are pinned to full commit SHAs — an unpinned action can read every secret in the job ([`examples/renovate/`](../examples/renovate/renovate.json5) keeps the pins fresh)
- [ ] `permissions:` is declared explicitly per job, defaulting to `contents: read`
- [ ] Secret masking in logs is enabled — and known to be defeatable by base64/chunked printing, so it is not relied upon
- [ ] Self-hosted runners for public repos are ephemeral, isolated, and never reuse a workspace
- [ ] Deployment credentials are per-environment, with production requiring a protected environment and approval
- [ ] Runner egress is restricted so an exfiltration attempt has somewhere to fail
- [ ] Nobody debugs a pipeline by `echo`-ing a secret; if they have, treat it as leaked

## 8. When a secret leaks

**Order matters. Rotate first, then investigate, then clean history.** Rewriting Git history first feels productive and leaves the credential valid — the attacker already has it, and now you have destroyed the timeline.

- [ ] **Rotate or revoke immediately** — before you finish reading the alert
- [ ] Confirm the old credential is dead by trying to use it
- [ ] Determine exposure window: when was it committed, when was it published, who could reach it
- [ ] Review provider audit logs **for the full exposure window** for use of that credential
- [ ] Assume compromise if the repository was ever public, or if the secret reached a third-party log, CI artifact, or paste site
- [ ] Check for persistence created *with* the credential: new IAM users, new access keys, new OAuth grants, new deploy keys, modified trust policies
- [ ] Only then clean history (`git filter-repo`, BFG), and remember forks, clones, mirrors, and the platform's cached views may retain it
- [ ] Record the incident and fix the class: what control would have stopped this reaching a commit?
- [ ] If the secret is in a published artifact or image, pull the artifact and publish a fixed version

> "It was only in a private repo" is not a mitigation. Private repos are read by every CI job, every integration, every contractor, and every compromised laptop with a clone.

## 9. Anti-patterns worth naming

- [ ] No `.env` files committed — and `.gitignore` alone is not the control, scanning is
- [ ] No secrets in `Dockerfile` `ENV`/`ARG` (build args are visible in image history and in the build cache)
- [ ] No secrets in Kubernetes ConfigMaps
- [ ] No secrets in Terraform variables committed to source, and state files treated as secret material (they contain plaintext values)
- [ ] No shared team credentials where individual identities are possible
- [ ] No "temporary" credentials with no expiry — they are permanent
- [ ] No secrets in issue trackers, chat, wikis, or screenshots
- [ ] No custom encryption of secrets in place of a secret manager

---

## What to do first

If this is a greenfield programme, the order that gives the most risk reduction per unit of effort:

| # | Do this | Effort | Why first |
|---|---|---|---|
| 1 | Push protection + pre-commit scanning | Hours | Stops the bleeding before you clean the wound |
| 2 | Scan full history, rotate what you find | Days | You will find something; assume it is live |
| 3 | Replace CI static cloud keys with OIDC | Days | Largest blast radius, and it is a one-off change |
| 4 | Central secret manager for what remains | Weeks | Auditability and rotation become possible |
| 5 | Dynamic database credentials | Weeks | Removes the next-largest class |
| 6 | Workload identity for service-to-service | Weeks | The end state; needs the platform work above |

---

## Where this fits

- Section 14 of the [roadmap](../README.md#14-secrets-management--workload-identity) has the learning resources
- CI-specific controls: [pipeline-security.md](pipeline-security.md)
- What to do in the first fifteen minutes: [incident-response.md](incident-response.md)
- Agent and MCP credentials: [ai-llm-security.md](ai-llm-security.md)
- Working OIDC example: [`examples/terraform-oidc/`](../examples/terraform-oidc/)

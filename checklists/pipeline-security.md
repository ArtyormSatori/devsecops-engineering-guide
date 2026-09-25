# CI/CD Pipeline Security Checklist

Your CI system can read every repository, holds every production credential, and executes arbitrary code submitted by strangers. Treat it as production infrastructure.

Mapped to the [OWASP Top 10 CI/CD Security Risks](https://owasp.org/www-project-top-10-ci-cd-security-risks/).

---

## Source control (CICD-SEC-1, CICD-SEC-2)

- [ ] Default branch is protected: no force-push, no deletion
- [ ] Pull requests require at least one review from someone other than the author
- [ ] `CODEOWNERS` covers `.github/`, `Dockerfile`, IaC directories, and dependency manifests
- [ ] Required status checks include the security gates (they cannot be bypassed silently)
- [ ] Stale approvals are dismissed when new commits are pushed
- [ ] Commit signing is required, or at least enforced on release branches
- [ ] Repository admin rights are limited and reviewed quarterly
- [ ] Organisation requires 2FA (hardware keys preferred) for all members
- [ ] Outside collaborators and bot accounts are inventoried, with owners
- [ ] Personal access tokens are fine-grained, expiring, and inventoried

## Pipeline definition (CICD-SEC-4, CICD-SEC-7)

- [ ] Workflow files are protected by CODEOWNERS — changing a pipeline requires security review
- [ ] **No `pull_request_target` (or GitLab equivalent) that checks out untrusted code**
- [ ] Untrusted input (`github.event.*`, branch names, PR titles) is never interpolated directly into `run:` blocks — it is passed via `env:` and quoted
- [ ] Workflows from forks require approval before running
- [ ] Pipeline behaviour is not configurable from within the PR being tested (no `.ci-config` read from the untrusted branch)
- [ ] Build scripts are in-repo and reviewed, not fetched at runtime (`curl | bash` is banned; if unavoidable, verify a pinned checksum)

## Third-party actions & plugins (CICD-SEC-3, CICD-SEC-8)

- [ ] **All third-party actions are pinned to a full 40-character commit SHA**, never a tag or branch
- [ ] A comment records the human-readable version next to each pin
- [ ] An org-level allow-list restricts which actions may run
- [ ] Actions are updated via Renovate/Dependabot with SHA pinning enabled and a cooldown window
- [ ] Jenkins/GitLab plugins are inventoried, minimal, and patched
- [ ] Third-party SaaS integrations with repo access are reviewed and least-privileged

> The `tj-actions/changed-files` compromise (CVE-2025-30066, March 2025) rewrote *existing tags* to point at malicious code across ~23,000 repositories. SHA-pinned consumers were unaffected. This single control is the highest-value item on this list.

## Credentials & identity (CICD-SEC-6)

- [ ] **No long-lived cloud credentials in CI** — use OIDC federation
- [ ] `permissions:` is declared explicitly at workflow level, defaulting to `contents: read`
- [ ] Elevated permissions are granted per-job, not per-workflow
- [ ] Secrets are scoped to environments, not organisation-wide
- [ ] Production deploy credentials are unavailable to build jobs
- [ ] Secrets are never passed as command-line arguments (they appear in process listings)
- [ ] Secret masking is enabled and verified; log output is spot-checked
- [ ] Rotation schedule exists and has actually been exercised
- [ ] Forks cannot access secrets

## Runners (CICD-SEC-5, CICD-SEC-7)

- [ ] Self-hosted runners are ephemeral (destroyed after each job)
- [ ] Self-hosted runners are **never** attached to public repositories
- [ ] Runners are network-segmented; egress is restricted to known destinations
- [ ] Runner egress monitoring is enabled (e.g. Harden-Runner) — exfiltration needs a network path
- [ ] Runners do not have standing cloud IAM roles beyond what the job needs
- [ ] Runner images are patched and rebuilt on a schedule
- [ ] Docker socket is not mounted into build containers

## Build integrity (CICD-SEC-9)

- [ ] Dependencies are resolved from a lockfile with integrity hashes
- [ ] Internal package names are scoped/namespaced (prevents dependency confusion)
- [ ] Registry precedence is configured so internal names never resolve publicly
- [ ] Builds are hermetic — no network access at build time where achievable
- [ ] SBOM is generated at build time from the build system
- [ ] Artifacts are signed (cosign / GitHub Artifact Attestations)
- [ ] SLSA provenance is generated and stored
- [ ] Signatures and provenance are **verified at deploy/admission time**, not just produced
- [ ] Caches are keyed so untrusted branches cannot poison trusted caches

## Security gates

- [ ] Secret scanning runs pre-commit, on PRs, and over full history
- [ ] SAST runs on PRs, diff-aware, completing in under 10 minutes
- [ ] SCA runs on PRs and nightly against the full dependency tree
- [ ] IaC scanning runs on the plan output, not just source
- [ ] Container images are scanned before push and continuously in the registry
- [ ] Workflow files are audited (`zizmor`, `poutine`, `actionlint`)
- [ ] Gates fail on **new** findings and warn on the pre-existing backlog
- [ ] There is a documented, logged, time-limited bypass procedure
- [ ] Findings are uploaded as SARIF to a single aggregation point

## Logging & visibility (CICD-SEC-10)

- [ ] CI/CD audit logs are shipped off-platform and retained
- [ ] Logs are append-only and cannot be deleted by pipeline identities
- [ ] Alerts exist for: new workflow file, secret access anomaly, self-hosted runner registration, permission escalation in a workflow
- [ ] Deployments are traceable from artifact digest back to commit and reviewer

---

## Quick audit commands

```bash
# Find unpinned third-party actions across a repo
grep -rn "uses:" .github/workflows/ | grep -vE "uses: \./" | grep -vE "@[0-9a-f]{40}"

# Audit workflows for known-dangerous patterns
pipx run zizmor .github/workflows/
docker run --rm -v "$PWD":/src ghcr.io/boostsecurityio/poutine analyze_local /src

# Lint workflow syntax and expressions
actionlint

# Pin everything currently unpinned
pinact run .github/workflows/*.yml
```

## Further reading

- [OWASP Top 10 CI/CD Security Risks](https://owasp.org/www-project-top-10-ci-cd-security-risks/)
- [GitHub: Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [CISA/NSA: Defending CI/CD Environments](https://www.cisa.gov/resources-tools/resources/defending-continuous-integrationcontinuous-delivery-cicd-environments)
- [SLSA specification](https://slsa.dev/spec/)

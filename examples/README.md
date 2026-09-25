# Examples

Working, commented configurations you can adapt. Every file explains *why* each control is there, not just what it does — the reasoning is the part that transfers.

| Path | What it is |
|---|---|
| [`github-actions/devsecops-pipeline.yml`](github-actions/devsecops-pipeline.yml) | Full GitHub Actions pipeline: parallel PR gates → build → SBOM → sign → attest → **verify** |
| [`gitlab-ci/.gitlab-ci.yml`](gitlab-ci/.gitlab-ci.yml) | The same pipeline for GitLab CI, using ID tokens and Kaniko (no privileged runner) |
| [`pre-commit/.pre-commit-config.yaml`](pre-commit/.pre-commit-config.yaml) | Fast local hooks — secrets, SAST, IaC, Dockerfile, shell, workflow lint |
| [`kyverno/baseline-policies.yaml`](kyverno/baseline-policies.yaml) | Kubernetes admission policies, including cosign signature verification and generated default-deny NetworkPolicies |
| [`opa/terraform.rego`](opa/terraform.rego) | Rego policies evaluated against a **Terraform plan**, not source |
| [`trivy/trivy.yaml`](trivy/trivy.yaml) | Shared Trivy configuration with a documented ignore policy |
| [`docker/`](docker/) | A deliberately bad Dockerfile and its hardened counterpart — the before/after for lab 2.2 and project P2 |
| [`semgrep/`](semgrep/) | 11 custom SAST rules **with passing tests**, including the tenant-scoping rules no registry can write for you |
| [`falco/custom-rules.yaml`](falco/custom-rules.yaml) | 8 runtime detection rules mapped to MITRE ATT&CK, each documenting its own false positive mode |
| [`renovate/renovate.json5`](renovate/renovate.json5) | Keeps SHA pins current with a cooldown, so pinning does not quietly become "running last year's dependencies" |
| [`terraform-oidc/`](terraform-oidc/) | GitHub Actions → AWS with no static keys, handling the July 2026 immutable subject claim change |

---

## Before you copy anything

**1. Resolve your own action pins.**
The SHAs in the GitHub Actions example were real at the time of writing, but pins go stale. Resolve current ones, then let Renovate keep them fresh with [`renovate/renovate.json5`](renovate/renovate.json5) — pinning without automated updates trades one risk for another:

```bash
gh api repos/actions/checkout/commits/v4 --jq .sha
pinact run .github/workflows/*.yml     # pin everything automatically
```

**2. Start in audit mode.**
Kyverno policies ship with `validationFailureAction: Audit` where breaking a live cluster is likely. Look at the PolicyReports, fix or exclude what breaks, *then* switch to `Enforce`. A policy engine that blocks deploys on day one gets uninstalled on day two.

**3. Baseline before you gate.**
Run every scanner once, record the existing findings, and configure the gate to fail only on **new** ones. Otherwise your rollout blocks every build in the company.

```bash
detect-secrets scan > .secrets.baseline
semgrep scan --config=auto --baseline-commit=$(git rev-parse HEAD)
```

**4. Verify, do not just sign.**
The most commonly skipped step in the whole pipeline is the `verify` job. Producing signatures and attestations that nothing ever checks is compliance theatre. The value is entirely in the verification.

---

## Order to adopt these

If you are starting from nothing, this sequence gives the most risk reduction per unit of effort:

| # | Do this | Effort | Why first |
|---|---|---|---|
| 1 | Secret scanning (pre-commit + CI + full history) | Hours | Leaked credentials are the most-exploited entry point |
| 2 | [Pin all third-party actions to SHAs](renovate/renovate.json5) | Hours | Stops the `tj-actions` class of attack outright |
| 3 | Branch protection + CODEOWNERS on workflow files | Hours | Makes every later control non-bypassable |
| 4 | SCA on PRs | A day | Cheap, high signal, easy to act on |
| 5 | [Replace static cloud keys with OIDC](terraform-oidc/) | Days | Removes the highest-value secret you have |
| 6 | [SAST with a tuned ruleset](semgrep/) | Days | Needs tuning to avoid becoming noise |
| 7 | [Container scanning + minimal base images](docker/) | Days | One base image change fixes hundreds of findings |
| 8 | IaC scanning on the plan | Days | Misconfiguration is A02:2025 |
| 9 | Admission policies in audit mode | Weeks | Needs cluster-specific tuning |
| 10 | SBOM + signing + provenance | Weeks | High value, but only once the basics hold |
| 11 | Verification at admission | Weeks | The step that makes #10 real |
| 12 | [Runtime detection](falco/custom-rules.yaml) | Weeks | Requires someone to actually respond to alerts |

Do not start at 10. Signing artifacts while static AWS keys sit in CI variables is optimising the wrong end of the problem.

---

## These examples are tested

[`.github/workflows/validate-examples.yml`](../.github/workflows/validate-examples.yml) runs on every change here: the Semgrep rules against their test cases, `hadolint` against the hardened Dockerfile, `terraform validate` and `fmt` against the OIDC module, the Renovate config through its schema validator, and every YAML file through a parser.

That is not ceremony. An example that has quietly stopped working teaches the wrong thing to everyone who copies it — and the whole argument of this repo is that policies, rules, and pipelines are code, which means they rot exactly like code does.

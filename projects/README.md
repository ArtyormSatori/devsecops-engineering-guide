# Portfolio Projects

Labs prove you can follow instructions. **Projects prove you can build.**

Employers cannot verify what you have read. They can clone your repo. Every project below is scoped to be finishable, publicly shareable, and genuinely useful — several of them are things real teams pay for.

---

## How to pick

| If you want to… | Build |
|---|---|
| Get your first DevSecOps role | **P1**, **P2**, **P4** — the pipeline trio |
| Move from DevOps into security | **P4**, **P5**, **P8** |
| Move from security into DevSecOps | **P2**, **P3**, **P7** |
| Show senior-level judgement | **P9**, **P11**, **P12** |
| Stand out in a crowded applicant pool | **P6**, **P10**, **P13** |

**Do three well rather than eight badly.** A finished, documented, tested project beats five abandoned repos.

---

## What makes a project count

Every project below is only "done" when it has:

- [ ] A README explaining **the problem**, not just the usage
- [ ] The **reasoning** for each design decision (this is what gets read in an interview)
- [ ] Working CI that proves it runs
- [ ] Tests, or a documented reason there are none
- [ ] An honest "limitations / what this does not do" section

That last item is the strongest signal of engineering maturity you can send. Anyone can list features.

---

## Tier 1 — Foundational (2–3 weeks each)

### P1 · Hardened pipeline template
**Build:** a template repository with a complete DevSecOps pipeline — secret scanning, SAST, SCA, IaC scanning, container scanning, workflow auditing — that runs on a PR in under 10 minutes.

**Requirements**
- Every third-party action pinned to a full commit SHA
- `permissions:` declared explicitly, least privilege per job
- Findings uploaded as SARIF to one aggregation point
- Fails on **new** findings, reports the backlog without blocking
- A documented, logged bypass procedure

**Proves:** you can build the thing the job is actually about.
**Stretch:** publish it as a reusable workflow other repos can call.

---

### P2 · Container hardening case study
**Build:** take a realistically bad Dockerfile (`FROM node:latest`, root user, secrets in layers) and drive it to production-grade, documenting each step with measurements.

**Requirements**
- Before/after CVE counts from two independent scanners
- Image size comparison
- Multi-stage → distroless or Wolfi, non-root, read-only rootfs, dropped capabilities
- SBOM generated, image signed with cosign
- A table showing which change removed which vulnerabilities

**Proves:** you understand that base image choice beats scanner tuning.
**Why it works in interviews:** the numbers are concrete and you can explain every one.

---

### P3 · Custom Semgrep ruleset
**Build:** 5–10 Semgrep rules for a real anti-pattern class, with test cases.

**Ideas:** missing tenant scoping on ORM queries · unsafe deserialisation in your language · secrets passed as CLI args · authorization decorators missing on route handlers · `verify=False` on HTTP clients.

**Requirements**
- Each rule has passing and failing test cases (`semgrep --test`)
- Documented false positive rate against a real open-source codebase
- Rules run in CI on the ruleset repo itself

**Proves:** the highest-value SAST skill there is. Most people only run other people's rules.

---

## Tier 2 — Intermediate (3–5 weeks each)

### P4 · Full supply chain: build → sign → attest → verify
**Build:** an end-to-end supply chain security implementation for a small application.

**Requirements**
- CycloneDX SBOM generated at build time from the build system
- Keyless cosign signing via OIDC
- SLSA provenance attestation
- SBOM ingested into Dependency-Track
- **Kyverno policy in a kind cluster that rejects unsigned or unattested images**
- A demo showing an unsigned image being blocked

**Proves:** you understand A03:2025 in practice, not just in slides.
**This is the single most in-demand skill set in the list.**

---

### P5 · Cloud guardrails module
**Build:** a Terraform module implementing a secure-by-default landing zone.

**Requirements**
- SCPs / Org Policies preventing: disabling audit logs, public storage, unencrypted volumes, unapproved regions
- Centralised logging to a separate, restricted account
- OIDC provider for CI, with a tightly scoped deploy role and no static keys
- Before/after Prowler report showing the improvement
- Policies tested with Checkov + OPA in CI

**Proves:** prevention over detection — the distinction that separates senior from junior.

---

### P6 · SARIF aggregator / mini-ASPM
**Build:** a CLI tool that ingests output from three or more scanners, normalises to SARIF, deduplicates, and prioritises.

**Requirements**
- Ingests at least: Semgrep, Trivy, Gitleaks
- Deduplicates the same finding reported by multiple tools
- Enriches with EPSS score and CISA KEV status
- Ranks by KEV → EPSS → exposure → CVSS
- Outputs a triage-ready report and a machine-readable feed

**Proves:** you understand that the bottleneck is triage, not detection.
**Why it stands out:** it is a real engineering project, not a configuration exercise.

---

### P7 · Policy library with tests
**Build:** a versioned Kyverno + OPA policy library covering a baseline security posture.

**Requirements**
- 15+ policies covering workloads, images, network, and RBAC
- `kyverno test` and `conftest verify` coverage for every policy
- Audit → Enforce rollout documentation
- An exception mechanism with owners and expiry dates
- CI that tests policies against both compliant and non-compliant manifests

**Proves:** policy as code done properly, including the operational reality of exceptions.

---

### P8 · Detection engineering pack
**Build:** a set of Falco rules for attacks the defaults miss, with tests.

**Requirements**
- 5+ custom rules mapped to MITRE ATT&CK techniques
- Each validated against an Atomic Red Team test
- Documented false positive analysis from a real workload
- Tuning notes: what you excluded and why

**Proves:** detection engineering, which is rarer than scanner operation.

---

## Tier 3 — Advanced (5–8 weeks each)

### P9 · Paved road / secure service template
**Build:** an internal-developer-platform-style golden path — a service template where the secure choice is the default and the only path.

**Requirements**
- `cookiecutter`/`copier` template generating a service with: hardened Dockerfile, full pipeline, K8s manifests passing restricted PSS, default-deny NetworkPolicy, OIDC auth to cloud, structured security logging
- Threat model committed as code
- A single command from nothing to a deployed, secured service
- Documentation aimed at a developer who does not care about security

**Proves:** platform-engineering-aligned security — how DevSecOps actually scales.
**This is what a staff-level DevSecOps engineer does.**

---

### P10 · Vulnerability management system
**Build:** a working risk-based vulnerability management pipeline.

**Requirements**
- Continuous SBOM ingestion, re-evaluated against new advisories
- Prioritisation combining EPSS, KEV, reachability, and internet exposure
- SLA tracking with MTTR measurement per severity
- VEX generation for not-affected findings
- A dashboard showing backlog trend and age distribution, not just totals

**Proves:** you can run a programme, not just a scanner.

---

### P11 · Threat model as code + control mapping
**Build:** a STRIDE threat model for a non-trivial system, expressed as code, with each threat mapped to an implemented control.

**Requirements**
- `pytm` or `threagile` model, versioned in Git, diagrams generated in CI
- Data flow diagram with explicit trust boundaries
- Each threat mapped to: a control, the test proving it, and the residual risk
- Threats that you have deliberately accepted, with the reasoning

**Proves:** design-level security thinking — the part no scanner can do, and the part A06:2025 is about.

---

### P12 · Compliance as code
**Build:** automated evidence collection for a control framework.

**Requirements**
- 15+ CIS Controls or NIST SSDF practices mapped to automated checks
- Checks run on a schedule and emit machine-readable evidence
- Evidence sourced from pipelines you already run (SBOMs, attestations, policy results)
- A generated report an auditor could actually read
- OSCAL output if you want to go further

**Proves:** you can make compliance cheap, which is what makes security teams welcome.

---

### P13 · AI/agentic security assessment
**Build:** a security assessment of an LLM application, with mitigations implemented.

**Requirements**
- A small RAG or agentic app you build yourself
- Threat model against the OWASP LLM Top 10 and Agentic Top 10
- `garak` and/or PyRIT results
- Demonstrated attacks: indirect prompt injection, tenant isolation bypass in the vector store, excessive agency via a tool
- **Mitigations implemented**, showing which attacks still succeed afterwards and why

**Proves:** currency in the fastest-moving area of the field.
**Be honest about what you could not fix** — prompt injection has no complete solution, and saying so is the correct answer.

---

## Presenting your work

**Repository README structure that works:**

```markdown
# Project name
One sentence: what problem this solves.

## The problem
Two paragraphs. Include a real incident if one motivates it.

## What this does
Bullets. Concrete.

## How it works
Architecture diagram. Explain the key decisions.

## Design decisions
| Decision | Alternative considered | Why |
The section interviewers actually read.

## Limitations
What this does not do. What would break at scale.
The strongest maturity signal in the whole README.

## Running it
Copy-pasteable. Test it on a clean machine.
```

**Also:**
- Pin 3–6 repos on your GitHub profile — the rest is noise
- Write a short post per project; link it from the README
- Record a 3-minute demo for the visual ones (P2, P4, P9 especially)
- Put the numbers in: "reduced image CVEs from 214 to 3" beats "hardened the image"

---

## Anti-patterns

| Don't | Do |
|---|---|
| Eight half-finished repos | Three finished, documented ones |
| A README that is only `npm install` | A README that explains the *problem* |
| Copying a tutorial verbatim | Change something, break it, explain what you learned |
| "Enterprise-grade", "military-grade" | Say what it actually does |
| Hiding the limitations | Lead with them — it reads as confidence, not weakness |
| Committing your `.env` to demonstrate secret scanning | Please no. Yes, this happens. |

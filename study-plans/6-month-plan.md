# 6-Month Intensive Plan

**For:** engineers who already have a DevOps, platform, SRE, or backend development background.
**Assumes:** comfortable with Linux, Git, and at least one programming language; has shipped software to production.
**Time:** ~15 hours/week (2 hrs on weeknights, 5 hrs at the weekend).
**Outcome:** employable as a DevSecOps engineer, with a portfolio to prove it.

If you are starting from a standing start, use the [12-month plan](12-month-plan.md) instead.

---

## How this plan works

Each month has **one theme**, **one deliverable**, and a small number of resources. The deliverable is the point — it is what you show people.

Three rules:

1. **Ship the deliverable even if it is ugly.** A working, imperfect pipeline beats a perfect plan.
2. **Write up what you learn.** A short post per month. Writing is how you find out what you do not actually understand.
3. **If you fall behind, cut resources, not deliverables.**

---

## Month 1 — Security foundations & AppSec

**Theme:** learn to think like an attacker before you try to defend anything.

| Week | Focus |
|---|---|
| 1 | Security fundamentals: CIA, AAA, risk, AuthN vs AuthZ, OAuth 2.0/OIDC, JWT pitfalls. Read the [OWASP Top 10:2025](https://owasp.org/Top10/2025/) properly, not the summary. |
| 2 | PortSwigger Academy: **Access control** and **Authentication** paths. All labs, no hints on the first attempt. |
| 3 | PortSwigger Academy: **SQL injection**, **XSS**, **SSRF**. Note that SSRF is now part of A01. |
| 4 | OWASP Juice Shop end to end. Skim [ASVS 5.0](https://asvs.dev/) and pick 20 requirements relevant to a service you know. |

**Deliverable:** a written walkthrough of five Juice Shop flaws — the attack, the root cause, the fix, and the *class* of issue each belongs to.

**Also:** set up [pre-commit](../examples/pre-commit/.pre-commit-config.yaml) on a personal repo. Ten minutes, permanent benefit.

---

## Month 2 — Containers & Kubernetes security

**Theme:** the substrate everything else runs on.

| Week | Focus |
|---|---|
| 1 | Container internals: namespaces, cgroups, capabilities, seccomp. Read Liz Rice's *Container Security* ch. 1–5. Not optional — everything later depends on this. |
| 2 | Image hardening: multi-stage, distroless, non-root, digests. Trivy, Syft, Hadolint, Dockle. |
| 3 | Kubernetes security: RBAC, Pod Security Standards, securityContext, NetworkPolicy. |
| 4 | [Kubernetes Goat](https://madhuakula.com/kubernetes-goat/) — all scenarios. Then Kyverno admission policies to block each attack. |

**Deliverable:** a hardened container image (CVE count before/after documented) and a kind cluster where the Kubernetes Goat workloads **fail to deploy**, with the policy that blocks each one.

---

## Month 3 — CI/CD security & the supply chain

**Theme:** the highest-leverage month. This is what employers are actually short of.

| Week | Focus |
|---|---|
| 1 | Build a real pipeline: SAST, SCA, secret scanning, IaC scanning, container scanning. Get it under 10 minutes. |
| 2 | [OWASP Top 10 CI/CD Risks](https://owasp.org/www-project-top-10-ci-cd-security-risks/). Read the `tj-actions` post-mortems. Audit your workflows with `zizmor` and `poutine`. Pin everything. |
| 3 | Supply chain: SBOM (Syft/CycloneDX), signing (cosign keyless), SLSA provenance. Stand up Dependency-Track. |
| 4 | [CICD-Goat](https://github.com/cider-security-research/cicd-goat) and [GitHub Actions Goat](https://github.com/step-security/github-actions-goat). Then: **verify** signatures at admission with Kyverno. |

**Deliverable:** a public template repository — full pipeline, signed and attested artifacts, verification enforced at admission, README explaining every control and why it is there.

> This deliverable alone gets interviews. Make it good, and make the reasoning visible.

---

## Month 4 — Cloud security

**Theme:** identity is the perimeter.

| Week | Focus |
|---|---|
| 1 | Pick one cloud. IAM deeply: policies, roles, trust relationships, SCPs/Org Policies, permission boundaries. |
| 2 | [flaws.cloud](http://flaws.cloud/) and [flaws2.cloud](http://flaws2.cloud/), both tracks. |
| 3 | [CloudGoat](https://github.com/RhinoSecurityLabs/cloudgoat) + [IAM Vulnerable](https://github.com/BishopFox/iam-vulnerable). Throwaway account, billing limit, destroy afterwards. |
| 4 | Prowler against a personal account. Fix the top findings, then codify them as SCPs so they cannot recur. Replace every static CI key with OIDC federation. |

**Deliverable:** a Terraform landing-zone module with guardrails baked in, plus a before/after Prowler report.

---

## Month 5 — IaC, policy, secrets & runtime

**Theme:** enforcement and detection.

| Week | Focus |
|---|---|
| 1 | IaC security: [TerraGoat](https://github.com/bridgecrewio/terragoat), Checkov, scanning the **plan** rather than source. |
| 2 | Policy as code: OPA/Rego fundamentals, Conftest, and a Kyverno policy library with `kyverno test` coverage. |
| 3 | Secrets: Vault or OpenBao — dynamic secrets, transit engine, auth methods. External Secrets Operator. SPIFFE/SPIRE concepts. |
| 4 | Runtime: deploy Falco, run [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) techniques, write a custom rule for something the defaults miss. |

**Deliverable:** a policy library (OPA + Kyverno) with tests running in CI, and a Falco rule you wrote yourself with the detection logic explained.

---

## Month 6 — AI security, governance & consolidation

**Theme:** the parts that make you senior rather than merely capable.

| Week | Focus |
|---|---|
| 1 | AI/LLM security: [OWASP LLM Top 10](https://genai.owasp.org/llm-top-10/), Agentic Top 10, prompt injection, model supply chain. Run `garak` against an endpoint you control. |
| 2 | Vulnerability management: CVSS 4.0, EPSS, KEV, VEX, reachability. Build a triage script that ranks findings properly. |
| 3 | Governance: NIST SSDF, CIS Controls, EU CRA timeline. Threat model one of your own systems with STRIDE, committed as code. |
| 4 | Consolidate: polish the portfolio, write the capstone post, prepare interview answers, book CKS if that is your path. |

**Deliverable:** a capstone write-up tying all six months together — the pipeline you built, the attacks it prevents, the ones it does not, and what you would do next with more time.

---

## Weekly rhythm

| When | What | Time |
|---|---|---|
| Mon–Thu evenings | Focused study on the week's topic | 2 hrs × 4 |
| Saturday | Hands-on lab / building the deliverable | 4 hrs |
| Sunday | Write-up, review, plan the week | 1–2 hrs |
| Anytime | [tl;dr sec](https://tldrsec.com/) + [CloudSecList](https://cloudseclist.com/) | 20 min/week |

---

## Checkpoints — be honest with yourself

**End of month 2:** Can you explain to a developer, without notes, why their container running as root is a problem and exactly what an attacker would do with it?

**End of month 3:** Can you build a signed, attested, verified pipeline from an empty repository in under two hours?

**End of month 4:** Can you find three IAM privilege escalation paths in an account you have never seen before?

**End of month 6:** Can you walk into a team with no security tooling and say what to do first, second, and third — and defend that ordering?

If a checkpoint fails, spend an extra fortnight there. The plan is a guide, not a deadline.

---

## What to skip if you fall behind

In priority order, the things you can drop without much damage:

1. Fuzzing (specialist, rarely a DevSecOps engineer's day job)
2. IAST (mostly commercial, hard to practise)
3. Depth in a *second* cloud (breadth here is low value)
4. Formal compliance frameworks (learn these on the job, in context)

**Never skip:** access control, supply chain, secrets, and CI/CD hardening. Those four are the job.

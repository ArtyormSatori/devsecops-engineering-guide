# Hands-On Lab Sheet

A trackable list of every lab worth doing, with time estimates and cost. **Copy this file, tick the boxes as you go, and keep the notes column honest.**

The `Proves` column is what you can legitimately claim in an interview after finishing it.

Legend: **Diff** = difficulty (1 easiest → 5 hardest) · **Cost** — `free`, or an estimate · **Time** = realistic focused hours

---

## Progress tracker

| Level | Labs | Done |
|---|---|---|
| 1 · Foundations | 6 | ☐☐☐☐☐☐ |
| 2 · AppSec | 7 | ☐☐☐☐☐☐☐ |
| 3 · Containers & K8s | 7 | ☐☐☐☐☐☐☐ |
| 4 · Cloud | 7 | ☐☐☐☐☐☐☐ |
| 5 · Pipelines & supply chain | 6 | ☐☐☐☐☐☐ |
| 6 · IaC, runtime & AI | 7 | ☐☐☐☐☐☐☐ |

---

## Level 1 — Foundations

| ☐ | Lab | Diff | Time | Cost | Proves | Notes |
|---|---|---|---|---|---|---|
| ☐ | [OverTheWire: Bandit](https://overthewire.org/wargames/bandit/) (all 33) | 1 | 10h | free | Linux CLI, permissions, SUID, SSH | |
| ☐ | [OverTheWire: Natas](https://overthewire.org/wargames/natas/) (1–15) | 2 | 8h | free | Web basics, HTTP, source inspection | |
| ☐ | [Linux Journey](https://linuxjourney.com/) full track | 1 | 6h | free | Filesystem, processes, networking | |
| ☐ | Harden a fresh Ubuntu VM to CIS Level 1 | 2 | 6h | free | Hardening, OpenSCAP, Ansible | |
| ☐ | [picoCTF](https://picoctf.org/) — general skills + web | 1 | 8h | free | Broad fundamentals, tooling | |
| ☐ | Capture and annotate a TLS 1.3 handshake in Wireshark | 2 | 3h | free | TLS, PKI, cert chains | |

---

## Level 2 — Application security

| ☐ | Lab | Diff | Time | Cost | Proves | Notes |
|---|---|---|---|---|---|---|
| ☐ | [PortSwigger](https://portswigger.net/web-security) — **Access control** path | 2 | 6h | free | A01:2025, IDOR, BOLA, privilege escalation | |
| ☐ | PortSwigger — **SQL injection** path | 2 | 8h | free | A05, parameterisation, blind injection | |
| ☐ | PortSwigger — **SSRF** path | 3 | 5h | free | SSRF → metadata → credential theft | |
| ☐ | PortSwigger — **Authentication** + **JWT** paths | 3 | 8h | free | A07, session handling, JWT footguns | |
| ☐ | [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/) — 30+ challenges | 2 | 12h | free | End-to-end AppSec on a modern stack | |
| ☐ | [OWASP crAPI](https://github.com/OWASP/crAPI) | 3 | 8h | free | API Top 10, BOLA/BFLA, mass assignment | |
| ☐ | [PortSwigger BSCP](https://portswigger.net/web-security/certification) exam | 4 | 40h | ~$99 | Recognised AppSec credential | |

---

## Level 3 — Containers & Kubernetes

| ☐ | Lab | Diff | Time | Cost | Proves | Notes |
|---|---|---|---|---|---|---|
| ☐ | Harden a `node:latest` image → distroless, non-root, signed | 2 | 5h | free | Image hardening, measurable CVE reduction | |
| ☐ | Escape a privileged container to the host (own VM) | 3 | 4h | free | Why `--privileged` is not a convenience flag | |
| ☐ | [Kubernetes Goat](https://madhuakula.com/kubernetes-goat/) — all scenarios | 3 | 12h | free | K8s attack paths, RBAC abuse, DIND, SSRF | |
| ☐ | Block every Kubernetes Goat attack with Kyverno policies | 3 | 8h | free | Admission control, policy authoring | |
| ☐ | [Killercoda CKS scenarios](https://killercoda.com/killer-shell-cks) | 3 | 10h | free | CKS exam readiness | |
| ☐ | Default-deny NetworkPolicy across a real workload | 3 | 6h | free | Segmentation without breaking the app | |
| ☐ | [ControlPlane Simulator](https://github.com/controlplaneio/simulator) | 4 | 10h | ~cloud | Realistic cluster attack & defence | |

---

## Level 4 — Cloud

> ⚠️ Use a **throwaway account with a hard billing alarm**. Destroy every lab when you finish. Costs below assume you tear down same-day.

| ☐ | Lab | Diff | Time | Cost | Proves | Notes |
|---|---|---|---|---|---|---|
| ☐ | [flaws.cloud](http://flaws.cloud/) (6 levels) | 2 | 4h | free | S3 exposure, IAM basics, metadata | |
| ☐ | [flaws2.cloud](http://flaws2.cloud/) — attacker **and** defender tracks | 3 | 6h | free | Full SSRF→creds chain, plus detection | |
| ☐ | [CloudGoat](https://github.com/RhinoSecurityLabs/cloudgoat) — 4+ scenarios | 3 | 12h | ~$5 | Real AWS attack paths | |
| ☐ | [IAM Vulnerable](https://github.com/BishopFox/iam-vulnerable) — 10+ paths | 4 | 10h | ~$2 | IAM privilege escalation, the core cloud skill | |
| ☐ | Prowler on a personal account → fix top 10 → codify as SCPs | 3 | 8h | free | CSPM, guardrails, prevention over detection | |
| ☐ | [AzureGoat](https://github.com/ine-labs/AzureGoat) or [GCPGoat](https://github.com/ine-labs/GCPGoat) | 3 | 8h | ~$5 | Second-cloud literacy | |
| ☐ | Map IAM escalation paths with [PMapper](https://github.com/nccgroup/PMapper) | 4 | 4h | free | Graph-based IAM analysis | |

---

## Level 5 — Pipelines & supply chain

| ☐ | Lab | Diff | Time | Cost | Proves | Notes |
|---|---|---|---|---|---|---|
| ☐ | [CICD-Goat](https://github.com/cider-security-research/cicd-goat) — 11 challenges | 3 | 10h | free | OWASP CI/CD Top 10, PPE | |
| ☐ | [GitHub Actions Goat](https://github.com/step-security/github-actions-goat) | 3 | 6h | free | Script injection, secret exfiltration | |
| ☐ | Audit a real public repo with `zizmor` + `poutine` | 2 | 3h | free | Pipeline auditing, exploitability triage | |
| ☐ | Build → SBOM → sign → attest → **verify** end to end | 3 | 8h | free | The whole supply chain control set | |
| ☐ | Enforce signature verification at admission (Kyverno) | 4 | 5h | free | Turning signing into an actual control | |
| ☐ | Simulate a dependency confusion attack in a private lab | 4 | 5h | free | Registry precedence, namespace scoping | |

---

## Level 6 — IaC, runtime & AI

| ☐ | Lab | Diff | Time | Cost | Proves | Notes |
|---|---|---|---|---|---|---|
| ☐ | [TerraGoat](https://github.com/bridgecrewio/terragoat) → fix with Checkov | 2 | 6h | free | IaC misconfiguration | |
| ☐ | Write a custom Checkov/OPA policy Checkov does not ship | 3 | 4h | free | Policy authoring, org-specific rules | |
| ☐ | Falco + [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) | 3 | 8h | free | Detection engineering, tuning | |
| ☐ | Write a Falco rule for something the defaults miss | 4 | 5h | free | Genuine detection engineering | |
| ☐ | Vault/OpenBao: dynamic DB credentials with a 15-min TTL | 3 | 6h | free | Secrets maturity level 3 | |
| ☐ | Replace all static CI cloud keys with OIDC federation | 3 | 4h | free | The single highest-value secrets project | |
| ☐ | Run [`garak`](https://github.com/NVIDIA/garak) against an LLM endpoint you control | 3 | 5h | ~$5 | LLM security testing, prompt injection | |

---

## Weekly log

Track what you actually did. This is more useful than the checkboxes when you come to write your CV — you will have forgotten the details in three months.

| Week | Lab | Hours | What broke | What I learned |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |

---

## Rules of engagement

1. **No hints on the first attempt.** Struggling is where the learning happens. Give it 30 minutes before looking.
2. **Write it up the same day.** A lab you cannot explain a week later did not teach you anything.
3. **Then defend it.** For every attack you performed, name the single cheapest control that would have stopped it.
4. **Only test what you own or are invited to test.** Everything on this sheet qualifies. Your employer's infrastructure does not, no matter how good your intentions.
5. **Destroy cloud labs when you finish.** `cloudgoat destroy`, `terraform destroy`, check the console, check the bill.

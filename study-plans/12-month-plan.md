# 12-Month Foundational Plan

**For:** career switchers, students, IT support / sysadmin / QA backgrounds, and anyone without a development or DevOps background.
**Assumes:** you can use a computer confidently and are willing to learn to code.
**Time:** ~8 hours/week (1 hr on weeknights, 3 hrs at the weekend).
**Outcome:** junior-to-mid DevSecOps engineer with a real portfolio.

If you already work in DevOps or development, use the [6-month plan](6-month-plan.md).

---

## The honest version

Twelve months at 8 hours a week is about 400 hours. That is enough to become genuinely employable, and not enough to become an expert. Nobody becomes an expert in 400 hours, and anyone selling you that is selling you something.

**What actually gets people hired from this plan:**
1. A portfolio of working things, publicly visible
2. Being able to explain *why*, not just *what*
3. Having broken something and understood how

Certificates help you get past screening. The portfolio gets you the offer.

---

## Quarter 1 (months 1–3) — Foundations

You cannot secure what you cannot operate. This quarter is not security. Resist the urge to skip it — most people who bounce off DevSecOps do so because they skipped this.

### Month 1 — Linux & networking
- Linux CLI daily until it is muscle memory: files, permissions, processes, packages, systemd, logs
- [OverTheWire: Bandit](https://overthewire.org/wargames/bandit/) — all 33 levels
- Networking: TCP/IP, DNS, HTTP, TLS. [How DNS works](https://howdns.works/), [How HTTPS works](https://howhttps.works/)
- Set up a home lab: a Linux VM you can break and rebuild

**Deliverable:** a Bash script that hardens a fresh Ubuntu VM (SSH config, firewall, unattended upgrades, auditd), with a README explaining each change.

### Month 2 — Programming
- Python fundamentals: [Automate the Boring Stuff](https://automatetheboringstuff.com/)
- Syntax, data structures, functions, error handling, file I/O, HTTP requests, JSON
- Bash scripting properly, plus ShellCheck
- Git: branching, merging, rebasing, pull requests, and what a commit actually is

**Deliverable:** a Python CLI tool that does something real for you — parse logs, check TLS certificate expiry, audit file permissions. Publish it on GitHub with a README and tests.

### Month 3 — Security fundamentals
- CIA triad, AAA, risk, threat vs vulnerability vs exploit
- Cryptography basics: hashing vs encryption vs signing, TLS, PKI ([Crypto 101](https://www.crypto101.io/))
- [Professor Messer Security+](https://www.professormesser.com/security-plus/sy0-701/sy0-701-video/sy0-701-comptia-security-plus-course/) — free, complete
- [MITRE ATT&CK](https://attack.mitre.org/): browse it, pick five techniques, understand them properly
- [TryHackMe](https://tryhackme.com/) beginner paths

**Deliverable:** a write-up of one real breach mapped to ATT&CK techniques, with the three cheapest controls that would have broken the chain.

> **Optional:** sit CompTIA Security+ around month 4 if you need a credential to get past HR filters. Skip it if you already work in tech.

---

## Quarter 2 (months 4–6) — Application security & the delivery system

### Month 4 — Web application security
- [PortSwigger Web Security Academy](https://portswigger.net/web-security): Access control, Authentication, SQL injection, XSS, SSRF, CSRF
- [OWASP Top 10:2025](https://owasp.org/Top10/2025/) — read the real document
- [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/)

**Deliverable:** write-ups of ten PortSwigger labs — attack, root cause, fix, and the class of issue.

### Month 5 — Containers
- Docker properly: images, layers, volumes, networking, Compose
- Container internals: namespaces, cgroups, capabilities
- Image hardening: multi-stage builds, non-root, distroless, digests
- Trivy, Hadolint, Syft

**Deliverable:** a containerised version of your month-2 tool — hardened image, scanned, SBOM generated, before/after CVE counts documented.

### Month 6 — CI/CD
- GitHub Actions: workflows, jobs, secrets, environments, OIDC
- Build a pipeline: lint → test → build → scan → publish
- Add security gates: Gitleaks, Semgrep, Trivy, Dependabot/Renovate
- Understand *why* each gate exists and what it cannot see

**Deliverable:** your tool's repo with a full pipeline running, badges in the README, and a document explaining each control.

---

## Quarter 3 (months 7–9) — Cloud & Kubernetes

### Month 7 — Cloud fundamentals
- Pick one cloud (AWS is the largest job market; Azure is strong in enterprise)
- Free tier account **with a hard billing alarm** set on day one
- Core services: compute, storage, networking, and above all **IAM**
- Deploy something real and make it work

**Deliverable:** a small application deployed to the cloud entirely via Terraform, in a public repo.

### Month 8 — Cloud security
- IAM deeply: policies, roles, trust relationships, least privilege
- [flaws.cloud](http://flaws.cloud/) and [flaws2.cloud](http://flaws2.cloud/)
- Prowler / ScoutSuite against your own account
- Logging, encryption, network controls, guardrails

**Deliverable:** a before/after Prowler report on your own account, with the fixes codified in Terraform.

### Month 9 — Kubernetes
- Kubernetes fundamentals: pods, deployments, services, ingress, RBAC
- Consider CKA-level study material — it also builds the security foundation
- Pod Security Standards, securityContext, NetworkPolicy
- [Kubernetes Goat](https://madhuakula.com/kubernetes-goat/)

**Deliverable:** your application running on Kubernetes with hardened manifests and a default-deny NetworkPolicy.

---

## Quarter 4 (months 10–12) — DevSecOps proper

### Month 10 — Supply chain & pipeline hardening
- SBOM generation, cosign signing, SLSA provenance
- [OWASP Top 10 CI/CD Risks](https://owasp.org/www-project-top-10-ci-cd-security-risks/); read the `tj-actions` post-mortems
- Audit workflows with `zizmor` / `poutine`; pin everything to SHAs
- [CICD-Goat](https://github.com/cider-security-research/cicd-goat)

**Deliverable:** signed and attested releases, with verification enforced by a Kyverno policy at admission.

### Month 11 — Policy, secrets & runtime
- OPA/Rego basics, Conftest, Checkov on Terraform plans
- Kyverno policy library with tests
- Vault or OpenBao: dynamic secrets; External Secrets Operator
- Falco + [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team)

**Deliverable:** a policy library with CI tests, and one Falco rule you wrote yourself.

### Month 12 — AI security, governance & job hunt
- [OWASP LLM Top 10](https://genai.owasp.org/llm-top-10/) and Agentic Top 10
- Vulnerability management: EPSS, KEV, VEX; build a triage script
- Threat modeling with STRIDE on your own system
- Polish the portfolio; write the capstone; practise interviews; apply

**Deliverable:** a capstone repository and write-up tying the whole year together.

---

## Weekly rhythm

| When | What | Time |
|---|---|---|
| Mon–Thu | One focused hour. Same time each day — consistency beats intensity. | 4 hrs |
| Saturday | Hands-on: labs and building | 3 hrs |
| Sunday | Write up the week, plan the next | 1 hr |

**Protect the streak, not the hours.** Four consistent hours a week beats one heroic twelve-hour Saturday every third weekend.

---

## Budget

| Item | Cost | Necessary? |
|---|---|---|
| Cloud free tier + billing alarm | $0–20/mo | Yes — set the alarm first |
| TryHackMe subscription | ~$14/mo | Optional, good value early |
| CompTIA Security+ | ~$400 | Only if you need it for screening |
| Burp Suite Certified Practitioner | ~$99 | Excellent value, well respected |
| CKA + CKS | ~$800 | Worth it in year 2, not year 1 |
| Everything else in this roadmap | $0 | Genuinely free |

**Minimum viable path: about $50 of cloud spend across the year.** Do not let a paywall stop you — nearly every essential resource here is free.

---

## Signs you are on track

| Month | You should be able to… |
|---|---|
| 3 | Navigate Linux without googling basics; write a useful Python script |
| 6 | Build and secure a CI/CD pipeline from scratch |
| 9 | Find and fix misconfigurations in a cloud account you have never seen |
| 12 | Explain, to a developer, why their code is vulnerable and how to fix it — without being annoying about it |

## Signs you are drifting

- Collecting courses without building anything → **stop watching, start breaking things**
- Studying certificates instead of systems → the certificate is not the skill
- Learning twelve tools shallowly → pick one per category and go deep
- Never writing anything down → you will not retain it, and you will have nothing to show

---

## After month 12

- Apply for junior DevSecOps, cloud security, or platform engineering roles — also apply for DevOps roles and be the person who brings security with them
- Contribute to an OSS security tool (a rule, a doc fix, a reproduction)
- Consider CKS if Kubernetes is your direction, or the Burp Practitioner exam if you lean AppSec
- Go deep in **one** area. Generalists get hired; specialists get promoted.

# Hands-On Labs

Reading a roadmap teaches you vocabulary. Breaking things teaches you security.

This is an **ordered** progression. Each lab lists what you should be able to explain when you finish — if you cannot explain it, the lab did not land and repeating it is worth more than moving on.

Everything here is free unless marked otherwise. **Only run offensive tooling against systems you own or that explicitly invite testing.** The labs below all do.

---

## Level 1 — Foundations (weeks 1–4)

### 1.1 Linux via CTF — [OverTheWire: Bandit](https://overthewire.org/wargames/bandit/)
33 levels of Linux fundamentals disguised as a game. Do all of them.

> **You should be able to explain:** file permissions and how SUID works, what `find` with `-perm` is really doing, how SSH keys authenticate you, why `/tmp` is dangerous.

### 1.2 Web fundamentals — [PortSwigger Web Security Academy](https://portswigger.net/web-security)
The best free security training in existence. Start with the **Access control** and **SQL injection** paths.

> **You should be able to explain:** why authorization must be checked server-side on every request, the difference between authentication and authorization, how a parameterized query actually prevents injection.

### 1.3 A vulnerable app end to end — [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/)
```bash
docker run --rm -p 3000:3000 bkimminich/juice-shop
```
Work through the challenges without the hints first. Then read the [companion guide](https://pwning.owasp-juice.shop/).

> **You should be able to explain:** how you found each flaw, and which single control would have prevented it.

---

## Level 2 — The delivery system (weeks 5–10)

### 2.1 Container escapes — [Kubernetes Goat](https://madhuakula.com/kubernetes-goat/)
Deliberately vulnerable cluster with guided scenarios: container escape, sensitive keys in code, DIND exploitation, SSRF in the cluster, hidden Helm history, RBAC misconfiguration.

> **You should be able to explain:** why a mounted Docker socket equals node compromise, what `hostPID` gives an attacker, how a service account token becomes cluster access.

### 2.2 Harden what you just broke
Take a naïve `node:latest` Dockerfile and drive it to:
- distroless or Wolfi base, referenced by digest
- non-root user with a fixed UID
- read-only root filesystem, all capabilities dropped
- SBOM generated, image signed with cosign

Record the vulnerability count before and after.

> **You should be able to explain:** which change removed the most CVEs, and why (hint: it is almost never the application dependencies).

### 2.3 Admission control
Deploy Kyverno into a kind cluster and apply [`examples/kyverno/baseline-policies.yaml`](../examples/kyverno/baseline-policies.yaml). Then try to deploy the Kubernetes Goat workloads again.

> **You should be able to explain:** the difference between validating, mutating, and generating policies, and why `failurePolicy: Fail` matters for a security webhook.

### 2.4 CKS practice — [Killercoda CKS scenarios](https://killercoda.com/killer-shell-cks)
Free, timed, hands-on scenarios matching the Certified Kubernetes Security Specialist exam.

---

## Level 3 — Cloud (weeks 8–14)

### 3.1 [flaws.cloud](http://flaws.cloud/) then [flaws2.cloud](http://flaws2.cloud/)
Six and then ten levels of real AWS misconfiguration, in increasing difficulty. flaws2 has both an attacker and a defender track — do both.

> **You should be able to explain:** the SSRF → instance metadata → credential theft chain, and exactly how IMDSv2 breaks it.

### 3.2 [CloudGoat](https://github.com/RhinoSecurityLabs/cloudgoat)
Terraform-deployed vulnerable AWS scenarios. Deploy into a **throwaway account with a hard billing limit**, and always `cloudgoat destroy` afterwards.

> **You should be able to explain:** at least three IAM privilege escalation paths, and what a permission boundary would have done about them.

### 3.3 [IAM Vulnerable](https://github.com/BishopFox/iam-vulnerable)
Focused entirely on IAM privilege escalation — 31 paths. This is where cloud security actually lives.

### 3.4 Fix it, then codify it
Run Prowler against a personal account. Fix the top ten findings. Then write SCPs / Org Policies so those findings cannot recur.

> **You should be able to explain:** the difference between detecting a misconfiguration and making it impossible.

---

## Level 4 — Pipelines & supply chain (weeks 12–18)

### 4.1 [CICD-Goat](https://github.com/cider-security-research/cicd-goat)
A deliberately vulnerable CI/CD environment (Jenkins, GitLab, Gitea) with 11 challenges mapped to the OWASP Top 10 CI/CD risks.

> **You should be able to explain:** Poisoned Pipeline Execution, and why `pull_request_target` with a checkout of untrusted code is so dangerous.

### 4.2 [GitHub Actions Goat](https://github.com/step-security/github-actions-goat)
Script injection, secret exfiltration, artifact poisoning — in the CI system you probably use daily.

### 4.3 Audit something real
Run `zizmor` and `poutine` against a public repository you use. Read every finding and decide whether it is genuinely exploitable.

> **You should be able to explain:** why SHA pinning is not paranoia, using the `tj-actions` timeline as your example.

### 4.4 Build a signed, attested release
End to end, on a repo of your own:
1. Build an image in GitHub Actions
2. Generate a CycloneDX SBOM at build time
3. Sign keyless with cosign
4. Generate SLSA provenance
5. **Verify all of it in a separate job**
6. Enforce verification with a Kyverno policy in a kind cluster

> **You should be able to explain:** what the signature actually proves, and what it does not.

---

## Level 5 — IaC, detection, and AI (weeks 16–24)

### 5.1 [TerraGoat](https://github.com/bridgecrewio/terragoat) · [CfnGoat](https://github.com/bridgecrewio/cfngoat)
Vulnerable IaC. Scan with Checkov, fix the findings, then write a **custom** policy for a rule Checkov does not have.

### 5.2 Detection engineering with Falco
Deploy Falco, run techniques from [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) against a test workload, and watch the alerts fire. Then find something Falco's default rules miss and write a rule for it.

> **You should be able to explain:** why a rule with a 5% false positive rate at scale is worse than no rule.

### 5.3 API security — [crAPI](https://github.com/OWASP/crAPI)
OWASP's "completely ridiculous API" — BOLA, BFLA, mass assignment, and the rest of the API Top 10.

### 5.4 AI/LLM security
- Read the [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/)
- Run [`garak`](https://github.com/NVIDIA/garak) against a model endpoint you control
- Build a small RAG app, then break its tenant isolation
- Threat-model an agentic workflow: write out every tool the agent can call and what a successful prompt injection would let it do

> **You should be able to explain:** why prompt injection has no complete fix, and what "design so a successful injection cannot do damage" means concretely.

---

## Ongoing

| Activity | Cadence | Why |
|---|---|---|
| [PortSwigger Academy](https://portswigger.net/web-security) labs | Weekly | ~250 labs; finishing them all is a genuine credential |
| [TryHackMe](https://tryhackme.com/) / [Hack The Box](https://www.hackthebox.com/) | Weekly | Keeps the offensive muscle alive |
| [CTFtime](https://ctftime.org/) events | Monthly | Time pressure teaches triage |
| [picoCTF](https://picoctf.org/) | Anytime | Excellent, free, permanently available |
| Read one real post-mortem | Weekly | The best curriculum is what actually went wrong |

---

## Building your portfolio

Employers cannot verify what you have read. They can verify what you have built. Each of the following is worth more than a certificate on a CV:

1. **A hardened pipeline template** — public repo, working, documented, with the reasoning for each control
2. **Custom Semgrep rules** with tests, for a real anti-pattern class
3. **A write-up of a lab you broke** — the attack path, the fix, and how you would prevent the class of issue
4. **A Kyverno/OPA policy library** with `kyverno test` coverage
5. **A tool you built** — even a small SARIF normaliser that deduplicates findings across scanners
6. **A contribution to an OSS security tool** — a rule, a doc fix, a bug report with a reproduction

> Write up what you learn as you go. Half the value of a lab is the explanation you write afterwards; it is also the artifact you can show someone.

---

## Safety and legality

- Only test systems you own or that explicitly permit testing. Everything linked here does.
- Deploy cloud labs (CloudGoat, IAM Vulnerable, AzureGoat) into a **throwaway account** with a hard billing limit, and destroy them afterwards.
- Never point offensive tooling at your employer's infrastructure without written authorization, however good your intentions.
- Vulnerable apps are vulnerable — do not expose them to the internet. Keep them on localhost or an isolated network.

# Checklists

Practical, opinionated checklists you can drop into a PR template, a design review, or an audit.

They are deliberately **not** exhaustive standards documents. Each is the subset of controls that, in practice, prevents most of what actually goes wrong.

| Checklist | Use it when |
|---|---|
| [Pipeline security](pipeline-security.md) | Auditing or building a CI/CD system · mapped to OWASP Top 10 CI/CD Risks |
| [Container security](container-security.md) | Reviewing a Dockerfile, base image policy, or registry setup |
| [Kubernetes security](kubernetes-security.md) | Hardening a cluster · mapped to NSA/CISA and CIS |
| [Cloud security](cloud-security.md) | Reviewing an AWS/Azure/GCP account or landing zone |
| [Supply chain security](supply-chain-security.md) | Building SBOM, signing, and provenance capability |
| [Secure code review](secure-code-review.md) | Reviewing a pull request · ordered by real-world breach frequency |
| [Secrets management](secrets-management.md) | Removing long-lived credentials · maturity ladder from committed `.env` to workload identity |
| [Incident response](incident-response.md) | Preparing for, or running, a cloud-native incident · mapped to NIST SP 800-61r3 |
| [AI, LLM & agentic security](ai-llm-security.md) | Building or reviewing an LLM feature or agent · mapped to OWASP LLM Top 10 (2025) and Agentic Top 10 (2026) |

## How to use them

**Do not** run every item on every change. That is how checklists get ignored.

1. **Pick a scope.** One system, one quarter.
2. **Baseline honestly.** Mark what is already true. Resist the urge to mark "partially".
3. **Rank the gaps** by (blast radius × likelihood) ÷ effort. The top three are your roadmap.
4. **Automate what you fix.** A checked box that depends on someone remembering will be unchecked in six months. Turn it into a policy, a test, or a pipeline gate.
5. **Re-run quarterly**, and track the trend rather than the absolute number.

## Turning a checklist into enforcement

| Checklist item lives best as… | Mechanism |
|---|---|
| A rule about code | Semgrep rule, linter, unit test |
| A rule about infrastructure | OPA/Checkov policy on the Terraform plan |
| A rule about what runs | Kyverno/Gatekeeper admission policy |
| A rule about artifacts | Signature + provenance verification at deploy |
| A rule about the pipeline | Required status check + CODEOWNERS on workflow files |
| A rule about behaviour at runtime | Falco/Tetragon rule + alert |

If an item cannot be expressed as one of the above, ask whether it is a real control or an aspiration.

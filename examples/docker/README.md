# Container hardening: before and after

Two Dockerfiles for the same application. [`Dockerfile.naive`](Dockerfile.naive) is what you get from the first search result. [`Dockerfile`](Dockerfile) is what you should ship. The gap between them is [lab 2.2](../../labs/README.md) and [project P2](../../projects/README.md).

The point of running both is not to admire the second one. It is to **measure** the difference, because the measurement teaches something counterintuitive:

> Almost all of your container CVEs come from the base image, and almost none come from your application's dependencies. Changing one `FROM` line usually removes more findings than a quarter of dependency upgrades.

Teams routinely spend months tuning scanner ignore rules for findings that a base image change would have deleted outright.

---

## The exercise

```bash
docker build -f Dockerfile.naive -t app:naive .
docker build -f Dockerfile        -t app:hardened .

trivy image app:naive
trivy image app:hardened

docker images | grep app          # size difference
docker history app:naive          # find the NPM_TOKEN, still there
```

Record, in a table: total CVEs, critical/high, image size, and **which change removed which findings**. That table is the deliverable — it is what makes P2 worth putting on a CV, and it is what you will be asked about in an interview.

Run two scanners. They will disagree, sometimes substantially. Working out why — different vulnerability databases, different package detection, different opinions about whether an unfixed CVE counts — is more educational than either number.

---

## What each change actually buys

| Change | What it removes |
|---|---|
| **Distroless/Wolfi runtime base** | The large majority of CVEs, plus the shell and package manager an attacker needs after RCE |
| **Multi-stage build** | Compilers, dev dependencies, source, and build secrets from the shipped image |
| **Digest pinning** | Unreproducible builds and silent base image swaps |
| **Non-root numeric UID** | Container escape as root on the node |
| **`npm ci --ignore-scripts`** | Install-time execution — the main npm supply chain path |
| **`.dockerignore` allowlist** | `.git`, `.env`, credentials, CI config leaking into layers |
| **BuildKit secret mounts** | Credentials recoverable from `docker history` forever |
| **Read-only rootfs, dropped caps** *(runtime)* | Persistence and privilege escalation after a successful exploit |

Ordered by findings removed, the first row dwarfs everything else. Ordered by *incidents prevented*, the last three do more work — they change what an attacker can do after they are already in, which is the part CVE counts do not measure at all.

That distinction is worth being explicit about: **a low CVE count is a proxy metric.** It is easy to measure and easy to improve, which is exactly why it attracts attention out of proportion to its value. An image with zero CVEs running as root with a mounted Docker socket is a worse outcome than an image with forty low-severity CVEs running read-only, non-root, with dropped capabilities.

---

## Choosing a runtime base

| Base | Trade-off |
|---|---|
| **[Distroless](https://github.com/GoogleContainerTools/distroless)** | No shell, no package manager. Tracks Debian stable, so fixes arrive on Debian's cadence — which is the main criticism of it |
| **[Wolfi](https://github.com/wolfi-dev) / [Chainguard](https://images.chainguard.dev/)** | Built for containers, continuously rebuilt, typically patched fastest; free tier keeps only recent tags |
| **[Docker Hardened Images](https://www.docker.com/products/hardened-images/)** | Open-sourced under Apache 2.0 in December 2025; worth evaluating if you are already on Docker Hub |
| **Alpine** | Small and has a shell — the shell is the trade-off; musl also breaks some native modules |
| **UBI Micro / Chiselled Ubuntu** | The right answer if you have a support contract that depends on it |

Any of these beats a full distro. **The choice between them matters far less than making one and pinning it by digest.** Do not spend a month on this decision.

## Verifying before you trust

None of the above tells you that the image running in production is the image you built. That requires signing at build time and **verifying at admission** — see [`../github-actions/devsecops-pipeline.yml`](../github-actions/devsecops-pipeline.yml) for the build side and [`../kyverno/baseline-policies.yaml`](../kyverno/baseline-policies.yaml) for the enforcement side.

```bash
cosign verify app:hardened \
  --certificate-identity-regexp '^https://github\.com/your-org/' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

Verification checks the **identity of the signer**, not merely that a signature exists. A policy that accepts any valid signature accepts the attacker's.

---

## See also

- [`checklists/container-security.md`](../../checklists/container-security.md) — the full review checklist
- [`../trivy/trivy.yaml`](../trivy/trivy.yaml) — shared scanner config with a documented ignore policy
- [`../kyverno/baseline-policies.yaml`](../kyverno/baseline-policies.yaml) — enforcing the runtime half at admission
- [Docker build best practices](https://docs.docker.com/build/building/best-practices/) · [hadolint](https://github.com/hadolint/hadolint)

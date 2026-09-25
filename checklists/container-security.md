# Container & Image Security Checklist

A container is a process with restricted views of the kernel. Everything below follows from that.

---

## Base image

- [ ] Base image is minimal — distroless, Chainguard/Wolfi, Alpine, or a slim variant
- [ ] Base image is referenced **by digest**, not by a mutable tag
- [ ] Base image comes from a trusted, mirrored registry — not an arbitrary Docker Hub account
- [ ] Base images are rebuilt on a schedule so patches actually land
- [ ] There is a small, curated set of approved base images, not one per team

## Dockerfile

- [ ] Multi-stage build — build tooling and source do not ship in the final image
- [ ] Explicit non-root `USER` with a fixed, non-zero UID
- [ ] No package manager, shell, or curl in the runtime stage (unless genuinely required)
- [ ] `COPY` used instead of `ADD` (no implicit remote fetch or archive extraction)
- [ ] `.dockerignore` excludes `.git`, `.env`, credentials, and test fixtures
- [ ] **No secrets in any layer** — build secrets use BuildKit `--mount=type=secret`; a secret deleted in a later layer is still present in the earlier one
- [ ] Package installs pin versions and clear caches in the same layer
- [ ] `HEALTHCHECK` defined
- [ ] Image labels record source commit, build time, and maintainer (OCI annotations)
- [ ] Dockerfile passes `hadolint` with no high-severity findings

## Build

- [ ] Build runs in an isolated, ephemeral environment
- [ ] Dependencies resolved from a lockfile with integrity hashes
- [ ] SBOM generated at build time (`syft`, CycloneDX or SPDX)
- [ ] Image scanned for vulnerabilities before push (`trivy image`, `grype`)
- [ ] Build fails on new critical/high vulnerabilities with an available fix
- [ ] Image signed with `cosign` (keyless via OIDC preferred)
- [ ] SLSA provenance attestation attached to the image
- [ ] SBOM attached as an attestation, not just stored as a build artifact

## Registry

- [ ] Private registry with authentication; anonymous pull disabled where appropriate
- [ ] Tag immutability enabled — a pushed tag cannot be overwritten
- [ ] Continuous re-scanning of stored images as new CVEs are published
- [ ] Retention/expiry policy removes stale images
- [ ] Signature verification enforced on pull or at admission
- [ ] Pull-through cache for upstream registries (availability *and* provenance control)

## Runtime configuration

- [ ] **Never `--privileged`**
- [ ] `cap_drop: ALL`, then add back only the specific capabilities required
- [ ] `no-new-privileges: true`
- [ ] Read-only root filesystem, with explicit writable volumes for what needs it
- [ ] Non-root user enforced at runtime (`runAsNonRoot: true`), not just declared in the image
- [ ] Seccomp profile applied (`RuntimeDefault` at minimum)
- [ ] AppArmor or SELinux profile applied
- [ ] Docker socket is **never** mounted into a container
- [ ] No `hostPID`, `hostIPC`, or `hostNetwork` unless justified and reviewed
- [ ] Host paths are not mounted writable; `/proc` and `/sys` are not writable
- [ ] Memory and CPU limits set (denial-of-service control)
- [ ] User namespace remapping or rootless runtime where feasible

## Runtime monitoring

- [ ] Runtime detection deployed (Falco, Tetragon, Tracee)
- [ ] Drift detection — a running container whose filesystem changed is an incident
- [ ] Egress network policy applied; containers cannot reach arbitrary internet hosts
- [ ] Container logs shipped centrally and retained
- [ ] Alerts for: shell spawned in a container, package manager executed, sensitive file read, unexpected outbound connection

---

## Quick commands

```bash
# Lint the Dockerfile
hadolint Dockerfile

# Vulnerability scan, fail on fixable high/critical
trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 myimage:tag

# Config/CIS audit of the built image
dockle myimage:tag

# Generate an SBOM
syft myimage:tag -o cyclonedx-json=sbom.cdx.json

# Sign and attest (keyless)
cosign sign myimage@sha256:...
cosign attest --predicate sbom.cdx.json --type cyclonedx myimage@sha256:...

# Verify before deploying
cosign verify --certificate-identity-regexp '.*' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  myimage@sha256:...

# Audit the Docker host itself
docker run --rm --net host --pid host --cap-add audit_control \
  -v /var/lib:/var/lib:ro -v /var/run/docker.sock:/var/run/docker.sock:ro \
  docker/docker-bench-security
```

## Further reading

- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [NIST SP 800-190: Application Container Security Guide](https://csrc.nist.gov/pubs/sp/800/190/final)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [Docker build best practices](https://docs.docker.com/build/building/best-practices/)

# Kubernetes Security Checklist

Aligned with the [NSA/CISA Kubernetes Hardening Guide](https://media.defense.gov/2022/Aug/29/2003066362/-1/-1/0/CTR_KUBERNETES_HARDENING_GUIDANCE_1.2_20220829.PDF), the [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes), and the [OWASP Kubernetes Top 10](https://owasp.org/www-project-kubernetes-top-ten/).

---

## Control plane

- [ ] API server is not exposed to the public internet (or is restricted by IP allow-list)
- [ ] **etcd is encrypted at rest** and reachable only from the API server
- [ ] etcd has its own TLS client certificates, separate from the rest of the cluster
- [ ] Anonymous authentication is disabled (`--anonymous-auth=false`)
- [ ] Audit logging is enabled with a considered policy, and logs ship off-cluster
- [ ] Admission plugins are reviewed: `NodeRestriction`, `PodSecurity` enabled; `AlwaysAdmit` absent
- [ ] Kubernetes version is supported and patched
- [ ] `kube-bench` passes the CIS master and node checks

## Nodes

- [ ] kubelet authentication and authorization are enabled (`--anonymous-auth=false`, `--authorization-mode=Webhook`)
- [ ] kubelet read-only port is disabled (`--read-only-port=0`)
- [ ] Nodes run a minimal, hardened OS (Bottlerocket, Talos, Flatcar, or a CIS-hardened image)
- [ ] SSH access to nodes is removed or tightly restricted
- [ ] Instance metadata service is protected — pods cannot reach node IAM credentials (IMDSv2 with hop limit 1, or network policy blocking 169.254.169.254)
- [ ] Node auto-upgrade / rebuild cadence is defined

## Authentication & RBAC

- [ ] No user or workload holds `cluster-admin` outside break-glass procedures
- [ ] No wildcard verbs or resources in Roles (`*` on `*`)
- [ ] The `escalate`, `bind`, and `impersonate` verbs are granted to nobody routinely (each is a privilege escalation path)
- [ ] Nobody can create pods in a namespace whose ServiceAccounts are more privileged than they are
- [ ] `secrets: get/list` is tightly restricted
- [ ] Default ServiceAccount token automounting is disabled (`automountServiceAccountToken: false`)
- [ ] Each workload has a dedicated ServiceAccount with minimum permissions
- [ ] Cloud IAM is bound via workload identity federation, not node instance roles
- [ ] Human access is via SSO with short-lived credentials, not long-lived kubeconfigs
- [ ] RBAC is reviewed on a schedule (`rbac-tool`, `KubiScan`)

## Workload security

- [ ] Pod Security Admission enforces `restricted` in application namespaces
- [ ] `runAsNonRoot: true` and an explicit non-zero `runAsUser`
- [ ] `allowPrivilegeEscalation: false`
- [ ] `privileged: false`; no `CAP_SYS_ADMIN`
- [ ] `capabilities.drop: ["ALL"]`
- [ ] `readOnlyRootFilesystem: true`
- [ ] `seccompProfile.type: RuntimeDefault`
- [ ] No `hostNetwork`, `hostPID`, `hostIPC`
- [ ] No `hostPath` volumes (especially not `/`, `/var/run/docker.sock`, or `/proc`)
- [ ] Resource `requests` and `limits` set on every container
- [ ] Images referenced by digest; `:latest` is blocked
- [ ] `imagePullPolicy: Always` for mutable environments

## Admission control & policy as code

- [ ] A policy engine is deployed and **enforcing**, not just auditing (Kyverno, Gatekeeper, or ValidatingAdmissionPolicy)
- [ ] Policies block: privileged pods, host namespaces, hostPath mounts, `:latest`, missing resource limits, unsigned images
- [ ] **Image signature verification at admission** (`cosign` / Kyverno `verifyImages`)
- [ ] Policies are versioned in Git and tested in CI (`kyverno test`, `conftest`)
- [ ] Exceptions are explicit, namespaced, owned, and expiring
- [ ] The policy webhook has a considered failure policy (`Fail` for security-critical rules)

## Network

- [ ] **Default-deny NetworkPolicy for ingress AND egress** in every namespace
- [ ] Explicit allow rules per workload, reviewed with the service owner
- [ ] DNS egress is allowed narrowly (to kube-dns only)
- [ ] Cluster-internal traffic is encrypted (service mesh mTLS or a CNI providing transparent encryption)
- [ ] Ingress controllers are patched and minimally configured (a recurring source of critical CVEs)
- [ ] LoadBalancer/NodePort services are inventoried — each is internet exposure
- [ ] Egress to the internet goes through a controlled gateway where feasible

## Secrets

- [ ] Kubernetes Secrets are encrypted at rest with a KMS provider (base64 is not encryption)
- [ ] Secrets are sourced from an external manager (Vault, ESO, cloud Secret Manager) rather than committed
- [ ] Secrets mounted as files, not environment variables (env vars leak into logs, crash dumps, and `/proc`)
- [ ] No secrets in ConfigMaps, container images, or Helm values in Git
- [ ] GitOps repos use SOPS/Sealed Secrets if secrets must live in Git at all
- [ ] ServiceAccount tokens are bound and short-lived (projected tokens with an audience)

## Supply chain

- [ ] Only images from approved registries are admitted
- [ ] Signature and provenance verified before admission
- [ ] Images continuously rescanned in-cluster (`trivy-operator`)
- [ ] Helm charts and operators are from trusted sources and pinned
- [ ] Third-party operators are reviewed — many request cluster-admin

## Detection & response

- [ ] Runtime security deployed (Falco, Tetragon, Tracee) with tuned rules
- [ ] Kubernetes audit logs are monitored for: exec into pod, secret access, RBAC changes, privileged pod creation
- [ ] Posture scanning on a schedule (`kubescape`, `kube-bench`, `polaris`)
- [ ] Incident playbook exists for a compromised pod (isolate with a deny-all NetworkPolicy — do not delete it, you destroy the evidence)

---

## Quick commands

```bash
# CIS benchmark
kube-bench run --targets master,node,etcd,policies

# Posture scan against NSA/CISA + CIS frameworks
kubescape scan framework nsa,cis-v1.10.0 --format html --output report.html

# What can this service account do?
kubectl auth can-i --list --as=system:serviceaccount:default:my-sa

# Find dangerous RBAC
rbac-tool analysis
kubectl get clusterrolebindings -o json | jq -r \
  '.items[] | select(.roleRef.name=="cluster-admin") | .metadata.name'

# Find pods running as root / privileged
kubectl get pods -A -o json | jq -r '.items[]
  | select(.spec.containers[].securityContext.privileged==true)
  | "\(.metadata.namespace)/\(.metadata.name)"'

# Namespaces with no NetworkPolicy at all
comm -23 <(kubectl get ns -o name | cut -d/ -f2 | sort) \
         <(kubectl get netpol -A -o jsonpath='{.items[*].metadata.namespace}' | tr ' ' '\n' | sort -u)

# Continuous in-cluster scanning
kubectl get vulnerabilityreports -A
```

## Further reading

- [Kubernetes security documentation](https://kubernetes.io/docs/concepts/security/)
- [NSA/CISA Kubernetes Hardening Guide](https://media.defense.gov/2022/Aug/29/2003066362/-1/-1/0/CTR_KUBERNETES_HARDENING_GUIDANCE_1.2_20220829.PDF)
- [OWASP Kubernetes Top 10](https://owasp.org/www-project-kubernetes-top-ten/)
- [Kyverno policy library](https://kyverno.io/policies/)
- [Kubernetes Goat](https://madhuakula.com/kubernetes-goat/) — practise the attacks these controls prevent

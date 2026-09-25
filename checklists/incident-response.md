# Cloud-Native Incident Response Checklist

**Aligned to [NIST SP 800-61r3](https://csrc.nist.gov/pubs/sp/800/61/r3/final): prepare → detect & analyse → contain → eradicate & recover → learn.**

Cloud-native incident response differs from the traditional kind in one way that changes everything else:

> **The evidence deletes itself.**

A pod lives for ninety seconds. A node is replaced by an autoscaler mid-investigation. A `kubectl delete pod` — the instinctive first reaction — destroys the process tree, the filesystem, and the memory you needed, and the ReplicaSet cheerfully starts a clean copy so the attacker's foothold looks like it never existed. Traditional IR assumes the disk is still there tomorrow. Here it is not.

Everything in §1 exists because of that sentence. If you only do one section before an incident, do that one.

---

## 1. Preparation

*The only section you can complete before an incident, and the only one that determines how the rest go.*

- [ ] A named **incident commander** role exists, with a rota and a documented handover
- [ ] Severity levels are defined with **examples**, not adjectives, so classification is not a debate at 3am
- [ ] An out-of-band communication channel exists — if the incident is in your cloud account, your chat tool may be in it too
- [ ] Contact paths are current: cloud provider support, legal, comms, insurance, key vendors, and law enforcement if applicable
- [ ] Regulatory reporting clocks are known **in advance**: GDPR 72 hours, and under the EU CRA from **11 Sep 2026**, 24-hour reporting of actively exploited vulnerabilities to ENISA
- [ ] Logs are **centralised off the compromised plane** — an attacker with account access must not be able to delete the audit trail
- [ ] Audit logging is on and retained: cloud audit logs, Kubernetes API audit logs, admission decisions, container runtime events
- [ ] Log retention exceeds realistic dwell time — a 7-day retention against a 90-day intrusion tells you nothing
- [ ] Runtime detection is deployed and tuned before you need it ([`examples/falco/`](../examples/falco/custom-rules.yaml)) — it is the only source of process-level evidence once a container is gone
- [ ] Forensic tooling and permissions exist **now**: snapshot rights, an isolated forensics account or namespace, an image registry the responders can pull from
- [ ] A break-glass identity exists, is protected, alerts on use, and has been tested
- [ ] Asset ownership is mapped: for any workload, who owns it and what data it touches
- [ ] Runbooks exist for the incidents you will actually have: **leaked cloud key**, compromised CI, compromised container, ransomware, dependency compromise, insider access
- [ ] Runbooks are **rehearsed** — a tabletop at minimum, once per quarter, timed
- [ ] Restores from backup have been tested this year; backups are immutable and in a separate trust boundary

> Rehearse the leaked-cloud-key runbook first. It is the incident you are most likely to actually have, and the one where the first fifteen minutes decide the outcome.

## 2. Detection and analysis

- [ ] Alerts carry enough context to triage without a console: identity, resource, region, cluster, namespace, workload, and what fired
- [ ] Detection covers the paths that matter: impossible-travel and anomalous IAM use, new IAM principals or trust-policy edits, disabled logging, public exposure of a bucket or database, egress to new destinations, container escape indicators, credential access from workloads
- [ ] There is a documented **triage decision**: is this an incident, and at what severity?
- [ ] The first action is to **start a timeline document** — every action, with a UTC timestamp and who did it
- [ ] Scope is established before containment where possible: which identities, which workloads, which data, which time window
- [ ] "How did they get in?" and "what did they do?" are tracked as separate questions — closing the first without answering the second means they come back
- [ ] Cloud audit logs are queried for the **full** exposure window, not just since the alert
- [ ] Related detections are correlated before concluding it is a single event

## 3. Containment — without destroying the evidence

**The order of operations here is the difference between an investigation and a guess.**

- [ ] **Isolate, do not delete.** Apply a deny-all NetworkPolicy to the pod; do not `kubectl delete pod`
- [ ] Remove the pod's labels so the ReplicaSet replaces it and stops routing traffic to it, while the original object stays for analysis
- [ ] Cordon the node (`kubectl cordon`) to stop new scheduling — **capture evidence before `kubectl drain`**
- [ ] For a suspect node: snapshot the volume and capture memory *before* terminating it; take the node out of the load balancer and out of the autoscaling group so nothing recycles it under you
- [ ] Revoke credentials at the **session** level, not just the key level — deleting an access key does not kill an issued STS session; use a deny-all policy or session revocation
- [ ] Rotate anything the compromised workload could read, including secrets it merely had permission to read
- [ ] Check for persistence before declaring containment: new IAM users, access keys, roles and trust-policy changes, OAuth grants, deploy keys, webhooks, scheduled tasks, mutating admission webhooks, modified CronJobs, new DaemonSets
- [ ] Restrict egress rather than allowing exfiltration to continue during analysis
- [ ] Preserve the container **image by digest** — the running tag will be overwritten
- [ ] Block the initial access vector so containment is not undone mid-response

### Evidence to capture, in order of volatility

- [ ] Memory of the running container/process (most volatile — first)
- [ ] Live process list, open sockets, and mounts, via an **ephemeral debug container** (`kubectl debug`) attached to the pod's namespaces rather than by execing into the workload
- [ ] Container filesystem diff and writable layer
- [ ] Pod and node logs — `/var/log/pods/` on the node survives pod deletion until log rotation removes it, and is frequently the only surviving record
- [ ] Kubernetes objects as they exist right now (`kubectl get -o yaml` for the pod, its owners, service accounts, and RBAC bindings)
- [ ] Kubernetes API audit log entries for the affected principals
- [ ] CoreDNS query logs for the pod IP — usually the clearest view of C2 and exfiltration destinations, if query logging was enabled
- [ ] Cloud audit logs, flow logs, and load balancer logs for the window
- [ ] Node volume snapshot, stored in an isolated account
- [ ] Registry records: who pushed what, and when
- [ ] Hashes recorded for every artifact collected, with chain of custody if this may become legal

> `kubectl exec` into a compromised container modifies it and may alert the attacker. `kubectl debug` with an ephemeral container is the cloud-native equivalent of arriving with your own tools.

## 4. Eradication and recovery

- [ ] Root cause identified — the vulnerability or misconfiguration, not merely the malicious process
- [ ] Rebuild from a known-good image rather than cleaning a compromised container; **redeploy, do not repair**
- [ ] The vulnerability is fixed in source and in the base image before redeployment, or the workload comes back compromised
- [ ] All credentials in the blast radius are rotated, including ones only *potentially* exposed
- [ ] Persistence mechanisms are removed and verified gone
- [ ] Restoration is from a backup predating the compromise, verified clean
- [ ] Recovery is staged with heightened monitoring, and specific detections for reappearance of the same tradecraft
- [ ] Return-to-normal is a decision someone makes explicitly, with criteria, not a thing that drifts into being true

## 5. Specific playbooks

### Leaked cloud credential — the first fifteen minutes
- [ ] Revoke or rotate the credential **immediately**; do not wait for scope
- [ ] Kill active sessions issued from it
- [ ] Query audit logs for every action taken by that principal since first exposure
- [ ] Check for created persistence: new users, keys, roles, trust policies, OAuth apps
- [ ] Check for resource abuse: unexpected regions, new instances, crypto mining, data transfer volume
- [ ] Check for data access: bucket reads, database exports, snapshot copies to unknown accounts
- [ ] Only then clean the credential out of Git history (see [secrets-management.md](secrets-management.md#8-when-a-secret-leaks))

### Compromised CI/CD
- [ ] Treat **every** secret the pipeline could reach as compromised
- [ ] Freeze deployments; verify what has been released since the earliest possible compromise
- [ ] Check artifacts and images published in the window — signatures and provenance are how you answer "which builds are trustworthy?"
- [ ] Audit workflow file changes, new self-hosted runners, and repository/organisation setting changes
- [ ] Check for backdoors in the build config, not just in application source
- [ ] Rotate signing keys and re-sign if the signing identity was reachable

### Compromised dependency or action
- [ ] Determine exposure precisely from **SBOMs**: which builds, which versions, which environments — this is what the SBOM programme was for
- [ ] Assume any secret present during an affected build is compromised
- [ ] Pin or roll back, then verify the fixed version by digest
- [ ] Check for self-propagation — post-2025 worming supply chain attacks steal maintainer tokens and republish automatically; a repository you own may now be a source
- [ ] Notify downstream consumers if you publish anything

### Compromised AI agent or MCP server
- [ ] Revoke the agent's tool credentials and disable the tools, not just the session
- [ ] Review the full transcript: prompts, tool calls, parameters, and results
- [ ] **Clear persisted memory** — an injected instruction in long-term memory reinfects the next session
- [ ] Identify the injection source document and remove or quarantine it in the index
- [ ] Treat everything the agent could read as potentially exfiltrated, and everything it could write as potentially tampered
- [ ] See [ai-llm-security.md](ai-llm-security.md)

## 6. Afterwards

- [ ] Post-mortem is **blameless** and written within a week, while people still remember
- [ ] The timeline includes detection latency and containment latency, measured — not estimated
- [ ] Contributing factors are separated from root cause; there is rarely one cause
- [ ] Action items have owners, dates, and tickets, and are tracked to completion — **an untracked action item is a decision not to fix it**
- [ ] The fix addresses the **class** of issue, not the instance
- [ ] A detection is added for the technique used, and tested against a replay
- [ ] The relevant runbook is updated with what actually happened versus what it said would happen
- [ ] Findings are shared internally; the same misconfiguration usually exists in three other teams
- [ ] Legal, regulatory, and customer notification obligations are confirmed complete

---

## Metrics worth tracking

| Metric | What it tells you |
|---|---|
| Mean time to detect | Whether your logging and detection actually work |
| Mean time to contain | Whether your runbooks and permissions work |
| Dwell time | The number attackers care about |
| % incidents found internally | Found by a customer or a researcher is a different grade of failure |
| Action items closed on time | Whether post-mortems change anything |
| Runbooks rehearsed this quarter | The only leading indicator on this list |

Track the trend, not the absolute. An increase in detected incidents after deploying runtime detection is a functioning programme, not a worsening one.

---

## Where this fits

- Section 18 of the [roadmap](../README.md#18-incident-response-for-cloud-native) has the learning resources
- Runtime detection that produces the evidence: [`examples/falco/`](../examples/falco/custom-rules.yaml)
- Credential incidents: [secrets-management.md](secrets-management.md)
- Pipeline incidents: [pipeline-security.md](pipeline-security.md)
- Cluster containment primitives: [kubernetes-security.md](kubernetes-security.md)

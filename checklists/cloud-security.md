# Cloud Security Checklist

Cloud-provider agnostic where possible, with AWS/Azure/GCP specifics called out. Identity is the perimeter — weight your effort accordingly.

---

## Identity & access management

- [ ] Root / global-admin accounts have hardware MFA and are used for nothing routine
- [ ] SSO is the only human access path; no individual IAM users with passwords
- [ ] **No long-lived access keys** — humans use SSO, workloads use roles/managed identities, CI uses OIDC federation
- [ ] Any remaining static keys are inventoried with owners and rotation dates
- [ ] Least privilege enforced: no `*:*`, no `AdministratorAccess` attached to workloads
- [ ] Permission boundaries / SCPs / Azure Policy prevent privilege escalation even by admins
- [ ] Unused permissions are identified and removed (AWS IAM Access Analyzer unused access, Azure PIM, GCP Recommender)
- [ ] Cross-account/tenant trust relationships are inventoried and use `ExternalId` or equivalent
- [ ] Service accounts cannot impersonate each other unintentionally (GCP `iam.serviceAccounts.actAs` is a privilege escalation path)
- [ ] Break-glass accounts exist, are monitored, and alert on use

## Account / subscription structure

- [ ] Multi-account or multi-subscription structure separates prod, non-prod, and security tooling
- [ ] Organisation-level guardrails (SCPs / Azure Policy / GCP Org Policy) deny dangerous actions globally:
  - [ ] Cannot disable audit logging
  - [ ] Cannot disable encryption
  - [ ] Cannot make storage public
  - [ ] Cannot create resources in unapproved regions
  - [ ] Cannot delete security tooling
- [ ] Landing zone / baseline is codified in IaC and applied to every new account
- [ ] Billing anomaly alerts are enabled (often the first sign of cryptomining)

## Logging & monitoring

- [ ] Audit logs enabled in **all regions**: CloudTrail / Azure Activity + Diagnostic / GCP Cloud Audit Logs
- [ ] Logs delivered to a **separate, restricted security account** the workload identities cannot write to or delete
- [ ] Log integrity validation / immutability enabled (object lock, retention policy)
- [ ] Data-plane logging enabled for sensitive stores (S3 data events, storage account logs)
- [ ] Flow logs enabled for VPCs/VNets
- [ ] Threat detection service enabled: GuardDuty / Defender for Cloud / Security Command Center
- [ ] Alerts routed to somewhere a human actually reads
- [ ] Retention meets both regulatory requirement and realistic investigation window (90+ days minimum)

## Network

- [ ] No security group / NSG / firewall rule allows `0.0.0.0/0` to SSH (22), RDP (3389), or database ports
- [ ] Default VPC/VNet is unused or deleted
- [ ] Private subnets for anything not needing inbound internet
- [ ] Private endpoints / VPC endpoints for cloud service access instead of internet egress
- [ ] Egress filtering in place — outbound is not unrestricted
- [ ] WAF in front of public web applications
- [ ] DDoS protection considered for internet-facing services
- [ ] Public IP inventory is reviewed regularly

## Data

- [ ] Encryption at rest enabled everywhere, with customer-managed keys where required
- [ ] Encryption in transit enforced (TLS-only bucket policies, `supportsHttpsTrafficOnly`)
- [ ] **No public storage buckets/containers** unless deliberate, documented, and content-reviewed
- [ ] Public access is blocked at the account level, not just per-bucket
- [ ] Snapshots and backups are encrypted and not shared publicly
- [ ] Versioning and soft-delete enabled on critical stores
- [ ] Backups are tested by actually restoring them
- [ ] Data classification exists and drives the controls above
- [ ] Key rotation configured; key deletion protected

## Compute

- [ ] **IMDSv2 enforced** on all instances (this breaks the SSRF → credential theft chain), hop limit set to 1
- [ ] Instances built from hardened, patched golden images
- [ ] Patch management automated (SSM Patch Manager, Update Manager)
- [ ] No SSH keys distributed to instances — use SSM Session Manager / Bastion / IAP
- [ ] Serverless functions have narrowly scoped execution roles
- [ ] Function environment variables contain no secrets (use the secret manager)
- [ ] Managed database instances are not publicly accessible

## Posture & drift

- [ ] CSPM scanning runs continuously (Prowler, ScoutSuite, or a commercial CNAPP)
- [ ] Findings have owners and SLAs, not just a dashboard
- [ ] Infrastructure is managed by IaC; console changes are detected as drift
- [ ] Drift triggers an alert and an investigation, not just a re-apply
- [ ] Resource tagging is enforced (owner, environment, data classification, cost centre)
- [ ] Untagged/orphaned resources are cleaned up on a schedule

---

## Quick commands

```bash
# Full multi-service posture assessment
prowler aws --severity critical high --output-formats html json-ocsf
prowler azure --subscription-ids <id>
prowler gcp --project-ids <id>

# Alternative posture scan
scout aws --report-dir ./scoutsuite-report

# Query cloud config as SQL
steampipe query "select name, bucket_policy_is_public from aws_s3_bucket where bucket_policy_is_public"

# AWS: find unused IAM permissions and access keys older than 90 days
aws iam generate-credential-report && aws iam get-credential-report --query Content --output text | base64 -d

# AWS: check IMDSv2 enforcement
aws ec2 describe-instances --query \
  'Reservations[].Instances[?MetadataOptions.HttpTokens!=`required`].[InstanceId]' --output text

# Map IAM privilege escalation paths
pmapper --account <id> graph create
pmapper --account <id> analysis --output-type text

# Policy-driven remediation
custodian run --output-dir out policy.yml
```

## Further reading

- [AWS Well-Architected — Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
- [Microsoft Cloud Adoption Framework — Secure](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/secure/)
- [Google Cloud Architecture Framework — Security](https://cloud.google.com/architecture/framework/security)
- [CIS Benchmarks for AWS / Azure / GCP](https://www.cisecurity.org/cis-benchmarks)
- [Hacking the Cloud](https://hackingthe.cloud/) — the attacker's view of every control above

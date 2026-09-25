# GitHub Actions → AWS with OIDC

Replacing static cloud keys in CI with OIDC federation is the highest value-per-hour change in [the adoption order](../README.md#order-to-adopt-these). It deletes the most valuable long-lived secret most teams own — one that every workflow can read, that appears in `env` dumps, and that nobody has rotated since it was created.

It is also the change most often done wrong, in a way that is worse than what it replaced.

> **A trust policy with a wildcard on `sub` can let repositories you do not control assume your role.** Static keys at least required a leak. A bad trust policy is an open door with a modern-looking lock on it.

---

## The trust policy is the whole control

Everything else here is plumbing. Three misconfigurations account for essentially all real incidents:

| Trust policy says | Who can actually assume the role |
|---|---|
| `"StringLike": {"...:sub": "repo:my-org/*"}` | **Any repository in the org** — including one an attacker gets created, or a test repo with no branch protection |
| `"StringLike": {"...:sub": "repo:my-org/my-repo:*"}` | Any branch, any environment, any workflow of that repo — anyone who can push a branch |
| No `sub` condition at all | **Any GitHub Actions workflow on Earth.** This has been found in the wild |

The fix is not subtle: **`StringEquals`, against an enumerated list.** Wildcards only expand under `StringLike`, which is exactly why `StringLike` is where the accidents happen. A wildcard under `StringEquals` is compared literally and silently never matches — so if you "need" `StringLike`, you are about to widen the policy.

[`main.tf`](main.tf) has no wildcards, and [`variables.tf`](variables.tf) rejects one if you try.

---

## Usage

```hcl
module "github_oidc" {
  source = "./examples/terraform-oidc"

  github_owner    = "my-org"
  github_repo     = "my-service"

  # gh api repos/my-org/my-service --jq '{repo_id: .id, owner_id: .owner.id}'
  github_owner_id = 123456
  github_repo_id  = 789012

  role_name       = "github-my-service-deploy"

  # Enumerate. A protected GitHub Environment is the strongest option here,
  # because approvals and branch restrictions are enforced before the token
  # is issued at all.
  allowed_claims = ["environment:production"]

  permissions_boundary_arn = aws_iam_policy.ci_boundary.arn
  ecr_repository_arns      = [aws_ecr_repository.app.arn]
}
```

In the workflow — note `id-token: write`, without which no token is minted, and no secrets at all:

```yaml
permissions:
  contents: read
  id-token: write        # required to request the OIDC token

jobs:
  deploy:
    environment: production          # must match the claim you trusted
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1

      - uses: aws-actions/configure-aws-credentials@e6de054238d6b7531b4efff3b6587d9aade6a06c # v6.2.3
        with:
          role-to-assume: arn:aws:iam::111122223333:role/github-my-service-deploy
          aws-region: eu-west-1
          role-session-name: deploy-${{ github.run_id }}
```

Resolve your own action SHAs before copying — the pins above go stale, and [`../renovate/renovate.json5`](../renovate/renovate.json5) is how you keep them fresh.

---

## Immutable subject claims — the July 2026 change

GitHub changed the default subject claim format. The old one used mutable names:

```
repo:my-org/my-repo:ref:refs/heads/main
```

The new one appends numeric owner and repository IDs after an `@`:

```
repo:my-org@123456/my-repo@789012:ref:refs/heads/main
```

The reason is that OIDC subjects are supposed to be permanently unique. Under the old format, deleting an organisation and letting someone else register the name meant they inherited every trust policy that referenced it.

**What applies to you:**

| Repository | Format |
|---|---|
| Created after 15 July 2026 | New format, automatically |
| Renamed or transferred after 15 July 2026 | New format, automatically |
| Existing, untouched | Old format until you opt in |
| GitHub Enterprise Server | Unaffected |

**Migrating safely:** keep `trust_legacy_subject_format = true` so the policy trusts both, opt the repository in, confirm a deploy works, then set it to `false`. Leaving both trusted forever preserves the vulnerability the change was made to fix.

The failure mode is loud rather than dangerous — `AssumeRoleWithWebIdentity` returns access denied and the deploy fails — which makes this a good change to make deliberately rather than discover on a Friday.

---

## Tighter conditions than `sub`

Since February 2026, AWS STS supports GitHub-specific OIDC claims as first-class condition keys, which express intent far more clearly than packing everything into one subject string:

| Condition key | Use it to |
|---|---|
| `job_workflow_ref` | Pin the exact **workflow file** allowed to assume the role |
| `repository_id` | Survive repository renames without editing the policy |
| `environment` | Require a protected environment |
| `actor_id` | Restrict to specific users, by immutable ID |

`job_workflow_ref` is the most useful of them. It means only your reviewed, centrally maintained reusable workflow can assume the role — copying the deploy steps into a new workflow file no longer inherits the credentials. See the commented `dynamic "condition"` block in [`main.tf`](main.tf).

These keys work in trust policies and resource control policies, not in identity-based policies after assumption.

---

## Also worth doing

- [ ] **One role per repository per environment.** A shared `github-actions-deploy` role recreates the shared-credential problem you just removed
- [ ] **Permissions boundary** on every pipeline role, so a future PR cannot attach `AdministratorAccess`
- [ ] **Least privilege from access-denied errors or IAM Access Analyzer**, not by starting at PowerUser and hoping to trim later
- [ ] **Alarm on `AssumeRoleWithWebIdentity` failures** — they are the signal of a misconfigured *or* attempted-abuse trust policy
- [ ] **Audit existing roles** for `StringLike` with `*` on `sub`, and for roles with no `sub` condition at all:

```bash
aws iam list-roles --query 'Roles[?AssumeRolePolicyDocument].[RoleName,AssumeRolePolicyDocument]' --output json \
  | grep -B5 -A15 'token.actions.githubusercontent.com'
```

- [ ] **Delete the static keys** once OIDC works. The migration is not finished while the old credential still exists — and an unused key is a key nobody is watching

---

## See also

- [`checklists/secrets-management.md`](../../checklists/secrets-management.md) — the wider "no long-lived secrets" programme
- [`checklists/pipeline-security.md`](../../checklists/pipeline-security.md) — the rest of the CI hardening
- [`../github-actions/devsecops-pipeline.yml`](../github-actions/devsecops-pipeline.yml) — the pipeline this role serves
- [GitHub: security hardening with OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect) · [aws-actions/configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials)

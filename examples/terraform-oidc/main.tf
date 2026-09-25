# ---------------------------------------------------------------------------
# GitHub Actions -> AWS via OIDC. No static access keys.
#
# Step 5 of the adoption order in ../README.md, and the change that removes
# the single most valuable long-lived secret most teams own: a set of AWS keys
# sitting in CI variables, readable by every workflow, rotated never.
#
# The security of this pattern lives entirely in the trust policy below. A
# sloppy one is *worse* than static keys, because it can let any repository on
# GitHub — not just yours — assume the role, and it looks modern while doing
# it. Read the condition block before you copy this.
#
#   terraform init && terraform plan
#   checkov -d .          # or: trivy config .
# ---------------------------------------------------------------------------

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.40"
    }
  }
}

# ---------------------------------------------------------------------------
# The OIDC provider. One per AWS account — if another stack already created
# it, set create_oidc_provider = false and pass the existing ARN instead.
#
# No thumbprint_list: since July 2023 AWS validates GitHub's OIDC endpoint
# against its own trusted CA library and ignores any thumbprint you configure.
# Configurations that still hardcode a thumbprint are carrying a value that
# does nothing, and that people waste time "rotating".
# ---------------------------------------------------------------------------
resource "aws_iam_openid_connect_provider" "github" {
  count = var.create_oidc_provider ? 1 : 0

  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
  tags           = var.tags
}

locals {
  oidc_provider_arn = var.create_oidc_provider ? aws_iam_openid_connect_provider.github[0].arn : var.existing_oidc_provider_arn

  # -------------------------------------------------------------------------
  # Subject claim formats.
  #
  # GitHub is migrating to immutable subject claims. The old format used
  # mutable names:
  #
  #   repo:my-org/my-repo:ref:refs/heads/main
  #
  # The new one appends numeric owner and repository IDs after an "@", so a
  # recycled org or repo name cannot inherit an existing trust relationship:
  #
  #   repo:my-org@123456/my-repo@789012:ref:refs/heads/main
  #
  # Repositories created — or renamed or transferred — after 15 July 2026 use
  # the new format automatically. Existing repositories keep the old one until
  # they opt in. GitHub Enterprise Server is not affected.
  #
  # Trust BOTH during migration, verify the new one works, then delete the
  # legacy entry. Getting this wrong fails closed: deploys break with an
  # AssumeRoleWithWebIdentity access denied, which is annoying but safe.
  # -------------------------------------------------------------------------
  legacy_prefix = "repo:${var.github_owner}/${var.github_repo}"

  immutable_prefix = var.github_owner_id != null && var.github_repo_id != null ? "repo:${var.github_owner}@${var.github_owner_id}/${var.github_repo}@${var.github_repo_id}" : null

  subject_prefixes = compact([
    var.trust_legacy_subject_format ? local.legacy_prefix : null,
    local.immutable_prefix,
  ])

  # Every allowed (prefix x claim) pair, enumerated explicitly. Enumeration is
  # the point — see the comment on the condition block below.
  allowed_subjects = flatten([
    for prefix in local.subject_prefixes : [
      for claim in var.allowed_claims : "${prefix}:${claim}"
    ]
  ])
}

# ---------------------------------------------------------------------------
# The trust policy. This is the whole control.
#
# Two conditions, both mandatory:
#
#  1. aud = sts.amazonaws.com
#     Without it the role accepts tokens minted for a different audience.
#
#  2. sub matched with StringEquals against an explicit list
#     StringEquals, not StringLike. Wildcards only expand under StringLike,
#     and every serious misconfiguration of this pattern is a wildcard:
#
#       "repo:my-org/*"        -> ANY repo in the org, including one an
#                                 attacker creates or a fork-turned-repo
#       "repo:my-org/my-repo:*" -> any branch, any PR, any environment of that
#                                 repo. A PR from a fork does not get this,
#                                 but any branch a contributor can push does.
#       sub condition missing  -> any GitHub Actions workflow on Earth
#
#     That last case has been found in the wild. There is no wildcard in this
#     file on purpose, and the variable validation rejects one.
# ---------------------------------------------------------------------------
data "aws_iam_policy_document" "trust" {
  statement {
    sid     = "GitHubActionsOIDC"
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [local.oidc_provider_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = local.allowed_subjects
    }

    # -----------------------------------------------------------------------
    # Optional extra hardening, available since AWS STS added provider-specific
    # OIDC claim validation (February 2026). These keys let you express
    # "only this reusable workflow, only from this repository ID" without
    # encoding everything into one sub string:
    #
    #   token.actions.githubusercontent.com:repository_id
    #   token.actions.githubusercontent.com:job_workflow_ref
    #   token.actions.githubusercontent.com:environment
    #   token.actions.githubusercontent.com:actor_id
    #
    # job_workflow_ref is the strongest of them: it pins the *workflow file*
    # that may assume this role, so a developer cannot copy the deploy steps
    # into an unreviewed workflow and get the same credentials.
    #
    # dynamic "condition" {
    #   for_each = var.required_job_workflow_ref != null ? [1] : []
    #   content {
    #     test     = "StringEquals"
    #     variable = "token.actions.githubusercontent.com:job_workflow_ref"
    #     values   = [var.required_job_workflow_ref]
    #   }
    # }
    # -----------------------------------------------------------------------
  }
}

resource "aws_iam_role" "github_actions" {
  name        = var.role_name
  description = "Assumed by GitHub Actions in ${var.github_owner}/${var.github_repo} via OIDC"

  assume_role_policy = data.aws_iam_policy_document.trust.json

  # An hour is plenty for a deploy. The session is the credential — a shorter
  # maximum limits how long a leaked one is useful, and jobs that need longer
  # than this usually need to be split rather than granted more time.
  max_session_duration = var.max_session_duration

  # A permissions boundary caps what this role can ever be granted, including
  # by a future well-meaning pull request that attaches AdministratorAccess.
  # Strongly recommended for any role a pipeline can assume.
  permissions_boundary = var.permissions_boundary_arn

  tags = var.tags
}

# ---------------------------------------------------------------------------
# Least-privilege permissions.
#
# Replace this with what your pipeline actually needs. The common failure here
# is attaching PowerUserAccess "to get the deploy working" and never revisiting
# it — at which point the OIDC migration has removed a static key and kept the
# blast radius, which is half a win at best.
#
# Derive the real policy from access-denied errors or IAM Access Analyzer's
# policy generation, rather than guessing upward from admin.
# ---------------------------------------------------------------------------
data "aws_iam_policy_document" "deploy" {
  statement {
    sid    = "PushImagesToECR"
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
    ]
    resources = var.ecr_repository_arns
  }

  statement {
    sid       = "GetECRAuthToken"
    effect    = "Allow"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"] # this action does not support resource-level permissions
  }
}

resource "aws_iam_role_policy" "deploy" {
  name   = "${var.role_name}-deploy"
  role   = aws_iam_role.github_actions.id
  policy = data.aws_iam_policy_document.deploy.json
}

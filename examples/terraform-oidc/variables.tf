variable "github_owner" {
  description = "GitHub organisation or user that owns the repository."
  type        = string
}

variable "github_repo" {
  description = "Repository name, without the owner prefix."
  type        = string
}

# ---------------------------------------------------------------------------
# Immutable identifiers. Find them with:
#
#   gh api repos/OWNER/REPO --jq '{repo_id: .id, owner_id: .owner.id}'
#
# Required for repositories created, renamed, or transferred after
# 15 July 2026, which use the immutable subject claim format by default.
# ---------------------------------------------------------------------------
variable "github_owner_id" {
  description = "Numeric GitHub owner ID, for the immutable subject claim format."
  type        = number
  default     = null
}

variable "github_repo_id" {
  description = "Numeric GitHub repository ID, for the immutable subject claim format."
  type        = number
  default     = null
}

variable "trust_legacy_subject_format" {
  description = <<-EOT
    Whether to also trust the pre-2026 name-based subject claim format.

    Keep this true while migrating, then set it to false. Leaving it enabled
    after migration means a recycled org or repository name could inherit this
    trust relationship — which is the exact problem the immutable format was
    introduced to solve.
  EOT
  type        = bool
  default     = true
}

# ---------------------------------------------------------------------------
# What may assume the role, expressed as the part of the subject claim after
# the repository. Enumerate it. Do not wildcard it.
#
# Common values:
#   "environment:production"     a job using a protected GitHub Environment
#                                — the strongest of these, because approval
#                                gates and branch restrictions are enforced by
#                                GitHub before the token is even issued
#   "ref:refs/heads/main"        a job on the default branch
#   "ref:refs/tags/v*"           NOT valid here: StringEquals does not expand
#                                wildcards, and StringLike would open this up
#   "pull_request"               PR-triggered jobs — grant read-only roles only
# ---------------------------------------------------------------------------
variable "allowed_claims" {
  description = "Exact subject-claim suffixes permitted to assume the role."
  type        = list(string)
  default     = ["environment:production"]

  validation {
    condition     = length(var.allowed_claims) > 0
    error_message = "Specify at least one claim; an empty list would produce a trust policy that nothing can use."
  }

  validation {
    condition     = alltrue([for c in var.allowed_claims : !can(regex("\\*", c))])
    error_message = "Wildcards are not permitted. They do nothing under StringEquals and are dangerous under StringLike — enumerate each branch or environment instead."
  }
}

variable "role_name" {
  description = "Name of the IAM role GitHub Actions will assume."
  type        = string
}

variable "create_oidc_provider" {
  description = "Create the GitHub OIDC provider. Set false if the account already has one — there can only be one per account."
  type        = bool
  default     = true
}

variable "existing_oidc_provider_arn" {
  description = "ARN of an existing GitHub OIDC provider, used when create_oidc_provider is false."
  type        = string
  default     = null
}

variable "permissions_boundary_arn" {
  description = "Permissions boundary capping what this role can ever be granted. Strongly recommended for pipeline roles."
  type        = string
  default     = null
}

variable "max_session_duration" {
  description = "Maximum session length in seconds. Keep it close to how long a deploy actually takes."
  type        = number
  default     = 3600

  validation {
    condition     = var.max_session_duration <= 3600
    error_message = "Keep pipeline sessions at one hour or less; a longer session is a longer-lived credential for no benefit."
  }
}

variable "required_job_workflow_ref" {
  description = <<-EOT
    Optional. Pins the exact workflow file permitted to assume this role, e.g.
    "my-org/shared-workflows/.github/workflows/deploy.yml@refs/heads/main".

    Uses the job_workflow_ref condition key, available since AWS STS added
    provider-specific OIDC claim validation in February 2026. Uncomment the
    dynamic condition block in main.tf to use it.
  EOT
  type        = string
  default     = null
}

variable "ecr_repository_arns" {
  description = "ECR repositories this pipeline may push to. Replace with your own permissions."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags applied to created resources."
  type        = map(string)
  default     = {}
}

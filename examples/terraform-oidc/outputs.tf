output "role_arn" {
  description = "Pass this to aws-actions/configure-aws-credentials as role-to-assume."
  value       = aws_iam_role.github_actions.arn
}

output "oidc_provider_arn" {
  description = "ARN of the GitHub OIDC provider in use."
  value       = local.oidc_provider_arn
}

# Print the exact subjects this role trusts. Diff this output in code review —
# it is the shortest possible summary of who can assume the role, and it is
# far easier to check than reading the rendered policy JSON.
output "trusted_subjects" {
  description = "Exact subject claims permitted to assume the role."
  value       = local.allowed_subjects
}

# ---------------------------------------------------------------------------
# OPA / Rego policies for Terraform plans
#
# Scanning Terraform SOURCE misses everything that only appears after
# variables, locals, and modules resolve. Scan the PLAN instead:
#
#   terraform plan -out=tf.plan
#   terraform show -json tf.plan > tf.json
#   conftest test --policy . tf.json
#
# Or with OPA directly:
#   opa eval --format pretty --data terraform.rego --input tf.json \
#     "data.terraform.security.deny"
# ---------------------------------------------------------------------------
package terraform.security

import rego.v1

# Every resource the plan will create or update.
resources contains resource if {
	some change in input.resource_changes
	change.change.actions[_] in ["create", "update"]
	resource := {
		"type": change.type,
		"name": change.name,
		"address": change.address,
		"values": change.change.after,
	}
}

# ---------------------------------------------------------------------------
# Storage must never be public
# ---------------------------------------------------------------------------

deny contains msg if {
	some r in resources
	r.type == "aws_s3_bucket_public_access_block"
	not all_public_access_blocked(r.values)
	msg := sprintf("%s: all four S3 public access block settings must be true", [r.address])
}

all_public_access_blocked(v) if {
	v.block_public_acls == true
	v.block_public_policy == true
	v.ignore_public_acls == true
	v.restrict_public_buckets == true
}

deny contains msg if {
	some r in resources
	r.type == "aws_s3_bucket_acl"
	r.values.acl in ["public-read", "public-read-write"]
	msg := sprintf("%s: bucket ACL '%s' makes data publicly readable", [r.address, r.values.acl])
}

deny contains msg if {
	some r in resources
	r.type == "azurerm_storage_account"
	r.values.allow_nested_items_to_be_public == true
	msg := sprintf("%s: storage account allows public blobs", [r.address])
}

# ---------------------------------------------------------------------------
# Encryption at rest and in transit
# ---------------------------------------------------------------------------

deny contains msg if {
	some r in resources
	r.type in {"aws_ebs_volume", "aws_rds_cluster", "aws_db_instance"}
	r.values.storage_encrypted == false
	msg := sprintf("%s: storage must be encrypted at rest", [r.address])
}

deny contains msg if {
	some r in resources
	r.type == "azurerm_storage_account"
	r.values.enable_https_traffic_only == false
	msg := sprintf("%s: HTTPS-only traffic must be enforced", [r.address])
}

# ---------------------------------------------------------------------------
# Network exposure — the rule that catches the most real incidents
# ---------------------------------------------------------------------------

sensitive_ports := {22, 3389, 3306, 5432, 6379, 27017, 9200, 2379}

deny contains msg if {
	some r in resources
	r.type == "aws_security_group_rule"
	r.values.type == "ingress"
	"0.0.0.0/0" in r.values.cidr_blocks
	some port in sensitive_ports
	r.values.from_port <= port
	r.values.to_port >= port
	msg := sprintf(
		"%s: port %d is open to 0.0.0.0/0 — use a bastion, VPN, or SSM instead",
		[r.address, port],
	)
}

deny contains msg if {
	some r in resources
	r.type in {"aws_db_instance", "aws_rds_cluster_instance"}
	r.values.publicly_accessible == true
	msg := sprintf("%s: database must not be publicly accessible", [r.address])
}

# ---------------------------------------------------------------------------
# IAM least privilege
# ---------------------------------------------------------------------------

deny contains msg if {
	some r in resources
	r.type == "aws_iam_policy"
	policy := json.unmarshal(r.values.policy)
	some statement in policy.Statement
	statement.Effect == "Allow"
	wildcard_action(statement)
	wildcard_resource(statement)
	msg := sprintf("%s: IAM policy grants Action:* on Resource:* ", [r.address])
}

wildcard_action(statement) if "*" in as_array(statement.Action)

wildcard_resource(statement) if "*" in as_array(statement.Resource)

as_array(x) := x if is_array(x)

as_array(x) := [x] if is_string(x)

# ---------------------------------------------------------------------------
# EC2 instance metadata — breaks the SSRF -> credential theft chain
# ---------------------------------------------------------------------------

deny contains msg if {
	some r in resources
	r.type in {"aws_instance", "aws_launch_template"}
	not imdsv2_required(r.values)
	msg := sprintf("%s: IMDSv2 must be required (http_tokens = \"required\")", [r.address])
}

imdsv2_required(v) if v.metadata_options[_].http_tokens == "required"

# ---------------------------------------------------------------------------
# Audit logging must not be disabled
# ---------------------------------------------------------------------------

deny contains msg if {
	some r in resources
	r.type == "aws_cloudtrail"
	r.values.enable_log_file_validation == false
	msg := sprintf("%s: CloudTrail log file validation must be enabled", [r.address])
}

deny contains msg if {
	some r in resources
	r.type == "aws_cloudtrail"
	r.values.is_multi_region_trail == false
	msg := sprintf("%s: CloudTrail must cover all regions", [r.address])
}

# ---------------------------------------------------------------------------
# Warnings — surfaced but non-blocking
# ---------------------------------------------------------------------------

required_tags := {"Owner", "Environment", "DataClassification"}

warn contains msg if {
	some r in resources
	startswith(r.type, "aws_")
	r.values.tags
	some tag in required_tags
	not r.values.tags[tag]
	msg := sprintf("%s: missing required tag '%s'", [r.address, tag])
}

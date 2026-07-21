package main

import rego.v1

# CSPM gate (fallback / local).
# Primary CSPM is Trivy (`trivy config`) in CI. These Rego rules mirror the
# headline misconfigurations so the gate is enforceable locally and offline,
# and so the same findings appear whether or not the Trivy bundle is available.

s3_buckets[name] := res if {
	some name, res in input.Resources
	res.Type == "AWS::S3::Bucket"
}

# Public S3 via canned ACL.
deny contains msg if {
	some name, res in s3_buckets
	acl := res.Properties.AccessControl
	acl in {"PublicRead", "PublicReadWrite", "AuthenticatedRead"}
	msg := sprintf("CSPM: S3 bucket '%s' uses public AccessControl '%s'", [name, acl])
}

# S3 without full public-access block.
deny contains msg if {
	some name, res in s3_buckets
	not fully_blocked(res)
	msg := sprintf("CSPM: S3 bucket '%s' is missing a complete PublicAccessBlockConfiguration", [name])
}

fully_blocked(res) if {
	pab := res.Properties.PublicAccessBlockConfiguration
	pab.BlockPublicAcls == true
	pab.BlockPublicPolicy == true
	pab.IgnorePublicAcls == true
	pab.RestrictPublicBuckets == true
}

# S3 without server-side encryption.
deny contains msg if {
	some name, res in s3_buckets
	not res.Properties.BucketEncryption
	msg := sprintf("CSPM: S3 bucket '%s' has no BucketEncryption", [name])
}

# Security group allowing SSH from the world.
deny contains msg if {
	some name, res in input.Resources
	res.Type == "AWS::EC2::SecurityGroup"
	some rule in res.Properties.SecurityGroupIngress
	rule.FromPort == 22
	rule.CidrIp == "0.0.0.0/0"
	msg := sprintf("CSPM: SecurityGroup '%s' allows SSH (22) from 0.0.0.0/0", [name])
}

# IAM policy with wildcard action + resource.
deny contains msg if {
	some name, res in input.Resources
	res.Type in {"AWS::IAM::Role", "AWS::IAM::Policy", "AWS::IAM::ManagedPolicy"}
	stmt := policy_statements(res)[_]
	has_wildcard(stmt.Action)
	has_wildcard(stmt.Resource)
	stmt.Effect == "Allow"
	msg := sprintf("CSPM: IAM resource '%s' grants Action:* on Resource:* (star-star)", [name])
}

policy_statements(res) := s if {
	res.Type == "AWS::IAM::Role"
	s := res.Properties.Policies[_].PolicyDocument.Statement
}

policy_statements(res) := res.Properties.PolicyDocument.Statement if {
	res.Type in {"AWS::IAM::Policy", "AWS::IAM::ManagedPolicy"}
}

has_wildcard(v) if v == "*"

has_wildcard(v) if {
	is_array(v)
	v[_] == "*"
}

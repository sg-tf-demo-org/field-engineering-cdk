package main

import rego.v1

# Mandatory-tags gate.
# Every taggable resource in a CloudFormation template (including CFN synthesized
# from CDK) must carry the org-required tag keys. Fail-closed.

required_tags := {"Owner", "CostCenter", "Environment"}

# Resource types we require tags on. Extend as needed.
taggable := {
	"AWS::S3::Bucket",
	"AWS::SQS::Queue",
	"AWS::SNS::Topic",
	"AWS::Lambda::Function",
	"AWS::DynamoDB::Table",
	"AWS::EC2::Instance",
	"AWS::EC2::SecurityGroup",
	"AWS::EC2::VPC",
	"AWS::IAM::Role",
	"AWS::KMS::Key",
	"AWS::RDS::DBInstance",
}

# Collect the tag keys present on a resource (CFN Tags are a list of {Key,Value}).
tag_keys(res) := {k | some t in res.Properties.Tags; k := t.Key}

deny contains msg if {
	some name, res in input.Resources
	taggable[res.Type]
	provided := tag_keys(res)
	missing := required_tags - provided
	count(missing) > 0
	msg := sprintf("MANDATORY-TAGS: resource '%s' (%s) is missing required tags: %v", [name, res.Type, missing])
}

# A resource with no Tags property at all is also a violation.
deny contains msg if {
	some name, res in input.Resources
	taggable[res.Type]
	not res.Properties.Tags
	msg := sprintf("MANDATORY-TAGS: resource '%s' (%s) has no Tags block; required: %v", [name, res.Type, required_tags])
}

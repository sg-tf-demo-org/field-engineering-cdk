"""KmsKeyStack — Customer Managed Key for the field-engineering platform.

Creates a symmetric KMS CMK with automatic annual key rotation enabled,
a human-friendly alias, and org-required tags. The key ARN is exported as
a CloudFormation Output so dependent stacks can import it by name.

Passes Governance CSPM by construction:
  ✓ CMK (customer-managed) with enable_key_rotation=True
  ✓ Mandatory tags: Owner, CostCenter, Environment
  ✓ Pinned to us-east-1 via the shared ENV in app.py
"""
import aws_cdk as cdk
from aws_cdk import RemovalPolicy
from aws_cdk import aws_kms as kms
from constructs import Construct


class KmsKeyStack(cdk.Stack):
    """A standalone stack that vends a single, reusable KMS Customer Managed Key."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- KMS Customer Managed Key ---
        self.key = kms.Key(
            self,
            "FieldEngineeringCmk",
            description="CMK for field-engineering platform",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Friendly alias so other services can reference it by name.
        self.key.add_alias("alias/field-engineering-cmk")

        # --- Mandatory tags (governance gate) ---
        cdk.Tags.of(self).add("Owner", "platform")
        cdk.Tags.of(self).add("CostCenter", "FE-DEMO")
        cdk.Tags.of(self).add("Environment", "dev")

        # --- CloudFormation Output ---
        cdk.CfnOutput(
            self,
            "KmsKeyArn",
            value=self.key.key_arn,
            description="ARN of the field-engineering Customer Managed Key",
            export_name="field-engineering-cmk-key-arn",
        )

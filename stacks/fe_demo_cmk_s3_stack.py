"""FeDemoCmkS3Stack — CMK-encrypted S3 assets bucket for fe-demo.

Creates a dedicated AWS KMS customer-managed key (CMK) with key rotation
enabled and passes it to the governance-compliant SecureBucket construct.
All resources are tagged with the org-required mandatory tags and locked
to us-east-1 via the app-level environment binding.
"""
import aws_cdk as cdk
from aws_cdk import RemovalPolicy, Stack, Tags
from aws_cdk import aws_kms as kms
from constructs import Construct

from cdk_constructs import SecureBucket


class FeDemoCmkS3Stack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)

        # Customer-managed KMS key with rotation enabled (governance gate: CMK + rotation).
        self.cmk = kms.Key(
            self,
            "AssetsBucketKey",
            description="CMK for fe-demo S3 assets bucket",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY,
        )
        Tags.of(self.cmk).add("Owner", "platform")
        Tags.of(self.cmk).add("CostCenter", "FE-DEMO")
        Tags.of(self.cmk).add("Environment", "dev")

        # SecureBucket bakes in: KMS encryption, BLOCK_ALL public access,
        # enforce_ssl=True, versioned=True — governance-compliant by construction.
        secure = SecureBucket(
            self,
            "AssetsBucket",
            encryption_key=self.cmk,
            owner="platform",
            cost_center="FE-DEMO",
            environment="dev",
        )
        self.bucket = secure.bucket

        # Stack-level mandatory tags (propagate to all taggable resources).
        Tags.of(self).add("Owner", "platform")
        Tags.of(self).add("CostCenter", "FE-DEMO")
        Tags.of(self).add("Environment", "dev")

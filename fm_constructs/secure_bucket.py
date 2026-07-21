"""SecureBucket — FM-CDK building block.

A governance-compliant S3 bucket: customer-managed KMS encryption, all public
access blocked, SSL enforced, versioned, and org-required tags. Passes Governance
CSPM by construction. Use this instead of raw s3.Bucket.
"""
from aws_cdk import RemovalPolicy, Tags
from aws_cdk import aws_kms as kms
from aws_cdk import aws_s3 as s3
from constructs import Construct


class SecureBucket(Construct):
    def __init__(self, scope: Construct, cid: str, *, encryption_key: kms.IKey | None = None,
                 owner: str = "platform", cost_center: str = "FE-DEMO",
                 environment: str = "dev", **kwargs):
        super().__init__(scope, cid)

        self.key = encryption_key or kms.Key(
            self, "Key", enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.bucket = s3.Bucket(
            self, "Bucket",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.key,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            versioned=True,
            **kwargs,
        )

        for res in (self.bucket, self.key):
            Tags.of(res).add("Owner", owner)
            Tags.of(res).add("CostCenter", cost_center)
            Tags.of(res).add("Environment", environment)

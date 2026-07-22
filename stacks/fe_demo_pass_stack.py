"""fe-demo-pass CDK stack — governance-compliant demo.

Uses SecureBucket (CMK-encrypted, enforce_ssl=True, Block Public Access)
and inherits app-wide mandatory tags (Owner, CostCenter, Environment)
pinned to us-east-1.
"""
import aws_cdk as cdk
from constructs import Construct

from cdk_constructs.secure_bucket import SecureBucket


class FeDemoPassStack(cdk.Stack):
    """A governance-passing demo stack with a CMK-encrypted private S3 bucket."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # SecureBucket: CMK-encrypted (aws:kms), Block Public Access,
        # enforce_ssl=True — compliant by construction.
        self.bucket = SecureBucket(self, "AssetsBucket")

        # Stack-level tags (supplement the app-wide tags already applied in app.py).
        for key, value in {
            "Owner": "platform",
            "CostCenter": "FE-DEMO",
            "Environment": "dev",
        }.items():
            cdk.Tags.of(self).add(key, value)

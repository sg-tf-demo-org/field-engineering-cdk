"""DemoPassStack — fe-demo-pass governance-compliant demo stack.

A minimal stack that provisions a CMK-encrypted, private S3 bucket using the
SecureBucket building block. Passes Governance CSPM by construction.
"""
import aws_cdk as cdk
from constructs import Construct

from cdk_constructs.secure_bucket import SecureBucket


class DemoPassStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.bucket = SecureBucket(
            self,
            "DemoPassBucket",
            owner="platform",
            cost_center="FE-DEMO",
            environment="dev",
        )

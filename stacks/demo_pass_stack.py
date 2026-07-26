"""DemoPassStack — fe-demo-pass CDK stack.

Provisions a CMK-encrypted S3 assets bucket (SecureBucket) tagged for the
platform team. Passes Governance CSPM by construction (CMK, private, tagged,
us-east-1).
"""
import aws_cdk as cdk
from constructs import Construct

from cdk_constructs import SecureBucket


class DemoPassStack(cdk.Stack):
    """Stack that provisions a CMK-encrypted S3 assets bucket for fe-demo-pass."""

    def __init__(self, scope: Construct, stack_id: str, **kwargs) -> None:
        super().__init__(scope, stack_id, **kwargs)

        self._assets = SecureBucket(
            self, "DemoPassAssets",
            owner="platform",
            cost_center="FE-DEMO",
            environment="dev",
        )

    @property
    def bucket(self):
        return self._assets.bucket

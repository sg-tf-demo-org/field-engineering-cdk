"""DemoPassStack — CMK-encrypted S3 bucket stack for the fe-demo-pass demo.

Uses the SecureBucket building block: customer-managed KMS key, all public
access blocked, SSL enforced, versioned. Tagged Owner=platform,
CostCenter=FE-DEMO, Environment=dev. Passes Governance CSPM by construction.
"""
from aws_cdk import Stack
from constructs import Construct

from cdk_constructs import SecureBucket


class DemoPassStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)

        demo = SecureBucket(
            self,
            "DemoBucket",
            owner="platform",
            cost_center="FE-DEMO",
            environment="dev",
        )
        self.bucket = demo.bucket

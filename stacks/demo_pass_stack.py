"""DemoPassStack — compliant path using cdk_constructs.SecureBucket."""
from aws_cdk import Stack
from constructs import Construct

from cdk_constructs import SecureBucket


class DemoPassStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)
        SecureBucket(
            self,
            "DemoPassAssets",
            owner="platform",
            cost_center="FE-DEMO",
            environment="dev",
        )

"""FeDemoPassStack — compliant SecureBucket assets."""
from aws_cdk import Stack
from constructs import Construct

from cdk_constructs import SecureBucket


class FeDemoPassStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)
        SecureBucket(
            self,
            "FeDemoPassAssets",
            owner="platform",
            cost_center="FE-DEMO",
            environment="dev",
        )

"""DemoPassStack — fe-demo-pass governance-compliant demo stack.

A standalone stack that provisions a CMK-encrypted, versioned, SSL-enforced
S3 bucket using the SecureBucket building block. Passes Governance CSPM by
construction (CMK + tags + region us-east-1).
"""
from aws_cdk import Stack
from constructs import Construct
from cdk_constructs import SecureBucket


class DemoPassStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)

        demo = SecureBucket(
            self, "DemoBucket",
            owner="platform",
            cost_center="FE-DEMO",
            environment="dev",
        )
        self.bucket = demo.bucket

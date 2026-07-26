"""DemoPassStack — fe-demo-pass CDK stack.

Provisions a CMK-encrypted S3 bucket (SecureBucket) and a CMK-encrypted
DynamoDB table (SecureTable) tagged for the platform team.
Passes Governance CSPM by construction (CMK, private, tagged, us-east-1).
"""
import aws_cdk as cdk
from constructs import Construct
from cdk_constructs import SecureBucket, SecureTable


class DemoPassStack(cdk.Stack):
    """Stack that provisions CMK-encrypted storage resources for the fe-demo-pass demo."""

    def __init__(self, scope: Construct, stack_id: str, **kwargs) -> None:
        super().__init__(scope, stack_id, **kwargs)

        self._bucket = SecureBucket(
            self, "DemoPassBucket",
            owner="platform",
            cost_center="FE-DEMO",
            environment="dev",
        )

        self._table = SecureTable(
            self, "DemoPassTable",
            owner="platform",
            cost_center="FE-DEMO",
            environment="dev",
        )

    @property
    def bucket(self):
        return self._bucket

    @property
    def table(self):
        return self._table

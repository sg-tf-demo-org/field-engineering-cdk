"""fe-demo-pass — governed demo stack.

CMK-encrypted S3 bucket + DynamoDB table, tagged and pinned to us-east-1.
Assembled from pre-built governance-compliant constructs so the synthesized
CloudFormation passes the Governance gate by construction.
"""
import aws_cdk as cdk
from constructs import Construct
from cdk_constructs import SecureBucket, SecureTable


class FeDemoPassStack(cdk.Stack):
    """Governed demo stack: CMK S3 bucket + CMK DynamoDB table."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # CMK-encrypted S3 bucket (private, versioned, access-logged).
        self.bucket = SecureBucket(self, "DemoBucket")

        # CMK-encrypted DynamoDB table (PAY_PER_REQUEST, PITR enabled).
        self.table = SecureTable(self, "DemoTable")

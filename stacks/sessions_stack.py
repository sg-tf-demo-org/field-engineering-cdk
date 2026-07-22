"""SessionsStack — DynamoDB Sessions table via SecureTable construct.

Provides a governance-compliant DynamoDB table (customer-managed KMS,
PITR enabled, on-demand billing) keyed on session_id / created_at.
"""
from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_dynamodb as dynamodb
from constructs import Construct

from cdk_constructs import SecureTable


class SessionsStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)

        sessions = SecureTable(
            self,
            "Sessions",
            partition_key="session_id",
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING,
            ),
            removal_policy=RemovalPolicy.DESTROY,
            owner="platform",
            cost_center="FE-DEMO",
            environment="dev",
        )
        self.table = sessions.table

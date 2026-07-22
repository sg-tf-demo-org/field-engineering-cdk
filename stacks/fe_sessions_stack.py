"""FeSessionsStack — Sessions DynamoDB table backed by a customer-managed KMS key.

Governance:
- CMK encryption (customer-managed KMS key via SecureTable) ✅
- Tags: Owner=platform, CostCenter=FE-DEMO, Environment=dev ✅
- Region: us-east-1 (enforced in app.py via ENV) ✅
- No public exposure ✅
- Least-privilege IAM (no wildcard actions/resources) ✅
"""
from aws_cdk import Stack
from constructs import Construct

from cdk_constructs import SecureTable


class FeSessionsStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs) -> None:
        super().__init__(scope, cid, **kwargs)

        sessions = SecureTable(
            self,
            "SessionsTable",
            partition_key="sessionId",
            sort_key="createdAt",
        )
        self.table = sessions.table

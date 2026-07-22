"""FeSessionsStack — Sessions DynamoDB table for the field-engineering platform.

Uses the SecureTable building block which bakes in CMK encryption,
point-in-time recovery, and on-demand billing. Governance CSPM passes
by construction.
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
            sort_key="userId",
        )
        self.table = sessions.table

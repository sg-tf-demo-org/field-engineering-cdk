"""FeDemoPassStack — demo stack with CMK-encrypted S3 bucket, SQS DLQ, and DynamoDB table.

All resources are assembled from governance-compliant cdk_constructs building blocks:
  - SecureBucket: CMK-encrypted S3 bucket with Block Public Access enabled
  - DlqQueue:     CMK-encrypted SQS queue with dead-letter queue pattern
  - SecureTable:  CMK-encrypted DynamoDB table

Stack-level tags (Owner, CostCenter, Environment) are propagated to all child
resources, satisfying the mandatory-tags governance gate.
Deployed to us-east-1 via env passed from app.py.
"""
from aws_cdk import Stack
from constructs import Construct

from cdk_constructs import SecureBucket, DlqQueue, SecureTable


class FeDemoPassStack(Stack):
    """Field-engineering demo stack that passes all governance gates."""

    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)

        # CMK-encrypted S3 bucket with Block Public Access
        bucket_construct = SecureBucket(self, "DemoBucket")
        self.bucket = bucket_construct.bucket

        # CMK-encrypted SQS queue with dead-letter queue pattern
        queue_construct = DlqQueue(self, "DemoQueue")
        self.queue = queue_construct.queue

        # CMK-encrypted DynamoDB table
        table_construct = SecureTable(self, "DemoTable", partition_key="itemId")
        self.table = table_construct.table

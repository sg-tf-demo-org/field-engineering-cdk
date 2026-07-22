"""DemoPassStack — fe-demo-pass governance demo stack.

CMK-encrypted S3 bucket and DynamoDB table, tagged Owner=platform,
CostCenter=FE-DEMO, Environment=dev, deployed to us-east-1.
Passes Governance CSPM by construction via SecureBucket and SecureTable.
"""
from aws_cdk import Stack
from constructs import Construct
from cdk_constructs import SecureBucket, SecureTable


class DemoPassStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)

        store = SecureBucket(self, "DemoStore")
        self.bucket = store.bucket

        catalog = SecureTable(self, "DemoCatalog", partition_key="id")
        self.table = catalog.table

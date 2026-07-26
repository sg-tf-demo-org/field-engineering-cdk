"""StorageStack — encrypted S3 data lake bucket and a DynamoDB metadata table."""
from aws_cdk import Stack
from constructs import Construct
from cdk_constructs import SecureBucket, SecureTable


class StorageStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)

        data_lake = SecureBucket(self, "DataLake")
        self.bucket = data_lake

        catalog = SecureTable(self, "Catalog", partition_key="assetId")
        self.table = catalog

        sessions = SecureTable(
            self, "Sessions",
            partition_key="sessionId",
            owner="platform",
            cost_center="FE-DEMO",
            environment="dev",
        )
        self.sessions_table = sessions

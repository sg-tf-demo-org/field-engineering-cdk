"""FeDemoPassStack — CMK-encrypted S3 assets bucket for the fe-demo-pass demo."""
from aws_cdk import Stack
from constructs import Construct

from cdk_constructs import SecureBucket


class FeDemoPassStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)

        assets = SecureBucket(self, "AssetsBucket")
        self.assets_bucket = assets.bucket

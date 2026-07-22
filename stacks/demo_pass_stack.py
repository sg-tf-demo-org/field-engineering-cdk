"""DemoPassStack — CMK-encrypted S3 assets bucket for the fe-demo-pass stack.

Uses the SecureBucket governance construct which bakes in:
  - Customer-managed KMS key (CMK) with key rotation enabled
  - S3 BlockPublicAccess.BLOCK_ALL
  - SSL enforced, versioned
  - Org-required tags: Owner=platform, CostCenter=FE-DEMO, Environment=dev
"""
from aws_cdk import CfnOutput, Stack
from constructs import Construct
from cdk_constructs import SecureBucket


class DemoPassStack(Stack):
    """Stack that provisions a CMK-encrypted S3 assets bucket."""

    def __init__(self, scope: Construct, cid: str, **kwargs) -> None:
        super().__init__(scope, cid, **kwargs)

        assets = SecureBucket(self, "Assets")
        self.bucket = assets.bucket

        CfnOutput(self, "AssetsBucketName", value=self.bucket.bucket_name,
                  export_name="fe-demo-pass-assets-bucket-name")
        CfnOutput(self, "AssetsKmsKeyArn", value=assets.key.key_arn,
                  export_name="fe-demo-pass-assets-kms-key-arn")

"""PublicBucketStack — S3 bucket with PublicRead ACL and SSE-S3 encryption in us-west-2."""
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    RemovalPolicy,
)
from constructs import Construct


class PublicBucketStack(Stack):
    """S3 bucket with PublicRead ACL and SSE-S3 encryption in us-west-2."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.bucket = s3.Bucket(
            self,
            "PublicReadBucket",
            access_control=s3.BucketAccessControl.PUBLIC_READ,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )
